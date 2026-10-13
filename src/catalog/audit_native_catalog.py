from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2];path=ROOT/'work/catalog/reviewed-native-translations.json';raw=path.read_bytes();entries=json.loads(raw);source={x['id']:x for x in json.loads((ROOT/'work/catalog/string-banks.json').read_text())};seen=set();errors=[]
from tournament_title_policy import allowed_ids
ram_allowed=allowed_ids()
for r in entries:
 key=r['string_id'];s=source[key]
 if r.get('ram_display_alias') and key not in ram_allowed:errors.append([hex(key),'RAM alias is not a tournament title'])
 if key in seen:errors.append([hex(key),'duplicate'])
 seen.add(key)
 if s['jp']['text']!=r['ja'] or s['en']['text']!=r['en_reference']:errors.append([hex(key),'source mismatch'])
 if s['en']['encrypted']:errors.append([hex(key),'encrypted/backend string'])
 if r.get('storage_policy') not in {None,'text-only-bank-pointer'}:errors.append([hex(key),'unknown storage policy'])
 if r['alias_policy'] not in {'exact-bank-pointer','all-identical-ROM-strings'}:errors.append([hex(key),'unknown alias policy'])
 a=re.findall(r'[$#][A-Za-z0-9]',r['ja']);b=re.findall(r'[$#][A-Za-z0-9]',r['zh'])
 if r.get('layout_policy')=='reflow-newlines':a=[x for x in a if x.lower()!='$n'];b=[x for x in b if x.lower()!='$n']
 if a!=b:errors.append([hex(key),'color/icon controls differ'])
 if re.search(r'[\u3040-\u30ff]',r['zh']):errors.append([hex(key),'kana residue'])
report=dict(passed=not errors,entries=len(entries),native_ledger_sha256=hashlib.sha256(raw).hexdigest(),errors=errors,scope='Native source identity, unique IDs, explicit routing, no encrypted strings, color/icon control order; explicit newline reflow allowed. Not proof of all contexts/layouts or safe additional bank/RAM policies.')
(ROOT/'outputs/reports/native-catalog-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report);assert not errors
