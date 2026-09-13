import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from casebook import case_markdown, full_casebook, delivery_preview, credited_totals
from streamlit.testing.v1 import AppTest

CONTENT = json.loads((ROOT/'portfolio_content.json').read_text(encoding='utf-8-sig'))


class CasebookTests(unittest.TestCase):
    def test_all_cases_have_reader_story_and_explicit_status(self):
        ids = [p['id'] for p in CONTENT['projects']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),14)
        for p in CONTENT['projects']:
            with self.subTest(case=p['id']):
                for field in ['status','audience','problem','before','after','role','evidence','limitation']:
                    self.assertTrue(p[field].strip())
                self.assertGreaterEqual(len(p['connections']),3)
                self.assertEqual(len(p['scenarios']),3)
                self.assertIn('?case='+p['id'],case_markdown(p))
        self.assertIn('候選',next(p for p in CONTENT['projects'] if p['id']=='rfc')['status'])

    def test_export_matches_the_website_source(self):
        self.assertEqual((ROOT/'CASEBOOK.md').read_text(encoding='utf-8'),full_casebook(CONTENT))

    def test_failed_source_never_continues_to_send(self):
        rows=delivery_preview('來源檢核')
        self.assertEqual([r['示範結果'] for r in rows],['通過','失敗','未執行','未執行','未執行'])
        rows=delivery_preview('寄送')
        self.assertEqual([r['示範結果'] for r in rows],['通過']*4+['失敗'])

    def test_order_excess_cannot_hide_other_shortfall(self):
        totals=credited_totals([(10,15),(10,5)])
        self.assertEqual(totals,dict(planned=20,actual=20,credited=15,remaining=5,excess=5))
        for a in [0,5,10,15,20]:
            for b in [0,5,10,15,20]:
                t=credited_totals([(10,a),(10,b)])
                self.assertEqual(t['credited']+t['remaining'],t['planned'])
                self.assertEqual(t['credited']+t['excess'],t['actual'])

    def test_deep_link_and_failure_interaction_do_not_connect_to_company(self):
        with patch.object(socket,'create_connection',side_effect=AssertionError('No network')):
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20)
            app.query_params['case']='n8n'
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.radio(key='page').value,'3～5 分鐘看作品')
            self.assertEqual(app.selectbox(key='case').value,'n8n')
            app.radio(key='failure_n8n').set_value('來源檢核').run()
            self.assertTrue(app.warning)
            app.selectbox(key='case').set_value('bi').run()
            self.assertEqual(app.query_params['case'],['bi'])
            app.slider(key='bi_a').set_value(10).run()
            self.assertFalse(app.exception)

    def test_case_demo_navigation_and_unknown_link(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20)
        app.query_params['case']='counter'
        app.run()
        app.button(key='try_counter').click().run()
        self.assertEqual(app.radio(key='page').value,'互動體驗')
        app.button(key='counter_plus').click().run()
        self.assertEqual(app.session_state.counter.completed,1)
        self.assertNotIn('case',app.query_params)
        fresh=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20)
        fresh.query_params['case']='unknown'
        fresh.run()
        self.assertFalse(fresh.exception)
        self.assertEqual(fresh.radio(key='page').value,'作品總覽')


if __name__=='__main__':
    unittest.main()
