"""Export Japanese/English/target review catalogs into a private local directory."""
from pathlib import Path
import argparse,tempfile,csv,sys
from prepare_inputs import prepare,read_json
REPO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(REPO/'src/tools'))
from bps import digest

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--japanese-rom',required=True,type=Path);p.add_argument('--english-rom',required=True,type=Path);p.add_argument('--translations',type=Path,default=REPO/'data');p.add_argument('--output',type=Path,default=REPO/'.build/catalogs');a=p.parse_args()
 ref=read_json(REPO/'reference-build.json');jp=a.japanese_rom.read_bytes();en=a.english_rom.read_bytes();assert digest(jp)['sha1']==ref['japanese_sha1'] and digest(en)['sha1']==ref['english_sha1']
 if a.output.exists():raise FileExistsError('Choose a new catalog directory')
 a.output.mkdir(parents=True)
 with tempfile.TemporaryDirectory() as temp:
  w=Path(temp);prepare(w,a.translations,jp,en)
  for name,source,idkey in [('dialogue','reviewed-translations.json','id'),('native','reviewed-native-translations.json','string_id'),('offbank','reviewed-offbank-translations.json','id')]:
   with (a.output/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['id','source_offset','ja','en_reference','target']);writer.writeheader()
    for r in read_json(w/'work/catalog'/source):writer.writerow(dict(id=r[idkey],source_offset=r.get('source_offset',''),ja=r['ja'],en_reference=r.get('en_reference',''),target=r['zh']))
 print('Local source catalog exported. Keep it private; English script alignment is intentionally not guessed from equal offsets.')
if __name__=='__main__':main()
