#!/usr/bin/env python3
"""Install the bundled skill to an explicit skills parent; refuse overwrites."""
import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def install(parent):
    parent=Path(parent).expanduser().resolve()
    target=parent/'portrait-forge'
    source=ROOT/'skill/portrait-forge'
    if target.exists() or target.is_symlink(): raise ValueError('Target exists; preserve it or choose another skills parent: '+str(target))
    if source.resolve()==target or source.resolve() in target.parents: raise ValueError('Cannot install inside the source skill')
    parent.mkdir(parents=True,exist_ok=True)
    # copytree without dirs_exist_ok refuses a competing install as well.
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dest',required=True)
    a=p.parse_args()
    try: print(install(a.dest))
    except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
