"""Title-background credit and version; original copyright and input code retained."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'work/stage4'),str(ROOT/'work/stage12')]
from font_support import build_font
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz
LABELS=[('云之君个人汉化',152,147,12),('v1.0',4,147,6)]
START=0xc00000;MAP=0xc0f000;LIMIT=0xc10000

def background(en):
 source=struct.unpack_from('<I',en,0x170dc)[0]-0x08000000
 map_source=struct.unpack_from('<I',en,0x170e0)[0]-0x08000000
 palette=struct.unpack_from('<I',en,0x1707c)[0]-0x08000000
 raw,n=decode_lz(en,source);assert len(raw)==9600
 entries=list(struct.unpack_from('<600H',en,map_source));pixels=[]
 for y in range(160):
  row=[]
  for x in range(240):
   t=entries[y//8*30+x//8];xx=7-x%8 if t&1024 else x%8;yy=7-y%8 if t&2048 else y%8
   row.append(raw[(t&1023)*64+yy*8+xx])
  pixels.append(row)
 return pixels,raw,entries,palette,source,map_source

def apply_title_branding(rom,en):
 old,raw,entries,palette,source,map_source=background(en)
 assert rom[START:LIMIT]==b'\xff'*(LIMIT-START)
 assert rom[0x170dc:0x170e4]==en[0x170dc:0x170e4]
 pixels=[r[:] for r in old];colors=list(struct.unpack_from('<240H',en,palette))
 def nearest(rgb):return min(range(1,240),key=lambda k:sum((v-t)**2 for v,t in zip((colors[k]&31,colors[k]>>5&31,colors[k]>>10&31),rgb)))
 ink=nearest((10,10,10));white=nearest((31,31,31))
 chars=sorted(set(''.join(t for t,x,y,advance in LABELS)));font,provenance=build_font(chars)
 glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)}
 for text,left,top,advance in LABELS:
  for y in range(top,top+12):
   for x in range(left,left+len(text)*advance):
    assert 0<=x<240 and 0<=y<160
    pixels[y][x]=old[y][x]
  for i,c in enumerate(text):
   points=[]
   for y in range(16):
    for half in (0,1):
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(x*2)&3:
       assert 2<=y<14
       points.append((half*6+x,y-2))
   shift=min(x for x,y in points) if advance==6 else 0
   assert advance==12 or max(x for x,y in points)-shift<6
   for x,y in points:pixels[top+y][left+i*advance+x-shift]=ink
 tiles=bytearray(raw);cache={bytes(raw[i:i+64]):i//64 for i in range(0,len(raw),64)};changed=[]
 for ty in range(20):
  for tx in range(30):
   if all(pixels[y][x]==old[y][x] for y in range(ty*8,ty*8+8) for x in range(tx*8,tx*8+8)):continue
   b=bytes(pixels[y][x] for y in range(ty*8,ty*8+8) for x in range(tx*8,tx*8+8))
   if b not in cache:cache[b]=len(tiles)//64;tiles.extend(b)
   entries[ty*30+tx]=cache[b];changed.append(ty*30+tx)
 assert len(tiles)<=0x4000,'BG character block overflow'
 blob=literal_lz(tiles);assert START+len(blob)<=MAP and decode_lz(blob,0)[0]==tiles
 rom[START:START+len(blob)]=blob;rom[MAP:MAP+1200]=struct.pack('<600H',*entries)
 struct.pack_into('<I',rom,0x170dc,0x08000000+START);struct.pack_into('<I',rom,0x170e0,0x08000000+MAP)
 return dict(labels=[dict(text=t,x=x,y=y,width=len(t)*advance,height=12) for t,x,y,advance in LABELS],source=source,map_source=map_source,palette=palette,allocation=[START,START+len(blob)],map_allocation=[MAP,MAP+1200],tile_bytes=len(tiles),changed_map_entries=changed,font=provenance,scope='Only title BG tiles/map and two load pointers. Copyright, palette, animated START prompt, code and saves unchanged; offline evidence only.')
