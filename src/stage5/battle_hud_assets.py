"""YOU/ENEMY label area only; keep HP-bar pixels and the swapped palettes."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import JP_PATH
from battle_result_assets import decode,encode

# Source game's compact 8x8 glyphs for 我/方; project-authored 7x7 simplified 敌.
# Each row is MSB-left in an 8px container, with a blank last baseline row.
ENEMY_GLYPH=bytes.fromhex('3227752372557500')
GLYPH_SOURCES={'我':0x696854,'方':0x69C15A}
ASSETS=[(0x6BC246,0x355D4,0x6C8E66,0x355CC),(0x6BC546,0x3563C,0x6C8E82,0x35634)]

def apply_battle_hud(rom,en):
 jp=JP_PATH.read_bytes();glyphs={'敌':ENEMY_GLYPH};entries=[]
 for c,p in GLYPH_SOURCES.items():
  assert jp[p-2:p]==c.encode('shift_jisx0213')
  assert jp[p:p+8]==en[p:p+8]
  glyphs[c]=jp[p:p+8]
 # Both copies are the same graphic; the original loaders swap palette colors.
 assert en[ASSETS[0][0]:ASSETS[0][0]+768]==en[ASSETS[1][0]:ASSETS[1][0]+768]
 for p,slot,palette,palette_slot in ASSETS:
  assert struct.unpack_from('<I',en,slot)[0]==0x08000000+p
  assert struct.unpack_from('<I',en,palette_slot)[0]==0x08000000+palette
  old=en[p:p+768];assert rom[p:p+768]==jp[p:p+768]==old
  pixels=decode(old,96,16);before=[row[:] for row in pixels]
  for y in range(16):pixels[y][:32]=[0]*32
  for label,top,color in [('我方',0,4),('敌方',8,3)]:
   ink=set()
   for n,c in enumerate(label):
    for y,row in enumerate(glyphs[c]):
     for x in range(8):
      if row>>(7-x)&1:
       assert y<7
       ink.add((6+n*9+x,top+y))
   for x,y in ink:pixels[y+1][x+1]=2
   for x,y in ink:pixels[y][x]=color
  assert all(pixels[y][32:]==before[y][32:] for y in range(16))
  raw=encode(pixels);assert len(raw)==768 and decode(raw,96,16)==pixels
  rom[p:p+768]=raw
  entries.append(dict(source=p,size=768,reference=slot,palette=palette,palette_reference=palette_slot,
                      width=96,height=16,changed_rect=[0,0,32,16],labels=['我方','敌方'],
                      source_sha256=hashlib.sha256(old).hexdigest(),target_sha256=hashlib.sha256(raw).hexdigest()))
 return dict(entries=entries,glyph_sources=GLYPH_SOURCES,simplified_enemy_bitmap=ENEMY_GLYPH.hex(),
             scope='Only first32 columns of two96x16 HUD sheets. All HP-bar pixels, palette colors, loaders, numeric/health logic and original glyph data unchanged; static evidence only.')
