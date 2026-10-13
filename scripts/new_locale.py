"""Create a target-language starting pack; translations remain Chinese until edited."""
from pathlib import Path
import argparse,shutil,re,json
REPO=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('locale');p.add_argument('--output',type=Path);a=p.parse_args()
 if not re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',a.locale):raise ValueError('Use a locale tag such as fr, es or zh-Hant')
 out=a.output or REPO/'locales'/a.locale
 if out.exists():raise FileExistsError(out)
 shutil.copytree(REPO/'data',out)
 (out/'locale.json').write_text(json.dumps(dict(locale=a.locale,based_on='zh-Hans',status='untranslated Chinese starting pack',engine_target_key='zh (legacy internal field; replace values with target-language text)'),indent=2)+'\n')
 print(out)
if __name__=='__main__':main()
