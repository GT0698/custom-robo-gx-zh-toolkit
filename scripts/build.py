#!/usr/bin/env python3
"""Portable, isolated build from local Japanese ROM plus EnglishV1.0.1 input."""
from pathlib import Path
import argparse,sys,hashlib,shutil,tempfile,subprocess,json
from prepare_inputs import prepare,read_json,write_json
REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src/tools'))
from bps import apply,create,digest

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--japanese-rom',required=True,type=Path)
 group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument('--english-rom',type=Path);group.add_argument('--english-bps',type=Path)
 parser.add_argument('--translations',type=Path,default=REPO/'data')
 parser.add_argument('--font',type=Path,default=REPO/'third_party/fusion_pixel/fusion-pixel-12px-monospaced-zh_hans.bdf')
 parser.add_argument('--output',type=Path,default=REPO/'.build/artifacts/custom-robo-gx-zh.gba')
 parser.add_argument('--verify-reference',action='store_true')
 args=parser.parse_args();reference=read_json(REPO/'reference-build.json')
 jp=args.japanese_rom.read_bytes();assert digest(jp)['sha1']==reference['japanese_sha1'],'Wrong Japanese ROM'
 en=args.english_rom.read_bytes() if args.english_rom else apply(jp,args.english_bps.read_bytes())[0]
 assert digest(en)['sha1']==reference['english_sha1'],'English input must beV1.0.1'
 assert shutil.which('clang'),'Clang with armv4t-none-eabi target is required'
 out=args.output.resolve();assert out not in [args.japanese_rom.resolve(),args.english_rom.resolve() if args.english_rom else args.english_bps.resolve()],'Output cannot overwrite input'
 private=REPO/'.build';private.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='isolated-',dir=private) as temp:
  workspace=Path(temp);shutil.copytree(REPO/'src',workspace/'work')
  (workspace/'outputs/reports').mkdir(parents=True);(workspace/'work/roms').mkdir()
  (workspace/'work/roms/custom-robo-gx-jp.gba').write_bytes(jp);(workspace/'work/roms/custom-robo-gx-en-v1.0.1.gba').write_bytes(en)
  font_dir=workspace/'work/upstream/fusion-font/extracted';font_dir.mkdir(parents=True)
  shutil.copyfile(args.font,font_dir/'fusion-pixel-12px-monospaced-zh_hans.bdf')
  counts=prepare(workspace,args.translations,jp,en)
  for script in ['work/catalog/audit_translations.py','work/catalog/audit_native_catalog.py','work/stage5/build_overlay.py']:
   subprocess.run([sys.executable,str(workspace/script)],cwd=workspace,check=True)
  rom=(workspace/'work/roms/custom-robo-gx-zh-native-overlay.gba').read_bytes();actual=digest(rom)
  if args.verify_reference:assert actual==reference['target'],'Reference build differs'
  if out.exists() and out.read_bytes()!=rom:raise FileExistsError('Choose a new output filename; existing file differs')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(rom)
  patch=create(en,rom);assert apply(en,patch)[0]==rom;out.with_suffix('.bps').write_bytes(patch)
  locale_file=args.translations/'locale.json';locale=read_json(locale_file).get('locale','zh-Hans') if locale_file.exists() else 'zh-Hans'
  manifest=dict(target_locale=locale,source=digest(en),target=actual,counts=counts,patch=digest(patch),patch_roundtrip=True,reference_match=actual==reference['target'],font_sha256=hashlib.sha256(args.font.read_bytes()).hexdigest(),full_single_player_acceptance=False)
  write_json(out.with_suffix('.manifest.json'),manifest)
  # Generated source catalogs/reports contain upstream content; keep them private.
  shutil.copytree(workspace/'outputs/reports',out.parent/'reports',dirs_exist_ok=True)
 print(json.dumps(dict(target=actual,reference_match=manifest['reference_match'],output=str(out),patch=str(out.with_suffix('.bps'))),indent=2))
if __name__=='__main__':main()
