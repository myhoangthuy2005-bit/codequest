"""Controller and real HTTP tests; do not require a graphical display."""
import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from academy import ProfileStore
from questions import TOPICS,QUESTIONS
from server import BrowserGame, make_server

class WebFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'profiles.json'
        self.store=ProfileStore(self.path);self.g=BrowserGame(self.store)
    def tearDown(self):self.tmp.cleanup()
    def win(self):self.g.submit(list(self.g.round.correct),'')
    def lose(self):self.g.submit(list(set(range(6))-self.g.round.correct),'')
    def test_answers_hidden_until_submission(self):
        self.g.start({'mode':'practice','topics':['Arithmetic']});s=self.g.state()
        self.assertTrue(all('output' not in c and 'match' not in c for c in s['cards']))
        self.win();self.assertTrue(all('output' in c for c in self.g.state()['cards']))
        self.assertEqual(self.g.score,100);self.assertEqual(self.g.profile['coins'],10)
    def test_three_lives_and_durable_progress(self):
        self.g.start({'mode':'mixed'})
        for i in range(3):self.lose();self.g.next()
        self.assertEqual(self.g.page,'summary');self.assertEqual(self.g.lives,0)
        self.assertEqual(len(ProfileStore(self.path).active['results']),3)
    def test_duel_equal_turns_and_two_summaries(self):
        second=self.store.create('Friend');ids=[self.store.active_id,second]
        self.g.start({'mode':'duel','players':ids,'rounds':5})
        for i in range(3):
            for j in range(2):
                self.g.action({'action':'ready'});self.lose()
                if j==0 and i==2:self.assertFalse(self.g.duel.finished)
                self.g.next()
        self.assertTrue(self.g.duel.finished);self.assertIsNone(self.g.duel.winner)
        self.assertEqual(self.g.page,'summary');self.assertEqual(self.g.summary_index,0)
        self.g.action({'action':'summary_next'});self.assertEqual(self.g.summary_index,1)
        self.assertEqual([len(self.store.profiles[i]['results']) for i in ids],[3,3])
    def test_daily_completes_and_replays_do_not_farm(self):
        for replay in range(2):
            self.g.start({'mode':'daily'})
            for i in range(5):self.win();self.g.next()
            self.assertEqual(self.g.page,'summary');self.assertEqual(self.g.score,500)
            self.assertEqual(self.g.profile['coins'],50)
        self.assertTrue(self.g.profile['daily'][self.g.day]['completed'])
    def test_topic_changes_preserve_session_lives_and_score(self):
        self.g.start({'mode':'practice','topics':['Arithmetic']});self.win();self.g.next()
        self.lose();self.g.action({'action':'change_topic','topic':'Slicing'})
        self.assertEqual((self.g.score,self.g.lives,len(self.g.results)),(100,2,2))
        self.assertEqual(self.g.round.question.topic,'Slicing')
    def test_lab_and_tutorial(self):
        self.g.start({'mode':'lab'});self.g.submit([],self.g.round.question.example)
        self.assertTrue(self.g.last_result['won'])
        before=len(self.g.profile['results']);coins=self.g.profile['coins']
        self.g.start({'mode':'tutorial'});self.lose()
        self.assertEqual((len(self.g.profile['results']),self.g.profile['coins'],self.g.lives),(before,coins,3))
    def test_timer_is_server_side_and_pause_works(self):
        self.g.profile['settings']['timer']=45;self.g.start({'mode':'mixed'})
        self.g.action({'action':'pause','paused':True});self.g.last-=200
        self.g.update_clock();self.assertGreater(self.g.remaining,40)
        self.g.action({'action':'pause','paused':False});self.g.last-=200;self.g.update_clock()
        self.assertEqual(self.g.page,'review');self.assertTrue(self.g.last_result['timed_out'])
        self.assertEqual(self.g.lives,2)
    def test_profile_switch_settings_and_invalid_requests(self):
        self.g.action({'action':'create_profile','name':'Friend'})
        self.assertEqual(self.g.profile['name'],'Friend');self.assertEqual(self.store.active_id,self.g.pid)
        self.g.action({'action':'settings','key':'music','value':True})
        self.assertTrue(ProfileStore(self.path).active['settings']['music'])
        with self.assertRaises(ValueError):self.g.action({'action':'settings','key':'timer','value':-1})
        self.g.start({'mode':'mixed'})
        with self.assertRaises(ValueError):self.g.action({'action':'hint','selected':['bad'],'kind':'count'})

class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.server=make_server(0,Path(self.tmp.name)/'profiles.json')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_port;self.cookie=''
    def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def call(self,path,body=None,origin=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port);headers={}
        if self.cookie:headers['Cookie']=self.cookie
        if origin:headers['Origin']=origin
        if body is not None:headers['Content-Type']='application/json'
        c.request('POST' if body is not None else 'GET',path,json.dumps(body) if body is not None else None,headers)
        r=c.getresponse();payload=r.read();cookie=r.getheader('Set-Cookie')
        if cookie:self.cookie=cookie.split(';')[0]
        status=r.status;c.close();return status,payload
    def test_http_session_game_and_download(self):
        status,body=self.call('/');self.assertEqual(status,200);self.assertIn(b'CodeQuest',body)
        status,body=self.call('/api/state');self.assertEqual(status,200);self.assertTrue(self.cookie)
        status,body=self.call('/api/action',{'action':'start','mode':'mixed'});state=json.loads(body)
        self.assertEqual(state['page'],'game');self.assertNotIn('output',state['cards'][0])
        status,body=self.call('/api/export.txt');self.assertEqual(status,200);self.assertIn(b'PROGRESS REPORT',body)
        self.assertEqual(self.call('/api/action',{'action':'state'},'https://other.example')[0],403)
        self.assertEqual(self.call('/../server.py')[0],404)
    def test_independent_browser_sessions(self):
        self.call('/api/state');first=self.cookie
        self.call('/api/action',{'action':'start','mode':'mixed'});self.cookie=''
        _,body=self.call('/api/state');self.assertEqual(json.loads(body)['page'],'menu')
        self.assertNotEqual(self.cookie,first)

if __name__=='__main__':unittest.main()
