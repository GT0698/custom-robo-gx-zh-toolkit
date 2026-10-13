from pathlib import Path
import re,struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[2]
BDF=ROOT/'work/upstream/fusion-font/extracted/fusion-pixel-12px-monospaced-zh_hans.bdf'
JP_PATH=(Path(__file__).resolve().parents[2]/'work/roms/custom-robo-gx-jp.gba')
def build_font(chars):
    wanted={ord(c) for c in chars};glyphs={}
    for block in BDF.read_text().split('STARTCHAR ')[1:]:
        code=int(re.search(r'^ENCODING (\d+)',block,re.M)[1])
        if code not in wanted:continue
        w,h,x,y=map(int,re.search(r'^BBX (-?\d+) (-?\d+) (-?\d+) (-?\d+)',block,re.M).groups())
        rows=block.split('BITMAP\n',1)[1].split('ENDCHAR',1)[0].strip().splitlines();pixels=[[0]*12 for _ in range(16)]
        for yy,row in enumerate(rows):
            val=int(row,16);width=len(row)*4
            for xx in range(w):
                px=x+xx;py=12-h-y+yy
                if not(0<=px<12 and 0<=py<16):raise ValueError(f'Glyph clipping U+{code:04X}')
                pixels[py][px]=3 if val & (1<<(width-1-xx)) else 0
        glyphs[chr(code)]=pixels
    missing=set(chars)-set(glyphs);fallback=[]
    if missing:
        fallback_ids={'−':59,'∞':69}
        jp=JP_PATH.read_bytes()
        for c in sorted(missing):
            if c not in '−∞':raise ValueError('Missing glyph '+c)
            n=fallback_ids[c];pixels=[[0]*12 for _ in range(16)]
            for y in range(16):
                row=struct.unpack_from('<H',jp,0x3e7d5e+n*32+y*2)[0]
                for x in range(8):pixels[y][x+2]=(row>>(2*x))&3
            glyphs[c]=pixels;fallback.append(c)
    out=bytearray()
    for c in chars:
        for half in range(2):
            for row in glyphs[c]:out+=struct.pack('<H',sum(row[x+half*6]<<(2*x) for x in range(6)))
    return out,dict(font='Fusion Pixel 12px monospaced zh_hans 2026.09.25',sha256=hashlib.sha256(BDF.read_bytes()).hexdigest(),original_rom_symbol_fallback=fallback)
