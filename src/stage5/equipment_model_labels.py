# coding: utf-8
from pathlib import Path
import struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import build_font

def apply_model_labels(rom,en):
 assert struct.unpack_from('<I',en,0x7220)[0]==0x083db0dc
 assert struct.unpack_from('<I',en,0x7224)[0]==0x083dab7c
 assert set(rom[0xb34000:0xb36400])<={255}
 m=[]
 for y in range(144):
  row=[]
  for x in range(120):
   t=en[0x3db0dc+y//8*15+x//8];v=en[0x3dab7c+t*32+y%8*4+x%8//2]>>((x%2)*4)&15;row.append(v)
  m.append(row)
 original=[r[:] for r in m]
 for left,col in [(1,3),(73,4)]:
  for y in list(range(0,14))+list(range(51,65)):
   for x in range(left,left+46):m[y][x]=0
  for x in range(left,left+46):m[13][x]=col;m[51][x]=col
  for y in range(13,52):m[y][left]=col;m[y][left+45]=col
 labels=[('辅助',1,0,3),('芯片',73,0,4),('枪械',1,52,1),('炸弹',73,52,2)]
 chars=sorted(set(''.join(t for t,*_ in labels)));font,provenance=build_font(chars);glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)}
 for text,left,top,col in labels:
  for n,c in enumerate(text):
   for y in range(16):
    for half in [0,1]:
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12;m[top+y-2][left+n*12+half*6+x]=col
 pool=[];indices={};mapping=bytearray()
 for ty in range(18):
  for tx in range(15):
   tile=bytes(m[ty*8+y][tx*8+x]|m[ty*8+y][tx*8+x+1]<<4 for y in range(8) for x in range(0,8,2))
   if tile not in indices:indices[tile]=len(pool);pool.append(tile)
   mapping.append(indices[tile])
 assert len(pool)<=256;data=b''.join(pool);assert len(data)<=0x2000
 rom[0xb34000:0xb34000+len(data)]=data;rom[0xb36000:0xb36000+270]=mapping
 struct.pack_into('<I',rom,0x7220,0x08b36000);struct.pack_into('<I',rom,0x7224,0x08b34000)
 changes=[(x,y) for y in range(144) for x in range(120) if m[y][x]!=original[y][x]]
 assert all((0<=y<14 or 51<=y<65) and (1<=x<47 or 73<=x<119) for x,y in changes)
 return dict(labels=[t for t,*_ in labels],font=provenance,tiles=len(pool),tile_pool_offset=0xb34000,tile_map_offset=0xb36000,tile_pool_sha256=hashlib.sha256(data).hexdigest(),tile_map_sha256=hashlib.sha256(mapping).hexdigest(),changed_pixels=len(changes),reference_slots=[0x7220,0x7224],scope='Four model-side labels; upper outline moved from y9..54 to y13..51 to fit12px labels. Palette color IDs, part/model sprites and lower boxes unchanged.')
