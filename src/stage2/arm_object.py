"""Extract .text from a little-endian ELF32 object, refusing relocations."""
from pathlib import Path
import struct
def text_section(path):
    b=Path(path).read_bytes()
    if b[:6]!=b'\x7fELF\x01\x01':raise ValueError('Expected little-endian ELF32')
    shoff=struct.unpack_from('<I',b,32)[0]
    entsize,count,stridx=struct.unpack_from('<HHH',b,46)
    secs=[struct.unpack_from('<10I',b,shoff+i*entsize) for i in range(count)]
    st=secs[stridx];names=b[st[4]:st[4]+st[5]]
    for s in secs:
        if s[1] in (4,9) and s[5]:raise ValueError('Unexpected linker relocation')
    for s in secs:
        n=names[s[0]:].split(b'\0')[0]
        if n==b'.text':return b[s[4]:s[4]+s[5]]
    raise ValueError('No text section')
