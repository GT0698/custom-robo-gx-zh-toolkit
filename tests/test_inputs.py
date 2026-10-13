import unittest,struct
from prepare_inputs import decode_dialogue,rom_string
class InputTests(unittest.TestCase):
 def test_source_controls_and_glyphs(self):
  image=bytearray(0x400000);struct.pack_into('<H',image,0x3f543e,0x8260);struct.pack_into('<H',image,0x3f63aa+16*2,0)
  data=bytes([0x99,16,1,1,0xf8,1,1,7,0]);image[100:100+len(data)]=data
  self.assertEqual(decode_dialogue(image,100,len(data)),'Ａ{RED}Ａ{WAIT_KEY}')
 def test_numeric_control_retained(self):
  image=bytearray(0x400000);image[10:15]=bytes([0x99,1,0x1a,255,0]);self.assertEqual(decode_dialogue(image,10,5),'{1A}')
 def test_encrypted_key_is_not_display_translation(self):
  plain='Ｃ'.encode('shift_jisx0213');data=bytes([255,plain[0]^0x3f,plain[1]^0x7e,0]);value=rom_string(data,0)
  self.assertTrue(value['encrypted']);self.assertEqual(value['text'],'Ｃ');self.assertEqual(value['raw'],data.hex())
if __name__=='__main__':unittest.main()
