"""12-frame title START prompt, four 32x16 4bpp OBJ chunks per frame."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'work/stage4'),str(ROOT/'work/stage12')]
from font_support import build_font,JP_PATH
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz
from battle_result_assets import encode,decode

LABEL='按START键'
TABLE=0x32506C
PALETTE=0x38C3EC

def apply_title_prompt(rom,en):
 jp=JP_PATH.read_bytes()
 assert struct.unpack_from('<I',en,0x1726C)[0]==0x08000000+TABLE
 assert struct.unpack_from('<I',en,0x17084)[0]==0x08000000+PALETTE
 # Loader: 48 chunks, 32px spacing, (56,112) origin; frame selector: 12 groups.
 for a,b in [(0x1705C,0x17088),(0x171D8,0x172B4),(0x172B4,0x17370)]:
  assert jp[a:b]==en[a:b]==rom[a:b],('title loader changed',hex(a))
 pos=0xBC0000;limit=0xBD0000
 assert rom[pos:limit]==b'\xff'*(limit-pos),'title prompt allocation collision'
 chars=sorted(set(LABEL));font,provenance=build_font(chars)
 glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)};points=set()
 left=(128-12*len(LABEL))//2
 for n,c in enumerate(LABEL):
  for half in (0,1):
   for y in range(16):
    row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
    for x in range(6):
     if row>>(2*x)&3:
      assert 1<=y<15
      points.add((left+n*12+half*6+x,y))
 records=[];frames=[]
 for frame in range(12):
  pixels=[[0]*128 for _ in range(16)]
  center=left+frame*8
  for x,y in points:
   assert x+1<128 and y+1<16
   pixels[y+1][x+1]=2 if abs(x-center)<7 else 8
  # Preserve frame cadence and complete strokes; replace the English letter
  # deformation with a short red highlight sweep across the Chinese prompt.
  for x,y in points:pixels[y][x]=1
  frames.append(hashlib.sha256(bytes(sum(pixels,[]))).hexdigest())
  for piece in range(4):
   slot=TABLE+(frame*4+piece)*4
   source=struct.unpack_from('<I',en,slot)[0]-0x08000000
   assert jp[slot:slot+4]==en[slot:slot+4]==rom[slot:slot+4]
   old,n=decode_lz(en,source);assert len(old)==256
   assert jp[source:source+n]==en[source:source+n]
   raw=encode([row[piece*32:(piece+1)*32] for row in pixels])
   assert len(raw)==256 and encode(decode(raw,32,16))==raw
   blob=literal_lz(raw);assert decode_lz(blob,0)[0]==raw and pos+len(blob)<=limit
   rom[pos:pos+len(blob)]=blob;struct.pack_into('<I',rom,slot,0x08000000+pos)
   records.append(dict(frame=frame,piece=piece,source=source,pointer_slot=slot,target=pos,
                       size=len(blob),source_sha256=hashlib.sha256(old).hexdigest(),target_sha256=hashlib.sha256(raw).hexdigest()))
   pos=(pos+len(blob)+3)&~3
 assert len(set(frames))==12
 return dict(zh=LABEL,entries=records,font=provenance,frame_hashes=frames,palette=PALETTE,
             allocation=[0xBC0000,pos],scope='Only 48 picture pointers plus new 4bpp chunks; loader, START input, palette, position and 12-frame cadence unchanged. Artwork uses a new highlight sweep; not a gameplay check.')
