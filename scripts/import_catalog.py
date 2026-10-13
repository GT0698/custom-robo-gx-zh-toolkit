"""Import edited target column; never overwrite source identities or policies."""
from pathlib import Path
import argparse,csv,json
KIND={'dialogue':('dialogue.zh.json','id'),'native':('native.zh.json','string_id'),'offbank':('offbank.zh.json','id')}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pack',required=True,type=Path);p.add_argument('--kind',required=True,choices=KIND);p.add_argument('--csv',required=True,type=Path);a=p.parse_args();name,key=KIND[a.kind];file=a.pack/name;rows=json.loads(file.read_text(encoding='utf-8'));by={str(r[key]):r for r in rows};seen=set();changed=0
 with a.csv.open(encoding='utf-8-sig',newline='') as stream:
  for item in csv.DictReader(stream):
   identity=item['id'];assert identity in by and identity not in seen,'Unknown/duplicate identity';seen.add(identity)
   value=item['target']
   if not value:continue
   if by[identity]['zh']!=value:by[identity]['zh']=value;changed+=1
 file.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Changed target records:',changed,'; build audits still required.')
if __name__=='__main__':main()
