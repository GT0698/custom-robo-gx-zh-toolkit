import unittest,struct,zlib
from bps import apply,create,encode_number

class BPSTest(unittest.TestCase):
    def test_all_actions_and_overlap(self):
        # SourceRead ab, TargetRead XY, SourceCopy ef, TargetCopy XYefXYef.
        s=b'abcdef';t=b'abXYefXYefXYef'
        p=bytearray(b'BPS1'+encode_number(len(s))+encode_number(len(t))+encode_number(0))
        p+=encode_number(4)+encode_number(5)+b'XY'+encode_number(6)+encode_number(8)
        p+=encode_number(31)+encode_number(4)
        p+=struct.pack('<II',zlib.crc32(s),zlib.crc32(t));p+=struct.pack('<I',zlib.crc32(p))
        self.assertEqual(apply(s,p),(t,[1,1,1,1]))
    def test_create_roundtrip(self):
        for s,t in [(b'abc',b'abc'),(b'',b'X'*1000),(b'abcd',b'abZZcd'),(b'abcd',b'ab'),(b'ab',b''),(bytes(range(255)),b'x'*32+bytes(range(255))+b'\xff'*4096)]:
            self.assertEqual(apply(s,create(s,t))[0],t)
    def test_wrong_source(self):
        with self.assertRaisesRegex(ValueError,'Source CRC'):apply(b'bad',create(b'abc',b'xyz'))
    def test_corruption(self):
        p=bytearray(create(b'abc',b'xyz'));p[5]^=1
        with self.assertRaisesRegex(ValueError,'Patch CRC'):apply(b'abc',p)
    def test_bad_target_checksum(self):
        p=bytearray(create(b'abc',b'xyz'));p[-8]^=1;p[-4:]=struct.pack('<I',zlib.crc32(p[:-4]))
        with self.assertRaisesRegex(ValueError,'Target CRC'):apply(b'abc',p)
    def test_out_of_bounds_target_copy(self):
        p=bytearray(b'BPS1'+encode_number(0)+encode_number(1)+encode_number(0)+encode_number(3)+encode_number(0))
        p+=struct.pack('<II',0,0);p+=struct.pack('<I',zlib.crc32(p))
        with self.assertRaisesRegex(ValueError,'TargetCopy bounds'):apply(b'',p)

if __name__=='__main__':unittest.main()
