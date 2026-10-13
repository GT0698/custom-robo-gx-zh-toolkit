"""Translate the Makano map SHOP sign; keep all other background pixels."""
from pathlib import Path
import struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'work/stage12'),str(ROOT/'work/stage4')]
from stage_image_assets import decode_lz
from main_menu_assets import matrix,tile,literal_lz
from font_support import JP_PATH,build_font

def apply_map_graphic(rom,en):
 source=0x32747c;slot=0x7b8530;target=0xbf0000;palette_at=0x32a9c0
 assert struct.unpack_from('<I',en,slot)[0]==0x08000000+source
 jp=JP_PATH.read_bytes();raw,n=decode_lz(en,source);jraw,_=decode_lz(jp,source)
 assert raw==jraw and len(raw)==240*160
 assert rom[source:source+n]==en[source:source+n]
 assert set(rom[target:0xc00000])<={255}
 palette=en[palette_at:palette_at+480];assert palette==jp[palette_at:palette_at+480]
 pixels=matrix(dict(width=240,height=160,pixels=raw));old=[r[:] for r in pixels]
 colors=[struct.unpack_from('<H',palette,i*2)[0]&32767 for i in range(128,240)]
 def nearest(rgb):return 128+min(range(112),key=lambda k:sum((v-t)**2 for v,t in zip((colors[k]&31,colors[k]>>5&31,colors[k]>>10&31),rgb)))
 background=nearest((7,7,7));ink=nearest((31,23,10));shadow=nearest((12,6,3))
 rect=[172,29,198,43]
 for y in range(rect[1],rect[3]):
  for x in range(rect[0],rect[2]):pixels[y][x]=background
 font,provenance=build_font(list('商店'))
 points=[]
 for i,c in enumerate('商店'):
  glyph=font[i*64:(i+1)*64]
  for y in range(16):
   for half in range(2):
    value=struct.unpack_from('<H',glyph,half*32+y*2)[0]
    for x in range(6):
     if value>>(2*x)&3:
      assert 2<=y<14
      points.append((173+i*12+half*6+x,30+y-2))
 for x,y in points:
  assert rect[0]<=x<rect[2]-1 and rect[1]<=y<rect[3]-1
  pixels[y+1][x+1]=shadow
 for x,y in points:pixels[y][x]=ink
 new=tile(pixels)
 for y in range(160):
  for x in range(240):
   if not(rect[0]<=x<rect[2] and rect[1]<=y<rect[3]):assert old[y][x]==pixels[y][x]
 blob=literal_lz(new);assert decode_lz(blob,0)[0]==new and target+len(blob)<=0xc00000
 rom[target:target+len(blob)]=blob;struct.pack_into('<I',rom,slot,0x08000000+target)
 return dict(source_offset=source,target_offset=target,reference_slot=slot,compressed_bytes=len(blob),allocation=[target,target+len(blob)],palette=palette_at,width=240,height=160,edited_rectangle=rect,zh='商店',font=provenance,source_pixel_sha256=hashlib.sha256(raw).hexdigest(),target_pixel_sha256=hashlib.sha256(new).hexdigest(),scope='Only Makano background sign pixels and one LZ source reference. No navigation flags, background geometry or palette changes.')
