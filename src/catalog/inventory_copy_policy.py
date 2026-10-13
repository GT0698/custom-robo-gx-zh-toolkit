"""Source-whitelisted inventory, prize and task-title display buffer copies."""
from pathlib import Path
import struct,json
ROOT=Path(__file__).resolve().parents[2]
TABLE=0x8F1400
POOL=0x8F1500
LIMIT=0x8F2000

def install(jp,en,rom,banks,mapping):
 parts=set();part_slots=[]
 for category in range(7):
  count=en[0x3e7d1c+category];assert count==jp[0x3e7d1c+category]
  p=struct.unpack_from('<I',en,0x3e7d24+category*4)[0]-0x08000000
  assert p==struct.unpack_from('<I',jp,0x3e7d24+category*4)[0]-0x08000000
  assert rom[p:p+count*4]==en[p:p+count*4]
  for i in range(count):
   source=struct.unpack_from('<I',en,p+i*4)[0];parts.add(source);part_slots.append(p+i*4)
 tables=json.loads((ROOT/'work/native-audit/data-table-index.json').read_text())['tables']
 def check_table(t):
  at=t['address'];n=t['rows']*t['columns']*t['entry_bytes'];assert rom[at:at+9+n]==jp[at:at+9+n]
 title_table=tables['LadyPThemeBattleData'];check_table(title_table)
 assert title_table['rows']==28 and title_table['columns']==16
 titles={0x08000000+banks[title_table['values'][i*16+1]]['en']['offset'] for i in range(28)}
 prizes=set();prize_tables=[]
 for name,t in tables.items():
  if not name.startswith('KadaiShouhinData'):continue
  check_table(t);prize_tables.append(name)
  for row in range(t['rows']):
   values=t['values'][row*t['columns']:(row+1)*t['columns']]
   if values[0]==999:continue
   prizes.add(0x08000000+banks[values[2]]['en']['offset'])
 # Validate the actual name source, width and copy opcode at every new route.
 patterns={
  0x50dc71:'062a00062c00bd020b44',
  0x51cc21:'061600060000bd020b44',
  0x511615:'060000020248020b44',
  0x5111d7:'060000020148021044',
 }
 for pc,h in patterns.items():
  raw=bytes.fromhex(h);assert jp[pc-len(raw):pc]==rom[pc-len(raw):pc]==raw,(hex(pc),'route drift')
 assert rom[TABLE:LIMIT]==b'\xff'*(LIMIT-TABLE)
 pos=POOL;source_sets={};bounds=[]
 for name,sources,width,extra in [('parts',parts,14,8),('prizes',prizes,14,4),('titles',titles,16,4)]:
  ordered=sorted(sources);start=pos
  for pointer in ordered:
   source=pointer-0x08000000;target=mapping.get(source,source)
   raw=rom[target:rom.index(0,target)];assert raw and raw[0]!=255
   i=cells=copied=0
   while i<len(raw):
    b=raw[i]
    if b==36:assert raw[i+1] not in [ord('n'),ord('N')];i+=2;continue
    step=2 if b==35 or rom[0x3d6088+(b>>4)] else 1
    i+=step;copied+=step;cells+=1
   assert cells<=width,(name,hex(source),cells,width)
   length=copied+width-cells+extra;assert length<=46,(name,hex(source),length)
   bounds.append(dict(group=name,source=source,target=target,half_cells=cells,maximum_row_bytes=length))
  blob=b''.join(struct.pack('<I',x) for x in ordered)
  rom[pos:pos+len(blob)]=blob;pos+=len(blob);source_sets[name]=dict(pointer=0x08000000+start,count=len(ordered),sources=ordered)
 rules=[(0x0850dc71,'parts',14),(0x0851cc21,'parts',14),(0x08511615,'prizes',14),(0x085111d7,'titles',16)]
 blob=struct.pack('<I',len(rules))+b''.join(struct.pack('<IIII',pc,source_sets[name]['pointer'],source_sets[name]['count'],width) for pc,name,width in rules)
 assert TABLE+len(blob)<=POOL and pos<=LIMIT
 rom[TABLE:TABLE+len(blob)]=blob
 return dict(rules=[dict(script_pc=pc,source_group=name,width=width) for pc,name,width in rules],source_sets=source_sets,bounds=bounds,part_reference_slots=part_slots,prize_tables=prize_tables,allocation=[TABLE,pos],scope='Exact PC and source membership plus current selected valid48-byte Strbuf. Original data/key bytes and all nonmatching callers retained.')
