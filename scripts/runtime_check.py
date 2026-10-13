"""Run representative whole-glyph placement probes; no gameplay or screenshots."""
from pathlib import Path
import argparse,ctypes as C,struct,json,hashlib

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',required=True,type=Path);p.add_argument('--rom',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 raw=a.rom.read_bytes();assert len(raw)==0x1000000
 lib=C.CDLL(str(a.library.resolve()));lib.start.argtypes=[C.c_char_p];lib.start.restype=C.c_int;lib.test_write_ram.argtypes=[C.c_uint,C.c_char_p,C.c_uint];lib.test_write_ram.restype=C.c_int;lib.glyph_wrap_probe.argtypes=[C.c_uint,C.c_uint];lib.glyph_wrap_probe.restype=C.c_int;lib.glyph_probe_result.restype=C.c_void_p
 assert lib.start(str(a.rom.resolve()).encode())
 def put(p,b):assert lib.test_write_ram(p,b,len(b))
 results=[];context=0x0203e000
 try:
  for table,first,bitmap,count_at in [(0x08880000,1719,0x08800000,0x88f000),(0x08884000,236,0x08840000,0x88f002)]:
   count=struct.unpack_from('<H',raw,count_at)[0];assert count>=first+1
   desc=bytearray(32);struct.pack_into('<III',desc,0,bitmap,table,0x083f61aa);struct.pack_into('<IHH',desc,16,0x06004000,30,count);put(0x030013b0,bytes(desc))
   for remaining in [0,1,2]:
    ctx=bytearray(16);ctx[2]=16;ctx[3]=10;ctx[4]=1;ctx[6]=21-remaining;struct.pack_into('<I',ctx,12,0x030013b0);put(context,bytes(ctx))
    placed=[]
    for glyph in [first,first+1]:
     assert lib.glyph_wrap_probe(context,glyph)
     placed.append(list(C.cast(lib.glyph_probe_result(),C.POINTER(C.c_uint*3)).contents))
    expected=(0,1) if remaining<2 else (19,0)
    assert placed[0][:2]==list(expected) and placed[1][:2]==[expected[0]+1,expected[1]]
    results.append(dict(table=hex(table),remaining_half_cells=remaining,positions=placed))
 finally:lib.stop()
 report=dict(passed=True,rom_sha1=hashlib.sha1(raw).hexdigest(),cases=results,gameplay_frames=0,screenshots=0,scope='Actual DrawChar/newline placement; pixel blitter bypassed before callee push. Not a playthrough or visual scene acceptance.')
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
