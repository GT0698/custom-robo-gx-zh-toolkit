# coding: utf-8
"""Validate exact ROM display-string sources before inserting overlay payloads."""
from pathlib import Path
import json,hashlib,re,struct
ROOT=Path(__file__).resolve().parents[2]
def audit():
 path=ROOT/'work/catalog/reviewed-offbank-translations.json';raw=path.read_bytes();rows=json.loads(raw)
 jp=(Path(__file__).resolve().parents[2]/'work/roms/custom-robo-gx-jp.gba').read_bytes()
 en=(ROOT/'work/roms/custom-robo-gx-en-v1.0.1.gba').read_bytes()
 assert hashlib.sha1(jp).hexdigest()=='0b5ce051aa1fd83ab0ec79122b07b02bb41096a5'
 assert hashlib.sha1(en).hexdigest()=='e033251c780dbbd83b15623159b743d2e624d8a0'
 seen=set()
 native={r['string_id']:r for r in json.loads((ROOT/'work/catalog/reviewed-native-translations.json').read_text())}
 descriptions={r['source_offset']:r for r in json.loads((ROOT/'work/catalog/equipment-description-inventory.json').read_text())}
 for r in rows:
  p=r['source_offset'];assert p not in seen;seen.add(p)
  if 'native_string_id' in r:
   n=native[r['native_string_id']]
   assert r['ja']==n['ja'] and r['zh']==n['zh'], 'Paired name alias drifted from canonical translation'
   cat=r['name_table_category'];index=r['name_table_index']
   assert cat in [5,6]
   assert index<en[0x3e7d1c+cat]==jp[0x3e7d1c+cat]
   a=struct.unpack_from('<I',en,0x3e7d24+4*cat)[0]-0x08000000
   assert a==struct.unpack_from('<I',jp,0x3e7d24+4*cat)[0]-0x08000000
   assert r['reference_slots']==[a+index*4]
  assert r['route']=='exact-ROM-display-pointer'
  for rom,key,textkey in [(jp,'jp_raw_hex','ja'),(en,'en_raw_hex','en_reference')]:
   value=bytes.fromhex(r[key]);assert value.endswith(b'\0') and b'\0' not in value[:-1]
   source=r.get('jp_offset',p) if rom is jp else p
   assert value[0]!=255 and rom[source:source+len(value)]==value,(r['id'],'source mismatch')
   assert value[:-1].decode('shift_jisx0213')==r[textkey]
  if p in descriptions:
   expected=descriptions[p]
   assert r.get('jp_offset',p)==expected['jp_offset'] and r['ja']==expected['ja'], 'Description alignment mismatch'
   assert r.get('reference_slots')==expected['reference_slots'], 'Description requires table references'
  if r.get('jp_offset',p)!=p:assert r.get('reference_slots'), 'Relocated source requires matching literal references'
  if r.get('reference_slots'):
   for slot in r['reference_slots']:
    assert struct.unpack_from('<I',jp,slot)[0]==0x08000000+r.get('jp_offset',p)
    assert struct.unpack_from('<I',en,slot)[0]==0x08000000+p
  if r.get('kind')=='map-inline-label':
   kind=r['map_record_kind'];i=r['map_record_index'];field=r['map_field_offset']
   if kind=='node':
    assert 1<=i<=16 and (field==0 or (i==5 and field==23))
    assert p==0x7b76a0+i*0x70+field
   else:
    assert kind=='header' and i in (1,2) and field==0
    assert p==0x7b84a0+i*0x64
   assert len(bytes.fromhex(r['en_raw_hex']))<=23
   assert struct.unpack_from('<I',en,0x183e4)[0]==struct.unpack_from('<I',jp,0x183e4)[0]==0x087b84a0
   for image in (jp,en):
    assert struct.unpack_from('<I',image,0x7b84f0)[0]==0x087b76a0 and image[0x7b84f4]==32
   assert r.get('jp_offset',p)==p
  else:
   assert en.count(struct.pack('<I',0x08000000+p))>0,(r['id'],'no ROM reference')
  assert '%' not in r['ja'] and '%' not in r['en_reference'],'Format templates require separate review'
  source_controls=re.findall(r'[$#][A-Za-z0-9]',r['ja']);target_controls=re.findall(r'[$#][A-Za-z0-9]',r['zh'])
  assert target_controls==r['controls']
  if r.get('layout_policy')=='reflow-newlines':
   source_controls=[x for x in source_controls if x.lower()!='$n'];target_controls=[x for x in target_controls if x.lower()!='$n']
  assert source_controls==target_controls
  assert not re.search(r'[\u3040-\u30ff]',r['zh'])
 result=dict(passed=True,entries=len(rows),ledger_sha256=hashlib.sha256(raw).hexdigest(),scope='Exact Japanese/English source bytes, NUL termination, existing ROM reference, display-only routing, controls and no format-template mutations; not reachability or all-layout proof.')
 (ROOT/'outputs/reports/offbank-catalog-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
if __name__=='__main__':print(audit())
