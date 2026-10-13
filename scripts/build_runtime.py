"""Compile optional bounded probes against user-installed mGBA0.10 headers/library."""
from pathlib import Path
import argparse,subprocess,platform
REPO=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--include',action='append',required=True,type=Path);p.add_argument('--library-dir',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 mac=platform.system()=='Darwin';out=a.output or REPO/'.build/runtime'/('emulator_probe.dylib' if mac else 'emulator_probe.so');out.parent.mkdir(parents=True,exist_ok=True)
 cmd=['clang','-O2','-dynamiclib' if mac else '-shared','-DENABLE_SCRIPTING','-DM_CORE_GBA','-DM_CORE_GB']
 if not mac:cmd.append('-fPIC')
 for include in a.include:cmd+=['-I',str(include)]
 cmd+=[str(REPO/'src/runtime/emulator_probe.c'),'-L',str(a.library_dir),'-lmgba','-Wl,-rpath,'+str(a.library_dir.resolve()),'-o',str(out)]
 subprocess.run(cmd,check=True);print(out)
if __name__=='__main__':main()
