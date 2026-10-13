"""Audited retry sites plus caller-supplied COM label buffer rules."""
import struct

TABLE = 0x8F1000
LIMIT = 0x8F1100
# pushstr address, string ID, original padding, opcode, destination buffer index.
SITES = [
    (0x4FE267, 0x19D, 6, 0x42, 0),
    (0x4FE273, 0x19E, 4, 0x44, 0),
    (0x4FE3A4, 0x1A1, 4, 0x42, 0),
    (0x4FE3B0, 0x1A2, 2, 0x44, 0),
    (0x4FE3D0, 0x1A1, 4, 0x42, 1),
    (0x4FE3DC, 0x1A2, 2, 0x44, 1),
    (0x4FE3FC, 0x1A1, 4, 0x42, 2),
    (0x4FE408, 0x1A2, 2, 0x44, 2),
]

def audit(jp, en, built, banks):
    # The English patch copies the full string and retains minimum padding.
    # Do not silently reuse this policy with the original clipping instruction.
    assert en[0xA978:0xA97A] == built[0xA978:0xA97A] == bytes.fromhex('6f45')
    out=[]
    for offset, key, width, opcode, index in SITES:
        sequence=b'\x05'+struct.pack('<H',key)+bytes([2,width,opcode])
        # This project restores the Japanese bytecode addresses. The English
        # script layout differs, so its same-address bytes are not evidence.
        for rom in (jp, built):
            assert rom[offset:offset+6]==sequence, ('retry script changed', hex(offset))
        row=banks[key]
        assert not row['en']['encrypted']
        for rom, lang in [(jp,'jp'),(en,'en')]:
            pointer=struct.unpack_from('<I',rom,row['pointer_slot'])[0]
            assert pointer==0x08000000+row[lang]['offset']
            raw=bytes.fromhex(row[lang]['raw'])
            assert rom[pointer-0x08000000:pointer-0x08000000+len(raw)]==raw
        out.append(dict(script_pc=0x08000000+offset+6,
                        source=0x08000000+row['en']['offset'],
                        destination=0x020132E0+48*index,
                        string_id=key, width=width))
    return out

def install(jp,en,rom,banks,extra_rows=()):
    rows=audit(jp,en,rom,banks)
    combined=rows+list(extra_rows)
    table=struct.pack('<I',len(combined))+b''.join(struct.pack('<III',r['script_pc'],r['source'],r['destination']) for r in combined)
    assert TABLE+len(table)<=LIMIT
    assert rom[TABLE:LIMIT]==b'\xff'*(LIMIT-TABLE), 'retry table allocation collision'
    rom[TABLE:TABLE+len(table)]=table
    return rows
