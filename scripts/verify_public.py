"""Fail closed before packaging/publishing: no private inputs, identity or artifacts."""
from pathlib import Path
import json,re,subprocess,ast
REPO=Path(__file__).resolve().parents[1]
TOP={'src','scripts','data','third_party','tests','docs','.github','locales','README.md','README.zh-CN.md','CREDITS.md','LICENSE_STATUS.md','LICENSE.txt','CHANGELOG.md','CONTRIBUTING.md','AGENTS.md','reference-build.json','requirements.txt','.gitignore'}
PRIVATE={'.build','.venv','.git','__pycache__'}
SUFFIX={'.py','.s','.c','.json','.md','.txt','.bdf','.yml','.yaml'}
FORBIDDEN={'.gba','.sav','.rawstate','.ss0','.ss1','.o','.so','.dylib','.zip','.png','.jpg','.jpeg','.webp','.bps','.env'}
def public_files(repo=REPO):
 files=[]
 for p in sorted(repo.rglob('*')):
  rel=p.relative_to(repo)
  if any(x in PRIVATE for x in rel.parts):continue
  if p.is_symlink():raise ValueError('Symlink rejected: '+str(rel))
  if not p.is_file():continue
  if p.name=='.DS_Store':raise ValueError('Finder metadata rejected')
  if rel.parts[0] not in TOP:raise ValueError('Unexpected export path: '+str(rel))
  if p.name!='.gitignore' and p.suffix.lower() not in SUFFIX:raise ValueError('Unsupported export file: '+str(rel))
  if p.suffix.lower() in FORBIDDEN:raise ValueError('Binary/private artifact rejected: '+str(rel))
  s=p.read_text(encoding='utf-8')
  private_patterns=[r'/'+r'Users/[^/\s]+/',r'/'+r'var/folders/',r'/'+r'home/[^/\s]+/','codex-'+'clipboard-','DS'+'H_','DEEPSEEK_'+'API_KEY',r'(?:sk-|ghp_|github_pat_)[A-Za-z0-9_]{20,}']
  if any(re.search(pattern,s) for pattern in private_patterns):raise ValueError('Personal path/config/credential-like value: '+str(rel))
  if p.suffix=='.py':ast.parse(s,filename=str(rel))
  if p.suffix=='.json':
   data=json.loads(s)
   if rel.parts[0] in {'data','locales'} and p.name!='glossary.json':
    def walk(x):
     if isinstance(x,dict):
      if {'ja','en_reference','jp_raw_hex','en_raw_hex','raw'} & x.keys():raise ValueError('Source corpus/raw dump in public target data: '+str(rel))
      for v in x.values():walk(v)
     elif isinstance(x,list):
      for v in x:walk(v)
    walk(data)
  files.append(p)
 if (repo/'.git').exists():
  result=subprocess.run(['git','ls-files','-z'],cwd=repo,capture_output=True,check=True)
  for name in result.stdout.decode().split('\0'):
   if name and (Path(name).parts[0] in PRIVATE or Path(name).suffix.lower() in FORBIDDEN):raise ValueError('Private file already tracked: '+name)
 return files
if __name__=='__main__':print(json.dumps(dict(passed=True,public_files=len(public_files()),scope='Export content/path safeguards; not a legal authorization check.'),indent=2))
