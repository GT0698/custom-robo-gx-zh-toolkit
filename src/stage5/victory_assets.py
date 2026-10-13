"""Localize the two four-sprite victory captions; preserve scene/OAM behavior."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'work/stage4'),str(ROOT/'work/stage12')]
from font_support import build_font,JP_PATH
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz
from battle_result_assets import encode,decode

GROUPS=[
 dict(zh='对战胜利',en='YOU WIN!',table=0x7BB130,reference=0x1C0B4,first_sprite=16,
      palette=0x33D9FC,sources=[0x33D594,0x33DA24,0x33DD94,0x33E0CC]),
 dict(zh='完美胜利',en='PERFECT',table=0x7BB160,reference=0x1C0B8,first_sprite=20,
      palette=0x33C868,sources=[0x33C408,0x33C890,0x33CDBC,0x33D280]),
]

def apply_victory(rom,en):
 jp=JP_PATH.read_bytes();pos=0xBB0000;limit=0xBC0000
 assert rom[pos:limit]==b'\xff'*(limit-pos),'victory allocation collision'
 chars=sorted(set(''.join(g['zh'] for g in GROUPS)));font,provenance=build_font(chars)
 glyphs={c:font[n*64:(n+1)*64] for n,c in enumerate(chars)};entries=[]
 for g in GROUPS:
  assert struct.unpack_from('<I',en,g['reference'])[0]==0x08000000+g['table']
  palette,_=decode_lz(en,g['palette']);assert len(palette)==32
  # Original palettes run light highlights -> saturated gold -> dark shading.
  image=[[0]*256 for _ in range(64)];points=set()
  for n,c in enumerate(g['zh']):
   for half in (0,1):
    for y in range(16):
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12
       for dy in range(4):
        for dx in range(4):points.add((24+(n*12+half*6+x)*4+dx,5+(y-2)*4+dy))
  def paint(x,y,v):
   assert 0<=x<240 and 0<=y<64
   image[y][x]=v
  for x,y in points:paint(x+4,y+5,12)
  for x,y in points:
   for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:paint(x+dx,y+dy,1)
  for x,y in points:paint(x,y,3+min(5,(y-5)//8))
  for i,source in enumerate(g['sources']):
   record=g['table']+i*12;slot=record+8
   sprite,pal,pointer=struct.unpack_from('<III',en,record)
   assert sprite==g['first_sprite']+i
   assert pal==(0x08000000+g['palette'] if not i else 0)
   assert pointer==0x08000000+source
   assert rom[record:record+12]==jp[record:record+12]==en[record:record+12]
   original,n=decode_lz(en,source);assert len(original)==2048
   assert jp[source:source+n]==en[source:source+n]
   raw=encode([row[i*64:(i+1)*64] for row in image])
   assert len(raw)==2048 and encode(decode(raw,64,64))==raw
   blob=literal_lz(raw);assert decode_lz(blob,0)[0]==raw
   assert pos+len(blob)<=limit
   rom[pos:pos+len(blob)]=blob;struct.pack_into('<I',rom,slot,0x08000000+pos)
   entries.append(dict(zh=g['zh'],en=g['en'],piece=i,source=source,pointer_slot=slot,
                       sprite=sprite,palette_source=g['palette'],target=pos,size=len(blob),raw_size=2048,
                       source_raw_sha256=hashlib.sha256(original).hexdigest(),target_raw_sha256=hashlib.sha256(raw).hexdigest()))
   pos=(pos+len(blob)+3)&~3
 return dict(entries=entries,font=provenance,allocation=[0xBB0000,pos],
             scope='4bpp 64x64 sprite chunks, palette/OAM identifiers and 64px spacing retained; only 8 image pointers and new image data. Static preview, no runtime animation claim.')
