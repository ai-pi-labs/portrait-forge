#!/usr/bin/env python3
"""Export a portable reading pack, not a live ChatGPT installation."""
import argparse
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def export(out):
    out=Path(out).resolve()
    if out.exists():raise ValueError('Choose a new output directory')
    if ROOT==out or ROOT in out.parents:raise ValueError('Export outside the project source')
    skill=ROOT/'skill/portrait-forge'
    sources=[skill/'SKILL.md',*sorted((skill/'references').glob('*.md')),skill/'assets/fields.json']
    parts=[]
    for path in sources:
        data=path.read_text(encoding='utf-8')
        data=re.sub(r'\[([^\]]+)\]\((?!https?://)[^)]+\)',r'\1',data)
        parts.append('# Source: '+str(path.relative_to(skill))+'\n\n'+data)
    out.mkdir(parents=True)
    content='\n\n'.join(parts)
    (out/'portrait-forge-knowledge.md').write_text(content,encoding='utf-8')
    (out/'START-HERE.txt').write_text('请读取 portrait-forge-knowledge.md，将其作为本任务的人像设计参考规则。默认交付文字；明确委托才生图。没有 Python 时执行人工检查，并注明未运行程序校验。这里的资料不等于已安装 Skill。\n',encoding='utf-8')
    hashes={str(p.relative_to(skill)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (out/'provenance.json').write_text(json.dumps({'source_sha256':hashes,'live_installation':False},indent=2),encoding='utf-8')
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    try:print(export(a.out))
    except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
