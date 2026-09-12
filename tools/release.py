#!/usr/bin/env python3
"""Create deterministic ZIPs plus a byte/hash inventory; no publishing."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sources(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','__pycache__')) and p.suffix!='.pyc')

def build(out):
    out=Path(out).resolve()
    if out==ROOT or ROOT in out.parents: raise ValueError('Release output must be outside project')
    out.mkdir(parents=True,exist_ok=True)
    manifest=ROOT/'manifest.json'
    rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources(ROOT) if p!=manifest]
    manifest.write_text(json.dumps({'name':'portrait-forge','version':'1.0.0','format':'project-inventory-v1','scope':'project inventory, not host plugin metadata','files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for root,name in ((ROOT,'portrait-forge-1.0.0.zip'),(ROOT/'skill/portrait-forge','portrait-forge-skill-1.0.0.zip')):
        target=out/name
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sources(root):
                info=zipfile.ZipInfo('portrait-forge/'+p.relative_to(root).as_posix(),(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,p.read_bytes())
        with zipfile.ZipFile(target) as z:
            if z.testzip():raise ValueError('Corrupt archive')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('portrait-forge*1.0.0.zip'))}
    (out/'SHA256SUMS.txt').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()),encoding='utf-8')
    return hashes
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    try:print(json.dumps(build(a.out),indent=2))
    except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
