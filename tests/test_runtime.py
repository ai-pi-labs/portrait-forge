import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skill/portrait-forge'
sys.path.insert(0,str(SKILL/'scripts'))
from portraitcore.contracts import load,validate,FIELDS,digest
from portraitcore.compiler import compile_plan
from portraitcore.revisions import revise,compare

def example(name='01-original'):return load(ROOT/'examples'/(name+'.json'))
def cell(value):return {'value':value,'status':'designed','evidence':'test'}
def tool(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class RuntimeTests(unittest.TestCase):
    def test_create_and_every_confirmed_field_compiles(self):
        p=example();r=compile_plan(p)
        self.assertEqual(r['source_sha256'],digest(p))
        self.assertEqual({t['field'] for t in r['outputs'][0]['trace']},set(p['cards'][0]['fields']))
        for t in r['outputs'][0]['trace']:self.assertIn(t['text'],r['outputs'][0]['prompt'])
    def test_stable_despite_json_key_order(self):
        p=example();q=copy.deepcopy(p);q['cards'][0]['fields']=dict(reversed(list(q['cards'][0]['fields'].items())))
        self.assertEqual(compile_plan(p),compile_plan(q))
    def test_roster_all_ten_pairs(self):
        r=validate(example('03-roster'));self.assertEqual(r['status'],'PASS');self.assertEqual(len(r['pairs']),10)
    def test_repeated_faces_fail_even_with_different_styling(self):
        p=example('03-roster');p['cards'][4]['fields']=copy.deepcopy(p['cards'][3]['fields']);p['cards'][4]['fields']['styling.hair']=cell('红色长发')
        self.assertEqual(validate(p)['status'],'FAIL')
        self.assertTrue(any('cast-4/cast-5' in e['message'] for e in validate(p)['errors']))
    def test_one_group_cannot_count_as_several(self):
        p=example('03-roster');p['cards']=p['cards'][:2]
        a,b=p['cards'];b['fields']=copy.deepcopy(a['fields'])
        for k,s in FIELDS.items():
            if s.get('group')=='eyes':b['fields'][k]=cell(list(s['values'])[1])
        r=validate(p);self.assertEqual(r['pairs'][0]['groups'],['eyes']);self.assertEqual(r['status'],'FAIL')
    def test_same_makeup_lip_finish_detected(self):
        p=example('03-roster');p['cards'][1]['fields']['makeup.lip_finish']=cell('镜面')
        self.assertEqual(validate(p)['status'],'FAIL')
    def test_locks_apply_across_every_domain(self):
        for k in ('bone.brow','skin.tone','makeup.lip_color','photo.light','styling.hair'):
            with self.subTest(k=k):
                p=example();p['policy']['locks'][k]=p['cards'][0]['fields'][k]['value']
                p['cards'][0]['fields'][k]=cell('changed')
                self.assertEqual(validate(p)['status'],'FAIL')
    def test_local_global_conflict(self):
        p=example();p['policy']['locks']['face.ratio']='long';self.assertEqual(validate(p)['status'],'FAIL')
    def test_reference_unknown_and_inference_not_prompted(self):
        p=example('04-reference');p['cards'][0]['fields']['bone.orbit']={'value':'deep','status':'inferred','evidence':'shadow only'}
        o=compile_plan(p)['outputs'][0];self.assertNotIn('眼窝',o['prompt']);self.assertIn('bone.orbit',o['omitted'])
    def test_reference_invention_rejected(self):
        p=example('04-reference');p['cards'][0]['fields']['bone.orbit']=cell('deep');self.assertEqual(validate(p)['status'],'FAIL')
    def test_exact_revision_and_original_unchanged(self):
        p=example();h=digest(p);q=revise(p,{'makeup.lip_color':cell('酒红')},['makeup.lip_color'],'只改唇色')
        self.assertEqual(digest(p),h);self.assertEqual(set(compare(p,q)),{'makeup.lip_color'})
        self.assertEqual(len(compile_plan(q,p)['outputs']),1)
    def test_wrong_baseline_refused(self):
        p=example();q=example('02-edited');p['cards'][0]['fields']['photo.light']=cell('new light')
        with self.assertRaises(ValueError):compile_plan(q,p)
    def test_edit_without_baseline_refused(self):
        with self.assertRaises(ValueError):compile_plan(example('02-edited'))
    def test_unauthorized_path_refused(self):
        with self.assertRaises(ValueError):revise(example(),{'photo.light':cell('new')},['makeup.lip_color'],'改唇色')
    def test_tampered_revision_detected(self):
        p=example();q=example('02-edited');q['cards'][0]['fields']['photo.light']=cell('new')
        with self.assertRaises(ValueError):compare(p,q)
    def test_log_tampering_detected(self):
        q=example('02-edited');q['revision']['changes']={}
        with self.assertRaises(ValueError):compare(example(),q)
    def test_locked_unknown_preserved(self):
        p=example('05-partial-baseline');q=example('06-partial-edited');compare(p,q)
        self.assertEqual(p['cards'][0]['fields']['bone.orbit'],q['cards'][0]['fields']['bone.orbit'])
        self.assertNotIn('nose.width',q['cards'][0]['fields'])
        with self.assertRaises(ValueError):revise(p,{'bone.orbit':cell('deep')},['bone.orbit'],'补充')
    def test_image_mode_requires_record_but_compiler_never_generates(self):
        p=example();p['request']['deliverable']='image';self.assertEqual(validate(p)['status'],'FAIL')
        p['request']['image_authorized']=True;self.assertFalse(compile_plan(p)['image_generated'])
    def test_missing_required_original(self):
        p=example();del p['cards'][0]['fields']['bone.orbit'];self.assertEqual(validate(p)['status'],'FAIL')
    def test_duplicate_ids(self):
        p=example('03-roster');p['cards'][1]['id']=p['cards'][0]['id'];self.assertEqual(validate(p)['status'],'FAIL')
    def test_empty_reference_rejected(self):
        p=example('04-reference');p['cards'][0]['fields']={};self.assertEqual(validate(p)['status'],'FAIL')
    def test_unknown_key_rejected(self):
        p=example();p['cards'][0]['fields']['face.rato']=cell('short');self.assertEqual(validate(p)['status'],'FAIL')
    def test_malformed_inputs_do_not_crash(self):
        bad=[None,[],True,1,'text',{}, {'cards':[None]}]
        for v in bad:self.assertEqual(validate(v)['status'],'FAIL')
        for path in ('request','policy','cards'):
            for v in bad:
                p=example();p[path]=v;self.assertEqual(validate(p)['status'],'FAIL')
        for key in ('id','intent','fields','locks','assumptions'):
            p=example();p['cards'][0][key]=None;self.assertEqual(validate(p)['status'],'FAIL')
    def test_duplicate_keys_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'
            for text in ('{"a":1,"a":2}','{"a":NaN}'):
                p.write_text(text)
                with self.assertRaises(ValueError):load(p)
    def test_cli_error_exit_json(self):
        r=subprocess.run([sys.executable,str(SKILL/'scripts/portrait.py'),'validate','/no/such/input.json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,1);self.assertEqual(json.loads(r.stdout)['status'],'FAIL');self.assertNotIn('Traceback',r.stderr)
    def test_cli_compile_from_other_directory(self):
        r=subprocess.run([sys.executable,str(SKILL/'scripts/portrait.py'),'compile',str(ROOT/'examples/01-original.json')],cwd=tempfile.gettempdir(),capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout);self.assertEqual(len(json.loads(r.stdout)['outputs']),1)
    def test_cli_edit_validate_requires_baseline(self):
        r=subprocess.run([sys.executable,str(SKILL/'scripts/portrait.py'),'validate',str(ROOT/'examples/02-edited.json')],capture_output=True,text=True)
        self.assertEqual(r.returncode,1)
    def test_install_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            t=tool('install').install(d);self.assertTrue((t/'SKILL.md').exists())
            r=subprocess.run([sys.executable,str(t/'scripts/portrait.py'),'compile',str(ROOT/'examples/01-original.json')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout)
            with self.assertRaises(ValueError):tool('install').install(d)
    def test_work_export_contains_all_reference_rules(self):
        with tempfile.TemporaryDirectory() as d:
            out=tool('export_work').export(Path(d)/'pack');data=(out/'portrait-forge-knowledge.md').read_text()
            for p in (SKILL/'references').glob('*.md'):self.assertIn(p.name,data)
            with self.assertRaises(ValueError):tool('export_work').export(out)
    def test_generated_schema_fresh(self):
        self.assertEqual(tool('schema').generate(),load(SKILL/'assets/plan.schema.json'))
    def test_all_example_outputs_current(self):
        for name,base in [('01-original',None),('02-edited','01-original'),('03-roster',None),('04-reference',None),('06-partial-edited','05-partial-baseline')]:
            result=compile_plan(example(name),example(base) if base else None)
            self.assertEqual(result,load(ROOT/'examples/compiled'/(name+'.json')))

if __name__=='__main__':unittest.main()
