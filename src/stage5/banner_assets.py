# coding: utf-8
"""Compile Chinese font glyphs into the existing equipment type-banner tile format."""
from pathlib import Path
import sys,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/stage4'))
from font_support import build_font
TYPE_LABELS=['闪耀战士型','空中丽人型','金属格斗型','突击隐形型','闪电飞行型','迷雾幻影型','违禁','特殊','枪手装置','辅助舱']
TYPE_OFFSET=0x3eaac0

def apply_type_banners(rom,en):
    assert struct.unpack_from('<I',en,0x8b48)[0]==0x08000000+TYPE_OFFSET
    assert en[0x8b0a:0x8b10].hex()=='d3009b181b02', 'Type banner stride code changed'
    chars=sorted(set(''.join(TYPE_LABELS)));raw,font=build_font(chars)
    glyphs={c:raw[i*64:(i+1)*64] for i,c in enumerate(chars)}
    details=[]
    def addr(x,y):return (y//8)*12*64+(x//8)*64+(y%8)*8+x%8
    for i,label in enumerate(TYPE_LABELS):
        start=TYPE_OFFSET+i*2304;source=en[start:start+2304]
        assert bytes(rom[start:start+2304])==source, 'Unexpected type-banner overlap'
        output=bytearray(source);background=195 if i<6 else [199,202,205,208][i-6]
        # Yellow glyphs and their black shadow are text-only palette entries.
        # Bevels, skulls and stars use other entries and remain unchanged.
        for y in range(2,22):
            for x in range(2,94):
                k=addr(x,y)
                if output[k] in (223,197):output[k]=background
        ink=[];left=(96-len(label)*12)//2
        for n,c in enumerate(label):
            for y in range(16):
                for half in (0,1):
                    row=struct.unpack_from('<H',glyphs[c],half*32+y*2)[0]
                    for x in range(6):
                        if (row>>(2*x))&3:ink.append((left+n*12+half*6+x,4+y))
        for x,y in ink:
            assert 1<=x<94 and 1<=y<22
            output[addr(x+1,y+1)]=197
        for x,y in ink:output[addr(x,y)]=223
        rom[start:start+2304]=output
        details.append(dict(index=i,zh=label,offset=start,size=2304,source_sha256=hashlib.sha256(source).hexdigest(),target_sha256=hashlib.sha256(output).hexdigest()))
    return dict(kind='equipment-type-banners',width=96,height=24,format='8bpp 8x8 tiles;12 columns;3 rows',reference_slot=0x8b48,font=font,entries=details,scope='Existing artwork format and palette retained; compile only type-title glyph pixels. Main menu and small equipment category labels not included.')
