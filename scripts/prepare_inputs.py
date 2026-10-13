"""Generate source catalogs locally from user-supplied ROMs; no source corpus bundled."""
from pathlib import Path
import json,struct,hashlib,re
CONTROL={1:'RED',2:'GREEN',3:'GRAY',4:'BLACK',5:'NEWLINE',7:'WAIT_KEY',8:'WAIT',10:'PLAYER'}
BANKS=[(0x3e25e0,0x3e3e74),(0x3e3e74,0x3e3f4c),(0x3e3f4c,0x3e3fc8),(0x3e3fc8,0x3e40a4),(0x3e40a4,0x3e411c),(0x3e411c,0x3e4120),(0x3e4120,0x3e41b4),(0x3e41b4,0x3e4268)]
def read_json(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write_json(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rom_string(image,p):
 start=p;encrypted=image[p]==255;decoded=bytearray()
 if encrypted:
  p+=1
  while image[p]!=0:
   if p-start>4096:raise ValueError('Unbounded encrypted string')
   decoded.extend([image[p]^0x3f,image[p+1]^0x7e]);p+=2
 else:
  end=image.index(0,p);assert end-p<4096;decoded.extend(image[p:end]);p=end
 return dict(offset=start,raw=image[start:p+1].hex(),encrypted=encrypted,text=decoded.decode('shift_jisx0213'),error=None)
def decode_dialogue(jp,offset,length):
 raw=jp[offset:offset+length];assert raw[0]==0x99 and raw[-1]==0
 def glyph(index):
  if index==0:return '▀'
  v=struct.unpack_from('<H',jp,0x3f543e+(index-1)*2)[0]
  return v.to_bytes(2,'big').decode('shift_jisx0213')
 p=1;out=[]
 while raw[p]:
  b=raw[p];p+=1
  if b==1:
   n=raw[p];p+=1;out.append('{'+CONTROL.get(n,f'{n:02X}')+'}')
  elif b==255:continue
  elif b>=248:
   index=(b-248)*256+raw[p];p+=1;out.append(glyph(index))
  else:out.append(glyph(struct.unpack_from('<H',jp,0x3f63aa+b*2)[0]+1))
 assert p==length-1
 return ''.join(out)
def prepare(workspace,data_dir,jp,en):
 data_dir=Path(data_dir);workspace=Path(workspace)
 spans=read_json(data_dir/'message-spans.json');translations=read_json(data_dir/'dialogue.zh.json');by_id={r['id']:r for r in translations}
 messages=[];units={}
 for offset,length in spans:
  text=decode_dialogue(jp,offset,length);key='ja-'+hashlib.sha256(text.encode()).hexdigest()[:16];assert key in by_id,'Source content identity mismatch'
  controls=re.findall(r'\{[^}]+\}',text)
  messages.append(dict(id='jp-msg-'+hex(offset)[2:],offset=offset,byte_length=length,ja=text,controls=controls))
  if key not in units:units[key]=dict(id=key,ja=text,controls=controls,occurrences=[])
  units[key]['occurrences'].append(offset)
 assert set(units)==set(by_id)
 hydrated=[]
 for r in translations:
  row=dict(r);row['ja']=units[r['id']]['ja'];row['status']='draft';hydrated.append(row)
 write_json(workspace/'work/text/japanese-messages.json',messages);write_json(workspace/'work/catalog/dialogue-units.json',list(units.values()));write_json(workspace/'work/catalog/reviewed-translations.json',hydrated)
 banks=[]
 for number,(start,end) in enumerate(BANKS):
  for slot in range(start,end,4):
   banks.append(dict(id=(number<<12)+(slot-start)//4,pointer_slot=slot,jp=rom_string(jp,struct.unpack_from('<I',jp,slot)[0]-0x08000000),en=rom_string(en,struct.unpack_from('<I',en,slot)[0]-0x08000000)))
 write_json(workspace/'work/catalog/string-banks.json',banks);bank_ids={r['id']:r for r in banks}
 native=[]
 for r in read_json(data_dir/'native.zh.json'):
  row=dict(r);source=bank_ids[r['string_id']];row.update(ja=source['jp']['text'],en_reference=source['en']['text']);native.append(row)
 write_json(workspace/'work/catalog/reviewed-native-translations.json',native)
 offbank=[]
 for r in read_json(data_dir/'offbank.zh.json'):
  row=dict(r);j=rom_string(jp,r.get('jp_offset',r['source_offset']));e=rom_string(en,r['source_offset']);assert not j['encrypted'] and not e['encrypted'];row.update(ja=j['text'],en_reference=e['text'],jp_raw_hex=j['raw'],en_raw_hex=e['raw']);offbank.append(row)
 write_json(workspace/'work/catalog/reviewed-offbank-translations.json',offbank)
 descriptions=[]
 for r in read_json(data_dir/'description-locations.json'):
  row=dict(r);j=rom_string(jp,r['jp_offset']);e=rom_string(en,r['source_offset']);row.update(ja=j['text'],en_reference=e['text'],jp_raw_hex=j['raw'],en_raw_hex=e['raw']);descriptions.append(row)
 write_json(workspace/'work/catalog/equipment-description-inventory.json',descriptions)
 write_json(workspace/'work/catalog/league-object-inventory.json',read_json(data_dir/'league-objects.json'))
 tables={}
 for name,r in read_json(data_dir/'script-table-layouts.json').items():
  row=dict(r);n=r['rows']*r['columns'];size=r['entry_bytes'];at=r['address']+9
  row['values']=[int.from_bytes(jp[at+i*size:at+(i+1)*size],'little') for i in range(n)];tables[name]=row
 write_json(workspace/'work/native-audit/data-table-index.json',dict(tables=tables))
 return dict(script_units=len(units),message_occurrences=len(messages),native_records=len(native),offbank_records=len(offbank))
