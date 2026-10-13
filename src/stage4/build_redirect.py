"""Full original-script layout + exact message-address redirection. Development build."""
from pathlib import Path
import json,re,struct,sys,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/stage2'));sys.path.insert(0,str(ROOT/'work/tools'));sys.path.insert(0,str(ROOT/'work/stage3'))
from build_opening import tokens,branch,encode,CONTROL
from arm_object import text_section
from font_support import build_font,JP_PATH
from build_chapter1 import UI as BEDROOM_UI
from bps import digest,create,apply
JP_START=0x4b5fa0;JP_END=0x5371d8
TEXT_BASE=0x940000;TEXT_END=0xb00000
UI={**BEDROOM_UI,8:'这是什么？',9:'嗯'}
NATIVE_CODES=[(lead<<8)|trail for lead in range(0xe8,0xff) for trail in range(1,256)]

def encode_extended(text,ids):
    # Original numeric controls >= 0x10 are spacing/special-glyph controls.
    if ''.join(tokens(text))!=text:raise ValueError('Malformed control syntax')
    out=bytearray()
    for t in tokens(text):
        if re.fullmatch(r'\{[0-9A-F]{2}\}',t):
            v=int(t[1:-1],16)
            if v!=9 and not 0x10<=v<=0x23:raise ValueError('Unknown numeric control '+t)
            out+=bytes([1,v])
        else:out+=encode(t,ids)
    return bytes(out)

def build(extra_chars=''):
    en=(ROOT/'work/roms/custom-robo-gx-en-v1.0.1.gba').read_bytes();jp=JP_PATH.read_bytes()
    assert hashlib.sha1(en).hexdigest()=='e033251c780dbbd83b15623159b743d2e624d8a0'
    assert hashlib.sha1(jp).hexdigest()=='0b5ce051aa1fd83ab0ec79122b07b02bb41096a5'
    rows=json.loads((ROOT/'work/text/japanese-messages.json').read_text())
    translations=json.loads((ROOT/'work/catalog/reviewed-translations.json').read_text());by_ja={r['ja']:r['zh'] for r in translations}
    texts=[by_ja.get(r['ja'],r['ja']) for r in rows]
    chars=sorted(set(''.join(''.join(t for t in tokens(s) if not t.startswith('{') and not t.isascii()) for s in texts)+''.join(UI.values())+extra_chars))
    ids={c:i for i,c in enumerate(chars)}
    (ROOT/'work/stage4/character-map.json').write_text(json.dumps(ids,ensure_ascii=False,indent=2))
    if len(chars)>len(NATIVE_CODES)//2:raise ValueError('Native character capacity exceeded')
    font,provenance=build_font(chars)
    font=en[0x3e7d5e:0x3f543e]+font
    rom=bytearray(en)+bytearray(b'\xff'*(0x1000000-len(en)))
    # Original control-flow bytecode and inline data retain every original address.
    rom[JP_START:JP_END]=jp[JP_START:JP_END]
    rom[0x800000:0x800000+len(font)]=font
    struct.pack_into('<I',rom,0x4c80,0x08800000)
    table=en[0x3f543e:0x3f61aa]+b''.join(struct.pack('<H',v) for v in NATIVE_CODES[:len(chars)*2])
    rom[0x880000:0x880000+len(table)]=table;struct.pack_into('<I',rom,0x4c84,0x08880000)
    struct.pack_into('<H',rom,0x88f000,1718+len(chars)*2);struct.pack_into('<I',rom,0x4c90,0x0888f000)
    pos=TEXT_BASE;redirect=bytearray(struct.pack('<I',len(rows)));locations=[]
    for row,text in zip(rows,texts):
        # DrawDialogString is called with a pointer AFTER opcode 0x99.
        src=row['offset']+1;end=row['offset']+row['byte_length']
        body=encode_extended(text,ids)+b'\0'
        payload=body+branch(pos+len(body),end)
        if pos+len(payload)>TEXT_END:raise ValueError('Translated payload budget exceeded')
        rom[pos:pos+len(payload)]=payload;redirect+=struct.pack('<II',0x08000000+src,0x08000000+pos)
        locations.append(dict(id=row['id'],source=src,target=pos,end=end,translated=row['ja'] in by_ja))
        pos+=len(payload)
    if 0x8a0000+len(redirect)>0x900000:raise ValueError('Redirect table overflow')
    rom[0x8a0000:0x8a0000+len(redirect)]=redirect
    subprocess.run(['clang','-target','armv4t-none-eabi','-c',str(ROOT/'work/stage4/zh_redirect.s'),'-o',str(ROOT/'work/stage4/zh_redirect.o')],check=True)
    code=text_section(ROOT/'work/stage4/zh_redirect.o');rom[0x900000:0x900000+len(code)]=code
    rom[0x3f8046:0x3f8050]=b'\x01\x4b\x18\x47\x00\x00'+struct.pack('<I',0x08900001)
    ui_pos=0x930000
    for key,text in UI.items():
        data=b''.join(NATIVE_CODES[ids[c]*2+h].to_bytes(2,'big') for c in text for h in range(2))+b'\0'
        if 0 in data[:-1] or data[0]==255:raise ValueError('Unsafe native string encoding')
        bank=struct.unpack_from('<I',en,0x3e4268+4*(key>>12))[0]-0x08000000
        slot=bank+4*(key&4095);struct.pack_into('<I',rom,slot,0x08000000+ui_pos)
        rom[ui_pos:ui_pos+len(data)]=data;ui_pos+=len(data)
    # No raw patching over short inline messages. All script bytes stay original.
    assert rom[JP_START:JP_END]==jp[JP_START:JP_END]
    out=ROOT/'work/roms/custom-robo-gx-zh-redirect.gba';out.write_bytes(rom)
    manifest=dict(source=digest(en),target=digest(rom),translation_ledger_sha256=hashlib.sha256((ROOT/'work/catalog/reviewed-translations.json').read_bytes()).hexdigest(),characters=len(chars),font=provenance,font_bytes=len(font),
        message_count=len(rows),translated_occurrences=sum(x['translated'] for x in locations),
        translated_unique=len(by_ja),untranslated_message_occurrences=sum(not x['translated'] for x in locations),fallback=('Original Japanese rendered with Fusion Pixel; NOT complete Chinese' if any(not x['translated'] for x in locations) else 'No fallback in extracted script messages; native/graphical UI and whole-game QA remain incomplete'),
        body_bytes=pos-TEXT_BASE,table_bytes=len(redirect),engine_bytes=len(code),script_restored_byte_identical=True,
        short_messages_supported=sum(r['byte_length']<4 for r in rows),
        native_character_capacity=len(NATIVE_CODES)//2,native_encoding='Private double-byte codes; no NUL byte, no FF lead; not standard Shift-JIS',locations=locations)
    (ROOT/'outputs/reports/stage4-redirect-build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print({k:v for k,v in manifest.items() if k not in ['locations','source','target','font']})
    return manifest
if __name__=='__main__':build()
