#!/usr/bin/env python3
"""Local CLI. JSON to stdout, errors as JSON; never generates or uploads images."""
import argparse
import json
import sys
from portraitcore.contracts import load, validate
from portraitcore.compiler import compile_plan
from portraitcore.revisions import revise, compare


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('validate','compile'):
        s=sub.add_parser(name);s.add_argument('plan');s.add_argument('--baseline')
    s=sub.add_parser('revise');s.add_argument('plan');s.add_argument('patch')
    s.add_argument('--allow',nargs='+',required=True);s.add_argument('--request',required=True)
    s=sub.add_parser('compare');s.add_argument('baseline');s.add_argument('candidate')
    a=p.parse_args()
    try:
        if a.command=='compare': result={'status':'PASS','changes':compare(load(a.baseline),load(a.candidate))}
        else:
            plan=load(a.plan)
            if a.command=='validate':
                result=validate(plan)
                if result['status']=='PASS' and plan['request']['mode']=='edit':
                    if not a.baseline: raise ValueError('edit validation requires --baseline')
                    compare(load(a.baseline),plan)
            elif a.command=='compile': result=compile_plan(plan,load(a.baseline) if a.baseline else None)
            else: result=revise(plan,load(a.patch),a.allow,a.request)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result.get('status')=='FAIL' else 0
    except (OSError,ValueError,TypeError,RecursionError) as e:
        print(json.dumps({'status':'FAIL','errors':[str(e)]},ensure_ascii=False));return 1

if __name__=='__main__': sys.exit(main())
