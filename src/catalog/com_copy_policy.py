"""Exact COM/battle settings display-buffer routes; no general RAM rewrite."""
import struct
RIGHT_TABLE=0x8F1100
RIGHT_LIMIT=0x8F1400
STARTS=[0x50EC02,0x50EC1E,0x50EDC0,0x50EE4B,0x50EF12,0x50EF2E,0x50EF4A,0x50F1EA,0x50F275,0x50F300]
FIELDS={
 0x522:(0,0x22,0x50F514,list(range(0x529,0x52E)),6),
 0x523:(1,0x23,0x50F527,list(range(0x52E,0x532)),6),
 0x526:(0,0x22,0x50F538,[0x37C,0x37D,0x37E,0x37F,0x37B],4),
 0x527:(1,0x23,0x50F538,[0x37C,0x37D,0x37E,0x37F,0x37B],4),
 0x528:(2,0x21,0x50F54B,[0x379,0x37A,0x37B],4),
}
def install(jp,en,rom,banks):
 left=[];right=[];groups=[]
 def source(key):
  r=banks[key];assert not r['en']['encrypted']
  for data,lang in [(jp,'jp'),(en,'en')]:
   p=struct.unpack_from('<I',data,r['pointer_slot'])[0]-0x08000000
   assert p==r[lang]['offset']
   raw=bytes.fromhex(r[lang]['raw']);assert data[p:p+len(raw)]==raw
  return 0x08000000+r['en']['offset']
 for at in STARTS:
  key=int.from_bytes(jp[at+1:at+3],'little');index,var,table,values,width=FIELDS[key]
  prefix=bytes([2,index,0x3f,5])+struct.pack('<H',key)+bytes([2,9,0x42])
  suffix=bytes([2,0,6])+struct.pack('<H',var)+bytes([0x48,2,width,0x45])
  for data in [jp,rom]:
   assert data[at-3:at+6]==prefix,(hex(at),'prefix')
   assert data[at+6:at+15]==suffix,(hex(at),'value')
   assert data[table+4:table+9]==b'\0'+struct.pack('<HH',1,len(values))
   assert data[table+9:table+9+len(values)*2]==struct.pack('<'+'H'*len(values),*values)
  dest=0x020132E0+48*index
  left.append(dict(script_pc=0x08000000+at+6,source=source(key),destination=dest,string_id=key,width=9))
  for value in values:right.append(dict(script_pc=0x08000000+at+15,source=source(value),destination=dest,string_id=value,original_width=width,new_width=6))
  groups.append(dict(label_id=key,destination=dest,left_pc=0x08000000+at+6,right_pc=0x08000000+at+15,values=values,original_right_width=width))
 blob=struct.pack('<I',len(right))+b''.join(struct.pack('<III',r['script_pc'],r['source'],r['destination']) for r in right)
 assert RIGHT_TABLE+len(blob)<=RIGHT_LIMIT
 assert rom[RIGHT_TABLE:RIGHT_LIMIT]==b'\xff'*(RIGHT_LIMIT-RIGHT_TABLE)
 rom[RIGHT_TABLE:RIGHT_TABLE+len(blob)]=blob
 return dict(left=left,right=right,groups=groups,scope='Exact PC/source/destination. Right fields6 half-cells preserve120秒 and all values; script numeric settings unchanged.')
