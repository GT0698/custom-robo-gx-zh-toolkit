"""Strict BPS1 application; based on byuu's public-domain BPS specification."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

def apply(source, patch):
    def check(condition, message):
        if not condition:
            raise ValueError(message)
    check(len(patch) >= 19 and patch[:4] == b'BPS1', 'Invalid BPS header')
    src_crc, dst_crc, patch_crc = struct.unpack('<III', patch[-12:])
    check(zlib.crc32(patch[:-4]) == patch_crc, 'Patch CRC mismatch')
    check(zlib.crc32(source) == src_crc, 'Source CRC mismatch')
    pos, end = 4, len(patch)-12
    def number():
        nonlocal pos
        value, shift = 0, 1
        for _ in range(10):
            check(pos < end, 'Truncated BPS integer')
            x = patch[pos]; pos += 1
            value += (x & 127)*shift
            if x & 128:
                return value
            shift <<= 7; value += shift
        raise ValueError('Oversized BPS integer')
    src_size, dst_size, meta_size = number(), number(), number()
    check(src_size == len(source), 'Source size mismatch')
    check(dst_size <= 32*1024*1024, 'Target exceeds GBA project limit')
    check(pos + meta_size <= end, 'Truncated metadata')
    pos += meta_size
    target = bytearray()
    src_rel = dst_rel = 0
    counts = [0]*4
    while pos < end:
        action = number(); mode, size = action & 3, (action >> 2)+1
        counts[mode] += 1
        check(len(target)+size <= dst_size, 'Output overflow')
        if mode == 0:
            offset = len(target)
            check(offset+size <= len(source), 'SourceRead overflow')
            target.extend(source[offset:offset+size])
        elif mode == 1:
            check(pos+size <= end, 'Truncated TargetRead')
            target.extend(patch[pos:pos+size]); pos += size
        else:
            delta = number(); delta = -(delta >> 1) if delta & 1 else delta >> 1
            if mode == 2:
                src_rel += delta
                check(0 <= src_rel and src_rel+size <= len(source), 'SourceCopy bounds')
                target.extend(source[src_rel:src_rel+size]); src_rel += size
            else:
                dst_rel += delta
                check(0 <= dst_rel < len(target), 'TargetCopy bounds')
                for _ in range(size):
                    target.append(target[dst_rel]); dst_rel += 1
    check(pos == end and len(target) == dst_size, 'Incomplete target')
    check(zlib.crc32(target) == dst_crc, 'Target CRC mismatch')
    return bytes(target), counts

def digest(data):
    return dict(size=len(data), crc32=f'{zlib.crc32(data):08x}',
                sha1=hashlib.sha1(data).hexdigest(), sha256=hashlib.sha256(data).hexdigest())

def encode_number(value):
    out=bytearray()
    while True:
        x=value&127;value >>= 7
        if not value:
            out.append(x|128);return bytes(out)
        out.append(x);value-=1

def create(source,target):
    """Linear BPS writer with repeated-byte compression, not size optimal."""
    out=bytearray(b'BPS1'+encode_number(len(source))+encode_number(len(target))+encode_number(0))
    pos=0;target_rel=0
    while pos<len(target):
        if pos<len(source) and source[pos]==target[pos]:
            stop=pos+1
            while stop<min(len(source),len(target)) and source[stop]==target[stop]:stop+=1
            out+=encode_number(((stop-pos-1)<<2)|0);pos=stop
            continue
        stop=pos+1
        while stop<len(target) and target[stop]==target[pos]:stop+=1
        if stop-pos>=16:
            out+=encode_number(1)+target[pos:pos+1]
            delta=pos-target_rel
            out+=encode_number(((stop-pos-2)<<2)|3)
            out+=encode_number((abs(delta)<<1)|(delta<0))
            target_rel=stop-1;pos=stop
            continue
        stop=pos+1
        while stop<len(target):
            if stop<len(source) and source[stop]==target[stop]:break
            if target[stop:stop+16]==target[stop:stop+1]*16:break
            stop+=1
        out+=encode_number(((stop-pos-1)<<2)|1)+target[pos:stop];pos=stop
    out+=struct.pack('<II',zlib.crc32(source),zlib.crc32(target))
    out+=struct.pack('<I',zlib.crc32(out))
    return bytes(out)

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path); p.add_argument('patch',type=Path); p.add_argument('output',type=Path)
    a=p.parse_args()
    s,b=a.source.read_bytes(),a.patch.read_bytes()
    t,counts=apply(s,b)
    with a.output.open('xb') as f:
        f.write(t)
    print(json.dumps(dict(source=digest(s),patch=digest(b),target=digest(t),action_counts=counts),indent=2))
