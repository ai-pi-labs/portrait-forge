#!/usr/bin/env python3
"""Generate a closed JSON Schema from the runtime field catalog (no dependencies)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'skill/portrait-forge/assets/fields.json').read_text(encoding='utf-8'))
def obj(props,required=None):return {'type':'object','additionalProperties':False,'properties':props,'required':list(props) if required is None else required}
def enum(*values):return {'enum':list(values)}
def generate():
    text={'type':'string','minLength':1,'pattern':'\\S'}
    cells={};lockprops={}
    for k,s in CAT['fields'].items():
        value=enum(*s['values']) if 'values' in s else text
        lockprops[k]={'anyOf':[value,{'type':'null'}]}
        cells[k]={'oneOf':[obj({'value':value,'status':enum('designed'),'evidence':{'type':'string'}}),obj({'value':value,'status':enum('observed','inferred'),'evidence':text}),obj({'value':{'type':'null'},'status':enum('unknown'),'evidence':{'type':'string'}})]}
    locks=obj(lockprops,[])
    field_object=obj(cells,[]);field_object['minProperties']=1
    card=obj({'id':text,'intent':text,'fields':field_object,'locks':locks,'assumptions':{'type':'array','items':text}})
    result=obj({'schema_version':{'type':'integer','const':1},'request':obj({'text':text,'mode':enum('create','edit','roster','reference'),'deliverable':enum('text','image'),'image_authorized':{'type':'boolean'}}),'policy':obj({'locks':locks,'same_makeup':{'type':'boolean'},'distinct':{'type':'boolean'},'min_groups':{'type':'integer','minimum':1,'maximum':6},'min_core':{'type':'integer','minimum':1,'maximum':3}}),'cards':{'type':'array','minItems':1,'items':card},'revision':obj({'base_sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'},'allowed':{'type':'array','items':enum(*cells)},'changes':{'type':'object'}})},['schema_version','request','policy','cards'])
    result.update({'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Portrait Forge plan v1','description':'Shape schema only; runtime validates mode requirements, locks, revisions, and cross-card constraints.'})
    return result
if __name__=='__main__':(ROOT/'skill/portrait-forge/assets/plan.schema.json').write_text(json.dumps(generate(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
