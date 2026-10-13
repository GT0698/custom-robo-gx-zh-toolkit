# coding: utf-8
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import build_font

def apply_battle_pause(rom,en):
 assert struct.unpack_from('<I',en,0x371b8)[0]==0x086bb346
 assert struct.unpack_from('<I',en,0x371c0)[0]==0x086bb946
 labels=[(0x6bb346,'返回战斗'),(0x6bb646,'退出对战'),(0x6bb946,'确定退出吗？'),(0x6bbc46,'是'),(0x6bbf46,'否')]
 chars=sorted(set(''.join(t for _,t in labels)));font,provenance=build_font(chars);glyphs={c:font[i*64:(i+1)*64] for i,c in enumerate(chars)};entries=[]
 for offset,label in labels:
  source=en[offset:offset+768];assert bytes(rom[offset:offset+768])==source
  pixels=[]
  for y in range(16):
   row=[]
   for x in range(96):
    p=(y//8)*384+(x//8)*32+(y%8)*4+(x%8)//2;v=source[p]>>((x%2)*4)&15;row.append(5 if v in (1,3,4) else v)
   pixels.append(row)
  ink=[];left=10 if len(label)<=4 else (96-len(label)*12)//2
  for n,c in enumerate(label):
   for y in range(16):
    for half in [0,1]:
     row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
     for x in range(6):
      if row>>(2*x)&3:
       assert 0<=y-2<12;ink.append((left+n*12+half*6+x,y))
  for x,y in ink:pixels[y+1][x+1]=4
  for x,y in ink:pixels[y][x]=1
  out=bytearray(768)
  for y in range(16):
   for x in range(0,96,2):out[(y//8)*384+(x//8)*32+(y%8)*4+(x%8)//2]=pixels[y][x]|pixels[y][x+1]<<4
  rom[offset:offset+768]=out
  entries.append(dict(offset=offset,size=768,zh=label,source_sha256=hashlib.sha256(source).hexdigest(),target_sha256=hashlib.sha256(out).hexdigest()))
 return dict(entries=entries,font=provenance,scope='Existing 96x16 pause/quit-confirmation image rows only. Connection-error and battle HUD pictures unchanged.')
