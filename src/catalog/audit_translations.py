"""Check dialogue source identities and engine control contracts before reporting progress."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'work/catalog/reviewed-translations.json';raw=path.read_bytes();rows=json.loads(raw)
sources={x['id']:x for x in json.loads((ROOT/'work/catalog/dialogue-units.json').read_text())}
# Deliberately accepted opening layout changes; exact outputs, not blanket exemptions.
layout_overrides={
 'ja-4cfa9ccfb541ebb5':[],
 'ja-51117a0a297c7cbe':['{NEWLINE}','{GREEN}','{BLACK}','{WAIT_KEY}','{RED}','{BLACK}','{WAIT_KEY}'],
}
errors=[];seen=set()
for r in rows:
 key=r['id'];source=sources.get(key)
 if key in seen:errors.append(dict(id=key,issue='duplicate'))
 seen.add(key)
 if not source:errors.append(dict(id=key,issue='unknown source'));continue
 if r['ja']!=source['ja']:errors.append(dict(id=key,issue='source changed'))
 if r['source_offset'] not in source['occurrences']:errors.append(dict(id=key,issue='offset mismatch'))
 expected=layout_overrides.get(key,source['controls'])
 if re.findall(r'\{[^}]+\}',r['zh'])!=expected:errors.append(dict(id=key,issue='control sequence mismatch'))
 if re.search(r'[\u3040-\u30ff]',r['zh']):errors.append(dict(id=key,issue='kana in Chinese'))
 if not r['zh']:errors.append(dict(id=key,issue='empty translation'))
report=dict(passed=not errors,entries=len(rows),ledger_sha256=hashlib.sha256(raw).hexdigest(),errors=errors,control_layout_exceptions=layout_overrides,scope='Source identity, unique IDs, source offsets, exact controls except two recorded opening layouts, nonempty text, no kana. Not proof of semantic perfection or full scene coverage.')
(ROOT/'outputs/reports/translation-ledger-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
assert not errors,errors
