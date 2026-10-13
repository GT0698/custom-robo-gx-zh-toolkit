from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[2]
BASE=0x66f730
OFFSETS=0x3e53ac
SIZES=0x3e5244

def decode_lz(data,offset):
 assert data[offset]==0x10
 size=int.from_bytes(data[offset+1:offset+4],'little');out=bytearray();p=offset+4
 while len(out)<size:
  flags=data[p];p+=1
  for mask in (128,64,32,16,8,4,2,1):
   if len(out)>=size:break
   if flags&mask:
    a,b=data[p:p+2];p+=2;n=(a>>4)+3;distance=((a&15)<<8|b)+1
    assert distance<=len(out)
    for _ in range(n):out.append(out[-distance])
   else:out.append(data[p]);p+=1
 return bytes(out[:size]),p-offset

def extract(rom,index):
 w,h=struct.unpack_from('<II',rom,SIZES+index*8)
 offset=(BASE+struct.unpack_from('<I',rom,OFFSETS+index*4)[0])&0xffffffff
 raw,size=decode_lz(rom,offset+256)
 assert len(raw)==w*h*64,(index,w,h,len(raw))
 return dict(index=index,width=w*8,height=h*8,offset=offset,palette=rom[offset:offset+256],pixels=raw,compressed_size=size)

def render(a):
 from PIL import Image
 im=Image.new('RGB',(a['width'],a['height']));cols=a['width']//8
 for y in range(a['height']):
  for x in range(a['width']):
   k=(y//8)*cols*64+(x//8)*64+(y%8)*8+x%8;idx=a['pixels'][k]&127
   color=struct.unpack_from('<H',a['palette'],idx*2)[0];im.putpixel((x,y),((color&31)*255//31,((color>>5)&31)*255//31,((color>>10)&31)*255//31))
 return im
if __name__=='__main__':
 rom=(ROOT/'work/roms/custom-robo-gx-en-v1.0.1.gba').read_bytes()
 for i in range(12,21):
  a=extract(rom,i);print(i,a['width'],a['height'],hex(a['offset']),a['compressed_size']);im=render(a);im.resize((a['width']*3,a['height']*3)).save(ROOT/f'work/stage12/menu-image-{i}.png')
