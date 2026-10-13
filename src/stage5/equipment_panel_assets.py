# coding: utf-8
"""Compile six left-panel equipment labels with 12px Chinese glyphs."""
from pathlib import Path
import struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import build_font

def apply_equipment_panel(rom,en):
 assert struct.unpack_from('<I',en,0x8e30)[0]==0x083d8af4
 assert struct.unpack_from('<I',en,0x8e34)[0]==0x083d8554
 assert set(rom[0xb30000:0xb32400])<={255}
 m=[]
 for y in range(144):
  row=[]
  for x in range(120):
   t=en[0x3d8af4+(y//8)*15+x//8];v=en[0x3d8554+t*32+(y%8)*4+(x%8)//2]>>((x%2)*4)&15;row.append(v)
  m.append(row)
 original=[r[:] for r in m]
 labels=[('指挥官',3,0),('机体',5,12),('枪械',5,36),('炸弹',5,60),('辅助',5,84),('芯片',5,108)]
 chars=sorted(set(''.join(t for t,_,_ in labels)));font,provenance=build_font(chars);glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)}
 for y in range(0,14):
  for x in range(2,51):
   m[y][x]=9
 for _,_,top in labels[1:]:
  for y in range(top,top+12):
   for x in range(2,35+(y-top)//2):m[y][x]=9
 for text,left,top in labels:
  for n,c in enumerate(text):
   for y in range(16):
    for half in [0,1]:
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12
       m[top+y-2][left+n*12+half*6+x]=1
 tiles=[];mapping=bytearray();index={}
 for ty in range(18):
  for tx in range(15):
   tile=bytes(m[ty*8+y][tx*8+x]|m[ty*8+y][tx*8+x+1]<<4 for y in range(8) for x in range(0,8,2))
   if tile not in index:index[tile]=len(tiles);tiles.append(tile)
   mapping.append(index[tile])
 assert len(tiles)<=256
 payload=b''.join(tiles);assert len(payload)<=0x2000
 rom[0xb30000:0xb30000+len(payload)]=payload;rom[0xb32000:0xb32000+len(mapping)]=mapping
 struct.pack_into('<I',rom,0x8e30,0x08b32000);struct.pack_into('<I',rom,0x8e34,0x08b30000)
 # Confirm the frame and all dynamic name fields remain outside edited pixels.
 changed=[(x,y) for y in range(144) for x in range(120) if original[y][x]!=m[y][x]]
 assert all((2<=x<51 and 0<=y<14) or any(2<=x<40 and top<=y<top+12 for _,_,top in labels[1:]) for x,y in changed)
 return dict(labels=[t for t,_,_ in labels],width=120,height=144,format='deduplicated4bpp tiles and byte tilemap',font=provenance,tiles=len(tiles),tile_pool_offset=0xb30000,tile_map_offset=0xb32000,tile_pool_sha256=hashlib.sha256(payload).hexdigest(),tile_map_sha256=hashlib.sha256(mapping).hexdigest(),reference_slots=[0x8e30,0x8e34],changed_pixels=len(changed),scope='Left equipment panel only; label tabs extended into existing gap for12px type. Model-side tiny labels remain separate.')
