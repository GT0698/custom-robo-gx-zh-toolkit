from pathlib import Path
import struct

def symbols(path):
    b=Path(path).read_bytes();off=struct.unpack_from('<I',b,32)[0];size,n,si=struct.unpack_from('<HHH',b,46)
    sections=[struct.unpack_from('<10I',b,off+i*size) for i in range(n)];out={}
    for s in sections:
        if s[1]!=2:continue
        st=sections[s[6]];names=b[st[4]:st[4]+st[5]]
        for i in range(s[4],s[4]+s[5],s[9]):
            name,val,_,info,_,ndx=struct.unpack_from('<IIIBBH',b,i)
            if name:out[names[name:].split(b'\0')[0].decode()]=val
    return out
