"""Exact-path edits bound to a baseline; unchanged cells retain evidence and unknowns."""
from copy import deepcopy
from .contracts import FIELDS, digest, validate


def require_valid(plan):
    report=validate(plan)
    if report['status']!='PASS': raise ValueError(str(report['errors']))


def compare(base, candidate):
    require_valid(base); require_valid(candidate)
    if len(base['cards'])!=1 or len(candidate['cards'])!=1:
        raise ValueError('revision requires single-card plans')
    rev=candidate.get('revision')
    if not rev or rev['base_sha256']!=digest(base): raise ValueError('baseline hash mismatch')
    if candidate['request']['mode']!='edit': raise ValueError('revision mode must be edit')
    if candidate['policy']!=base['policy']: raise ValueError('policy changed')
    a,b=base['cards'][0],candidate['cards'][0]
    for k in ('id','intent','locks','assumptions'):
        if a[k]!=b[k]: raise ValueError('metadata changed: '+k)
    actual={k:{'before':a['fields'].get(k),'after':b['fields'].get(k)}
            for k in sorted(set(a['fields'])|set(b['fields'])) if a['fields'].get(k)!=b['fields'].get(k)}
    if not set(actual)<=set(rev['allowed']): raise ValueError('changes outside allowed fields')
    if actual!=rev['changes']: raise ValueError('revision log differs from actual changes')
    return actual


def revise(base, changes, allowed, request):
    require_valid(base)
    if len(base['cards'])!=1: raise ValueError('revise one card at a time')
    if not isinstance(changes,dict) or not changes: raise ValueError('changes must be nonempty object')
    if not isinstance(allowed,list) or not allowed or any(k not in FIELDS for k in allowed):
        raise ValueError('allowed must contain known exact field paths')
    if not set(changes)<=set(allowed): raise ValueError('patch exceeds allowed fields')
    if not isinstance(request,str) or not request.strip(): raise ValueError('current request is required')
    out=deepcopy(base)
    out['request']={'text':request,'mode':'edit','deliverable':'text','image_authorized':False}
    cells=out['cards'][0]['fields']; before=base['cards'][0]['fields']
    for k,v in changes.items(): cells[k]=deepcopy(v)
    out['revision']={'base_sha256':digest(base),'allowed':allowed,
                     'changes':{k:{'before':before.get(k),'after':cells[k]} for k in sorted(changes)
                                if before.get(k)!=cells[k]}}
    require_valid(out); compare(base,out)
    return out
