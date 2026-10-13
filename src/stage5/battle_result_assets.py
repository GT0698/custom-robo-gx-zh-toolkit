"""Two uncompressed 4bpp single-player result captions; keep loading/layout code."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import build_font,JP_PATH

ASSETS=[
 dict(source=0x6C09E6,width=160,height=64,palette=0x6C9140,reference=0x1E120,
      palette_reference=0x1E118,en='DRAW',zh='平局',ink=6,outline=1,shadow=13),
 dict(source=0x6C4FE6,width=240,height=64,palette=0x6C91A8,reference=0x1E500,
      palette_reference=0x1E4F8,en='YOU LOSE',zh='对战失败',ink=4,outline=1,shadow=12),
]

def decode(raw,w,h):
 return [[(raw[(y//8)*(w//8)*32+(x//8)*32+(y%8)*4+(x%8)//2]>>((x%2)*4))&15 for x in range(w)] for y in range(h)]

def encode(pixels):
 h=len(pixels);w=len(pixels[0]);raw=bytearray(w*h//2)
 for y in range(h):
  for x in range(0,w,2):raw[(y//8)*(w//8)*32+(x//8)*32+(y%8)*4+(x%8)//2]=pixels[y][x]|pixels[y][x+1]<<4
 return bytes(raw)

def apply_battle_results(rom,en):
 jp=JP_PATH.read_bytes();chars=sorted(set(''.join(r['zh'] for r in ASSETS)))
 font,provenance=build_font(chars);glyphs={c:font[n*64:(n+1)*64] for n,c in enumerate(chars)}
 entries=[]
 for a in ASSETS:
  p,w,h=a['source'],a['width'],a['height'];size=w*h//2
  assert struct.unpack_from('<I',en,a['reference'])[0]==0x08000000+p
  assert struct.unpack_from('<I',en,a['palette_reference'])[0]==0x08000000+a['palette']
  original=en[p:p+size]
  assert rom[p:p+size]==jp[p:p+size]==original
  assert encode(decode(original,w,h))==original
  scale=4;left=(w-len(a['zh'])*12*scale)//2;top=5;points=set()
  for n,c in enumerate(a['zh']):
   glyph=glyphs[c]
   for half in (0,1):
    for y in range(16):
     row=struct.unpack_from('<H',glyph,half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12
       for dy in range(scale):
        for dx in range(scale):points.add((left+(n*12+half*6+x)*scale+dx,top+(y-2)*scale+dy))
  pixels=[[0]*w for _ in range(h)]
  def paint(x,y,v):
   assert 0<=x<w and 0<=y<h
   pixels[y][x]=v
  for x,y in points:paint(x+4,y+5,a['shadow'])
  for x,y in points:
   for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:paint(x+dx,y+dy,a['outline'])
  for x,y in points:paint(x,y,a['ink'])
  raw=encode(pixels);assert decode(raw,w,h)==pixels and len(raw)==size
  rom[p:p+size]=raw
  entries.append(a|dict(size=size,source_sha256=hashlib.sha256(original).hexdigest(),
                    target_sha256=hashlib.sha256(raw).hexdigest(),jp_equals_en=True,
                    ink_bounds=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]))
 return dict(entries=entries,font=provenance,scope='DRAW and YOU LOSE picture bytes only. Same source/dimensions/palette/loaders. Static layout, no normal-game display claim; YOU WIN and HUD are separate resources.')
