"""Chinese header for the confirmed FRESH ROBO venue illustration."""
from pathlib import Path
import sys,json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'work/stage4'),str(ROOT/'work/stage12')]
from font_support import build_font
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz,matrix,tile

def apply_venue_signs(rom,en):
 index=15;base=0x64c180;slot=0x3e5134+index*4;target=0xbe0000
 assert set(rom[target:0xbf0000])<={255}
 source=(base+struct.unpack_from('<I',en,slot)[0])&0xffffffff
 raw,size=decode_lz(en,source+256);assert len(raw)==112*80
 assert rom[source:source+256+size]==en[source:source+256+size]
 palette=en[source:source+256]
 pixels=matrix(dict(width=112,height=80,pixels=raw));before=[row[:] for row in pixels]
 names={r['string_id']:r['zh'] for r in json.loads((ROOT/'work/catalog/reviewed-native-translations.json').read_text())}
 label=names[0x400f];assert label=='新秀机器人杯'
 chars=sorted(set(label));font,provenance=build_font(chars)
 colors=[struct.unpack_from('<H',palette,k*2)[0]&32767 for k in range(128)]
 def nearest(rgb):return 128+min(range(128),key=lambda k:sum((v-t)**2 for v,t in zip((colors[k]&31,colors[k]>>5&31,colors[k]>>10&31),rgb)))
 dark=nearest((12,0,2));red=nearest((25,1,3));gold=nearest((31,25,0));ink=nearest((31,31,22));shadow=nearest((0,0,0))
 # Deliberate replacement of the complete old header rectangle, not inpainting.
 # Artwork below row24 and the existing128-color palette remain exact.
 for y in range(24):
  pixels[y]=[dark if y in (0,23) else red]*112
 for x in range(2,110):pixels[2][x]=gold;pixels[21][x]=gold
 points=[]
 for n,c in enumerate(label):
  g=font[chars.index(c)*64:(chars.index(c)+1)*64]
  for y in range(16):
   for half in range(2):
    value=struct.unpack_from('<H',g,half*32+y*2)[0]
    for x in range(6):
     if value>>(2*x)&3:
      assert 2<=y<14
      points.append((20+n*12+half*6+x,6+y-2))
 for x,y in points:pixels[y+1][x+1]=shadow
 for x,y in points:pixels[y][x]=ink
 assert pixels[24:]==before[24:]
 new=tile(pixels);blob=palette+literal_lz(new)
 assert decode_lz(blob,256)[0]==new
 assert target+len(blob)<0xbf0000
 rom[target:target+len(blob)]=blob
 struct.pack_into('<I',rom,slot,(target-base)&0xffffffff)
 return dict(entries=[dict(index=index,string_id=0x400f,zh=label,source_offset=source,target_offset=target,offset_table_slot=slot,size=len(blob),edited_rectangle=[0,0,112,24],source_pixel_sha256=hashlib.sha256(raw).hexdigest(),target_pixel_sha256=hashlib.sha256(new).hexdigest())],allocation=[target,target+len(blob)],font=provenance,scope='One visible venue sign; redesigned top24rows only, lower scene and palette exact. No gameplay/scene-unlock evidence.')
