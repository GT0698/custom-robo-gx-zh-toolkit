# coding: utf-8
"""Compile Rank, first-place numeral and Japanese-aligned result captions."""
from pathlib import Path
import sys,struct,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'));sys.path.insert(0,str(ROOT/'work/stage12'))
from font_support import build_font
from stage_image_assets import decode_lz
from main_menu_assets import literal_lz,matrix,tile

def apply_league_graphics(rom,en):
 chars=list('名次1冠亚军晋级决赛');font,provenance=build_font(chars)
 glyphs={}
 for n,c in enumerate(chars):
  glyphs[c]=[(h*6+x,y) for h in (0,1) for y in range(16) for x in range(6) if struct.unpack_from('<H',font,n*64+h*32+y*2)[0]>>(2*x)&3]
 raw,_=decode_lz(en,0x35d940);assert len(raw)==38400
 assert struct.unpack_from('<I',en,0x7b8b28)[0]==0x0835d940
 bg=matrix(dict(width=240,height=160,pixels=raw));original=[r[:] for r in bg]
 for y in range(29,51):
  for x in range(197,219):bg[y][x]=204
 for n,c in enumerate('名次'):
  pts=glyphs[c];top=min(y for x,y in pts);assert max(y for x,y in pts)-top==10
  for x,y in pts:bg[29+n*11+y-top][202+x]=203
 compiled=tile(bg);assert all(original[y][x]==bg[y][x] for y in range(160) for x in range(240) if not(197<=x<219 and 29<=y<51))
 assert set(rom[0xb80000:0xbb0000])<={255}
 blob=literal_lz(compiled);assert len(blob)<0x10000 and decode_lz(blob,0)[0]==compiled
 rom[0xb80000:0xb80000+len(blob)]=blob;struct.pack_into('<I',rom,0x7b8b28,0x08b80000)
 records=json.loads((ROOT/'work/catalog/league-object-inventory.json').read_text());records={r['index']:r for r in records}
 pos=0xb90000;entries=[]
 def place(raw,record,label):
  nonlocal pos
  p=record['source'];slot=record['pointer_slot'];assert struct.unpack_from('<I',en,slot)[0]==0x08000000+p
  before,_=decode_lz(en,p);assert len(before)==len(raw)
  blob=literal_lz(raw);assert decode_lz(blob,0)[0]==raw
  rom[pos:pos+len(blob)]=blob;struct.pack_into('<I',rom,slot,0x08000000+pos)
  entries.append(dict(index=record['index'],zh=label,source=p,pointer_slot=slot,target=pos,size=len(blob),raw_size=len(raw),source_raw_sha256=hashlib.sha256(before).hexdigest(),target_raw_sha256=hashlib.sha256(raw).hexdigest()))
  pos=(pos+len(blob)+3)&~3
 def letter_points(text,scale,w,h):
  pts=[];width=len(text)*12*scale;left=(w-width)//2;top=(h-12*scale)//2
  for n,c in enumerate(text):
   for x,y in glyphs[c]:
    assert 0<=y-2<12
    for dy in range(scale):
     for dx in range(scale):pts.append((left+(n*12+x)*scale+dx,top+(y-2)*scale+dy))
  return pts,top
 def paint(w,h,pts,top,kind):
  out=[[0]*w for _ in range(h)]
  for x,y in pts:out[y+3][x+3]=20
  if kind!='red':
   for x,y in pts:
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:out[y+dy][x+dx]=17
  for x,y in pts:
   color=23 if kind=='red' else (64 if kind=='gold' else 72)+(max(0,y-top)//3)%8
   out[y][x]=color
  return out
 groups=[('冠军',[18,19,20],4,'gold','優勝'),('亚军',[15,16,17],4,'silver','準優勝'),('晋级决赛',[21,22,23],3,'red','決勝進出')]
 for label,ids,scale,kind,ja in groups:
  pts,top=letter_points(label,scale,192,64);canvas=paint(192,64,pts,top,kind)
  for part,i in enumerate(ids):place(tile([r[part*64:(part+1)*64] for r in canvas]),records[i],label)
 # The other ranks already use Arabic numerals. Remove the English ordinal suffix
 # by compiling a centered gold1, keeping the original32x32 sprite dimensions.
 pts=glyphs['1'];minx=min(x for x,y in pts);miny=min(y for x,y in pts);maxx=max(x for x,y in pts);maxy=max(y for x,y in pts);w=(maxx-minx+1)*2;h=(maxy-miny+1)*2;left=(32-w)//2;top=(32-h)//2
 dots=[(left+(x-minx)*2+dx,top+(y-miny)*2+dy) for x,y in pts for dy in range(2) for dx in range(2)]
 out=[[0]*32 for _ in range(32)]
 for x,y in dots:out[y+2][x+2]=20
 for x,y in dots:
  for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:out[y+dy][x+dx]=17
 for x,y in dots:out[y][x]=min(31,25+(y-top)//4)
 place(tile(out),records[10],'1')
 assert pos<=0xbb0000
 return dict(font=provenance,background=dict(source=0x35d940,target=0xb80000,size=len(blob),pointer_slot=0x7b8b28,edited_rectangle=[197,29,219,51],target_raw_sha256=hashlib.sha256(compiled).hexdigest()),sprites=entries,sprite_allocation=[0xb90000,pos],scope='Rank header 名次, first-place numeral1, and three Japanese-aligned captions: 優勝→冠军,準優勝→亚军,決勝進出→晋级决赛. Existing dimensions, timing, palettes and score logic retained.')
