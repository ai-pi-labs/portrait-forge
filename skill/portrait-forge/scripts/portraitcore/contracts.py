"""Closed data contracts. No prompt execution, image loading, or network access."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = json.loads((ROOT / 'assets/fields.json').read_text(encoding='utf-8'))
FIELDS = CATALOG['fields']
STATUSES = ('designed', 'observed', 'inferred', 'unknown')


def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate key: ' + key)
        out[key] = value
    return out


def load(path):
    def invalid(value):
        raise ValueError('nonfinite JSON number: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=invalid)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def known(cell):
    return cell.get('status') in ('designed', 'observed')


def validate(plan):
    errors, warnings, pairs = [], [], []
    def err(path, message):
        errors.append({'path': path, 'message': message})
    def obj(value, keys, required, path):
        if not isinstance(value, dict):
            err(path, 'must be an object'); return False
        for key in sorted(set(value) - set(keys)):
            err(path + '.' + key, 'unknown field')
        for key in sorted(set(required) - set(value)):
            err(path + '.' + key, 'required')
        return True
    def string(value, path):
        if not isinstance(value, str) or not value.strip():
            err(path, 'must be a nonempty string'); return False
        return True
    def strings(value, path):
        if not isinstance(value, list):
            err(path, 'must be an array'); return False
        for i, v in enumerate(value): string(v, path + '.' + str(i))
        return True
    def field_value(key, value, path, nullable=False):
        if value is None and nullable: return
        if not string(value, path): return
        values = FIELDS[key].get('values')
        if values and value not in values: err(path, 'invalid canonical value')
    def field_map(value, path):
        if not isinstance(value, dict): err(path, 'must be an object'); return
        for k, v in value.items():
            if k not in FIELDS: err(path + '.' + k, 'unknown field path')
            else: field_value(k, v, path + '.' + k, True)
    if not obj(plan, ('schema_version','request','policy','cards','revision'),
               ('schema_version','request','policy','cards'), '$'):
        return {'status':'FAIL','errors':errors,'warnings':warnings,'pairs':pairs}
    if type(plan.get('schema_version')) is not int or plan['schema_version'] != 1:
        err('schema_version','only version 1 is supported')
    req = plan.get('request', {})
    if obj(req, ('text','mode','deliverable','image_authorized'),
           ('text','mode','deliverable','image_authorized'),'request'):
        string(req.get('text'),'request.text')
        if req.get('mode') not in ('create','edit','roster','reference'): err('request.mode','invalid mode')
        if req.get('deliverable') not in ('text','image'): err('request.deliverable','invalid deliverable')
        if type(req.get('image_authorized')) is not bool: err('request.image_authorized','must be boolean')
        if req.get('deliverable') == 'image' and req.get('image_authorized') is not True:
            err('request.image_authorized','image request has not been recorded')
    else: req = {}
    policy = plan.get('policy', {})
    if obj(policy, ('locks','same_makeup','distinct','min_groups','min_core'),
           ('locks','same_makeup','distinct','min_groups','min_core'),'policy'):
        field_map(policy.get('locks'),'policy.locks')
        for key in ('same_makeup','distinct'):
            if type(policy.get(key)) is not bool: err('policy.'+key,'must be boolean')
        for key, maximum in (('min_groups',6),('min_core',3)):
            if type(policy.get(key)) is not int or not 1 <= policy[key] <= maximum:
                err('policy.'+key,'out of range')
        if type(policy.get('min_core')) is int and type(policy.get('min_groups')) is int:
            if policy['min_core'] > policy['min_groups']: err('policy.min_core','cannot exceed min_groups')
    else: policy = {}
    cards = plan.get('cards')
    if not isinstance(cards,list) or not cards:
        err('cards','must be a nonempty array'); cards=[]
    if req.get('mode') in ('create','edit','reference') and len(cards)!=1:
        err('cards','this mode requires one card')
    if req.get('mode')=='roster' and len(cards)<2: err('cards','roster requires at least two cards')
    if policy.get('distinct') is True and len(cards)<2: err('policy.distinct','requires at least two cards')
    ids=set()
    for i,card in enumerate(cards):
        p='cards.'+str(i)
        if not obj(card, ('id','intent','fields','locks','assumptions'),
                   ('id','intent','fields','locks','assumptions'),p): continue
        if string(card.get('id'),p+'.id'):
            if card['id'] in ids: err(p+'.id','duplicate id')
            ids.add(card['id'])
        string(card.get('intent'),p+'.intent')
        strings(card.get('assumptions'),p+'.assumptions')
        field_map(card.get('locks'),p+'.locks')
        cells=card.get('fields')
        if not isinstance(cells,dict): err(p+'.fields','must be an object'); continue
        if not cells: err(p+'.fields','must contain at least one field')
        for k,cell in cells.items():
            cp=p+'.fields.'+k
            if k not in FIELDS: err(cp,'unknown field path'); continue
            if not obj(cell, ('value','status','evidence'),('value','status','evidence'),cp): continue
            status=cell.get('status')
            if status not in STATUSES: err(cp+'.status','invalid status')
            if status=='unknown':
                if cell.get('value') is not None: err(cp+'.value','unknown requires null')
            else: field_value(k,cell.get('value'),cp+'.value')
            if not isinstance(cell.get('evidence'),str): err(cp+'.evidence','must be string')
            if status in ('observed','inferred') and not cell.get('evidence'):
                err(cp+'.evidence','observation requires source and visible basis')
            if status=='inferred': warnings.append(cp+': inference omitted from prompt')
            if req.get('mode')=='reference' and status=='designed':
                err(cp,'reference analysis cannot mix invention with observation; create a separate design')
        if req.get('mode') in ('create','roster'):
            for k,spec in FIELDS.items():
                if spec['required_create'] and (not isinstance(cells.get(k),dict) or not known(cells[k])):
                    err(p+'.fields.'+k,'known design value required for create/roster')
        locks={}
        for source in (policy.get('locks'),card.get('locks')):
            if not isinstance(source,dict): continue
            for k,v in source.items():
                if k in locks and locks[k]!=v: err(p+'.locks.'+k,'local/global conflict')
                locks[k]=v
                cell=cells.get(k)
                if not isinstance(cell,dict) or cell.get('value')!=v or (v is not None and not known(cell)):
                    err(p+'.fields.'+k,'lock violated or unconfirmed')
    revision=plan.get('revision')
    if req.get('mode')=='edit' and revision is None: err('revision','edit requires baseline verification')
    if revision is not None:
        if obj(revision, ('base_sha256','allowed','changes'),('base_sha256','allowed','changes'),'revision'):
            d=revision.get('base_sha256')
            if not isinstance(d,str) or len(d)!=64 or any(c not in '0123456789abcdef' for c in d):
                err('revision.base_sha256','invalid digest')
            if strings(revision.get('allowed'),'revision.allowed'):
                for key in revision['allowed']:
                    if key not in FIELDS: err('revision.allowed','unknown field path: '+str(key))
            if not isinstance(revision.get('changes'),dict): err('revision.changes','must be object')
    # Relational checks run only after shape validation, to avoid malformed-input crashes.
    if not errors:
        for a,b in itertools.combinations(cards,2):
            if policy['same_makeup']:
                for k,spec in FIELDS.items():
                    if spec['section']=='makeup':
                        ca,cb=a['fields'].get(k),b['fields'].get(k)
                        if not ca or not cb or not known(ca) or not known(cb) or ca['value']!=cb['value']:
                            err('cards',a['id']+'/'+b['id']+': makeup differs at '+k)
            if policy['distinct']:
                groups=sorted({FIELDS[k]['group'] for k in set(a['fields'])&set(b['fields'])
                               if 'group' in FIELDS[k] and known(a['fields'][k]) and known(b['fields'][k])
                               and a['fields'][k]['value']!=b['fields'][k]['value']})
                core=sorted(set(groups)&{'face','eyes','nose'})
                pairs.append({'a':a['id'],'b':b['id'],'groups':groups,'core':core})
                if len(groups)<policy['min_groups'] or len(core)<policy['min_core']:
                    err('cards',a['id']+'/'+b['id']+': insufficient structural diversity')
    return {'status':'FAIL' if errors else 'PASS','errors':errors,'warnings':warnings,'pairs':pairs,
            'scope':'encoded design only; request semantics, likeness and images require human/agent review'}
