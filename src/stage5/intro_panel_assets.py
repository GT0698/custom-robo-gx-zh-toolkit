"""READY / BATTLE BG panels: keep size, palette and original draw/transition code."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'work/stage4'),str(ROOT/'work/stage12')]
from font_support import build_font,JP_PATH
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz,tile

def apply_intro_panels(rom,en):
 jp=JP_PATH.read_bytes();table=0x3E7CDC
 assert struct.unpack_from('<I',en,0xED38)[0]==0x08000000+table
 chars=sorted(set('准备开战'));font,provenance=build_font(chars)
 glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)}
 pos=0xBD0000;limit=0xBE0000;assert rom[pos:limit]==b'\xff'*(limit-pos)
 entries=[]
 for index,text,scale,expected_size in [(0,'准备',3,(128,48)),(1,'开战',4,(200,64))]:
  record=table+12*index;assert rom[record:record+12]==jp[record:record+12]==en[record:record+12]
  tw,th,pbase,_=en[record:record+4];w,h=tw*8,th*8;assert (w,h)==expected_size and pbase==48
  pal,src=struct.unpack_from('<II',en,record+4);pal-=0x08000000;src-=0x08000000
  original,n=decode_lz(en,src);assert len(original)==w*h and jp[src:src+n]==en[src:src+n]
  assert jp[pal:pal+64]==en[pal:pal+64]
  left=(w-len(text)*12*scale)//2;top=4 if index==0 else 5;points=set()
  for k,c in enumerate(text):
   for half in (0,1):
    for y in range(16):
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12
       for dy in range(scale):
        for dx in range(scale):points.add((left+(k*12+half*6+x)*scale+dx,top+(y-2)*scale+dy))
  pixels=[[0]*w for _ in range(h)]
  def paint(x,y,v):
   assert 0<=x<w and 0<=y<h
   pixels[y][x]=v
  for x,y in points:paint(x+3,y+3,63)
  for x,y in points:
   for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:paint(x+dx,y+dy,49)
  for x,y in points:paint(x,y,50+min(10,(y-top)*10//(12*scale)))
  raw=tile(pixels);blob=literal_lz(raw);assert decode_lz(blob,0)[0]==raw
  assert pos+len(blob)<=limit
  rom[pos:pos+len(blob)]=blob;slot=record+8;struct.pack_into('<I',rom,slot,0x08000000+pos)
  entries.append(dict(index=index,zh=text,en=['READY','BATTLE'][index],width=w,height=h,
                      record=record,pointer_slot=slot,palette=pal,palette_base=pbase,source=src,target=pos,size=len(blob),
                      source_sha256=hashlib.sha256(original).hexdigest(),target_sha256=hashlib.sha256(raw).hexdigest()))
  pos=(pos+len(blob)+3)&~3
 # Leave the third panel/icon and all descriptor fields other than two pointers alone.
 assert rom[table+24:table+36]==en[table+24:table+36]
 return dict(entries=entries,font=provenance,allocation=[0xBD0000,pos],
             scope='Only READY/BATTLE image pointers and new8bpp data. Dimensions, palettes, icon, timings, drawing and battle logic unchanged. Offline evidence only.')
