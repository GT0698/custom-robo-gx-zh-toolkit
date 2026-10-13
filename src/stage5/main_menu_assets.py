# coding: utf-8
"""Compile main-menu picture text without altering resource names or menu logic."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage12'));sys.path.insert(0,str(ROOT/'work/stage4'))
from stage_image_assets import extract,decode_lz,BASE,OFFSETS
from font_support import build_font
LABELS={12:'对战记录',13:'对战记录',15:'按键设置',16:'按键设置',17:'剧情模式',18:'剧情模式',19:'对战模式',20:'对战模式'}

def literal_lz(raw):
 out=bytearray(b'\x10'+len(raw).to_bytes(3,'little'))
 for i in range(0,len(raw),8):out.append(0);out+=raw[i:i+8]
 return bytes(out)

def matrix(a):
 w=a['width'];raw=a['pixels']
 return [[raw[(y//8)*(w//8)*64+(x//8)*64+(y%8)*8+x%8] for x in range(w)] for y in range(a['height'])]

def tile(m):
 h=len(m);w=len(m[0]);out=bytearray(w*h)
 for y in range(h):
  for x in range(w):out[(y//8)*(w//8)*64+(x//8)*64+(y%8)*8+x%8]=m[y][x]
 return bytes(out)

def apply_main_menu(rom,en):
 chars=sorted(set(''.join(LABELS.values())+'主菜单'));font,provenance=build_font(chars);glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)}
 def draw(m,text,left,top,color,shadow,scale=1):
  dots=[]
  for k,c in enumerate(text):
   for y in range(16):
    for half in [0,1]:
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12
       for sy in range(scale):
        for sx in range(scale):dots.append((left+(k*12+half*6+x)*scale+sx,top+(y-2)*scale+sy))
  for x,y in dots:m[y+1][x+1]=shadow
  for x,y in dots:m[y][x]=color
 entries=[];pos=0xb40000
 assert set(rom[pos:0xb60000])<={255},'Main-menu allocation not empty'
 for i in [12,13,14,15,16,17,18,19,20]:
  a=extract(en,i);m=matrix(a);original=a['pixels']
  if i==14:
   # Restore the repeated card pattern behind the old title from its next row.
   for y in range(3,28):
    for x in range(55,184):m[y][x]=m[y+48][x]
   # Original title colors are picked from its palette; palette itself stays intact.
   pal=[struct.unpack_from('<H',a['palette'],k*2)[0] for k in range(128)]
   def nearest(r,g,b):return 128+min(range(128),key=lambda k:((pal[k]&31)-r)**2+(((pal[k]>>5)&31)-g)**2+(((pal[k]>>10)&31)-b)**2)
   draw(m,'主菜单',84,3,nearest(31,24,3),nearest(0,0,0),2)
   label='主菜单'
  else:
   selected=i in [13,16,18,20]
   # Keep the original rounded ends. Rebuild only the straight middle where
   # old letter pixels cover the bar; selected art retains its red gradient.
   for y in range(16):
    for x in range(10,118):
     m[y][x]=(192+(-x)%16 if selected else 179) if 2<=y<=13 else (175 if y==14 else 128)
   label=LABELS[i];draw(m,label,(128-len(label)*12)//2,2,181 if selected else 176,175)
  raw=tile(m);lz=literal_lz(raw);blob=a['palette']+lz
  assert decode_lz(blob,256)[0]==raw
  rom[pos:pos+len(blob)]=blob
  pointer_slot=OFFSETS+i*4
  struct.pack_into('<I',rom,pointer_slot,(pos-BASE)&0xffffffff)
  entries.append(dict(index=i,zh=label,width=a['width'],height=a['height'],source_offset=a['offset'],target_offset=pos,size=len(blob),offset_table_slot=pointer_slot,original_offset_value=struct.unpack_from('<I',en,pointer_slot)[0],source_pixel_sha256=hashlib.sha256(original).hexdigest(),target_pixel_sha256=hashlib.sha256(raw).hexdigest()))
  pos=(pos+len(blob)+3)&~3
 assert pos<=0xb60000
 return dict(entries=entries,font=provenance,allocation=[0xb40000,pos],scope='Nine named menu pictures only: title background and four buttons in two states. Existing dimensions, palettes, resource IDs and menu logic unchanged; no link functionality tested.')
