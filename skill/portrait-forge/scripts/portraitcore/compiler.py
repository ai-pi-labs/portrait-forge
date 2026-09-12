"""Deterministic, lossless compilation of confirmed fields; no image API side effects."""
from .contracts import CATALOG, FIELDS, digest, known
from .revisions import compare, require_valid


def compile_plan(plan, baseline=None):
    require_valid(plan)
    if plan['request']['mode']=='edit':
        if baseline is None: raise ValueError('edit compilation requires --baseline')
        compare(baseline,plan)
    outputs=[]
    for card in plan['cards']:
        lines=[]; trace=[]
        for section,title in CATALOG['sections'].items():
            clauses=[]
            for key,spec in FIELDS.items():
                cell=card['fields'].get(key)
                if spec['section']!=section or not cell or not known(cell): continue
                value=spec.get('values',{}).get(cell['value'],cell['value'])
                clause=spec['label']+'：'+value
                clauses.append(clause)
                trace.append({'field':key,'section':section,'text':clause,'status':cell['status']})
            if clauses: lines.append(title+'｜'+'；'.join(clauses)+'。')
        outputs.append({'id':card['id'],'prompt':'\n'.join(lines),'trace':trace,
                        'omitted':[k for k,c in card['fields'].items() if not known(c)]})
    return {'schema_version':1,'source_sha256':digest(plan),'outputs':outputs,
            'kind':'observation_summary' if plan['request']['mode']=='reference' else 'prompt',
            'image_generated':False}
