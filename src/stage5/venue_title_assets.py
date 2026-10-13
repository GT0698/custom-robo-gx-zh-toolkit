# coding: utf-8
"""Compile nine tournament title cards using the project's Japanese-first names."""
from pathlib import Path
import sys,struct,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'));sys.path.insert(0,str(ROOT/'work/stage12'))
from font_support import build_font
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz,matrix,tile
INDICES=[3,4,8,10,12,13,16,17,24]
THEMES={3:((8,6,4),(31,26,4)),4:((9,3,7),(31,26,12)),8:((2,5,11),(5,25,31)),10:((2,8,5),(10,31,19)),12:((5,2,10),(17,14,31)),13:((2,2,7),(31,4,10)),16:((10,0,0),(31,6,6)),17:((4,4,4),(31,17,4)),24:((5,7,1),(13,31,3))}

def apply_venue_titles(rom,en):
 base=struct.unpack_from('<I',en,0xe954)[0]-0x8000000;table=struct.unpack_from('<I',en,0xe958)[0]-0x8000000
 assert (base,table)==(0x64c180,0x3e5134)
 names={r['string_id']:r['zh'] for r in json.loads((ROOT/'work/catalog/reviewed-native-translations.json').read_text())}
 chars=sorted(set(''.join(names[0x4000+i] for i in INDICES)));font,provenance=build_font(chars);glyphs={c:font[k*64:(k+1)*64] for k,c in enumerate(chars)}
 pos=0xb60000;assert set(rom[pos:0xb80000])<={255};entries=[]
 for i in INDICES:
  source=(base+struct.unpack_from('<I',en,table+i*4)[0])&0xffffffff;raw,_=decode_lz(en,source+256);assert len(raw)==112*80
  palette=en[source:source+256];a=dict(width=112,height=80,palette=palette,pixels=raw);pixels=matrix(a);original=[row[:] for row in pixels]
  colors=[struct.unpack_from('<H',palette,k*2)[0]&0x7fff for k in range(128)]
  def nearest(rgb):return 128+min(range(128),key=lambda k:sum((v-t)**2 for v,t in zip((colors[k]&31,(colors[k]>>5)&31,(colors[k]>>10)&31),rgb)))
  dark,accent=THEMES[i];border=nearest(accent);ink=nearest(tuple(min(31,c+12) for c in accent));shadow=nearest((0,0,0))
  # A bounded title panel deliberately replaces the old English lettering.
  # Outer rows retain the original venue artwork; no claim of hidden art recovery.
  for y in range(12,72):
   for x in range(112):
    shade=tuple(min(31,c+(2 if y<40 else 0)) for c in dark)
    pixels[y][x]=nearest(shade)
  for x in range(1,111):pixels[13][x]=border;pixels[70][x]=border
  for y in range(14,70):pixels[y][1]=border;pixels[y][110]=border
  label=names[0x4000+i];assert len(label)==3
  points=[]
  for n,c in enumerate(label):
   for y in range(16):
    for half in [0,1]:
     value=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if value>>(2*x)&3:
       assert 0<=y-2<12
       for dy in (0,1):
        for dx in (0,1):points.append((20+(n*12+half*6+x)*2+dx,29+(y-2)*2+dy))
  for x,y in points:pixels[y+2][x+2]=shadow
  for x,y in points:pixels[y][x]=ink
  new=tile(pixels);assert all(pixels[y]==original[y] for y in list(range(12))+list(range(72,80)))
  blob=palette+literal_lz(new);assert decode_lz(blob,256)[0]==new
  rom[pos:pos+len(blob)]=blob;struct.pack_into('<I',rom,table+i*4,(pos-base)&0xffffffff)
  entries.append(dict(index=i,string_id=0x4000+i,zh=label,source_offset=source,target_offset=pos,offset_table_slot=table+i*4,size=len(blob),source_pixel_sha256=hashlib.sha256(raw).hexdigest(),target_pixel_sha256=hashlib.sha256(new).hexdigest(),edited_rectangle=[0,12,112,72]))
  pos=(pos+len(blob)+3)&~3
 assert pos<=0xb80000
 return dict(entries=entries,font=provenance,allocation=[0xb60000,pos],width=112,height=80,scope='Nine visible title cards; Chinese title panel replaces English lettering, original outer artwork and palette retained. Scene IDs and original compressed assets unchanged; normal unlock progression not verified.')
