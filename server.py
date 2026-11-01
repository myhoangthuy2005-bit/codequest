"""CodeQuest browser app. Python owns rules, scoring, timers and persistent profiles.

Run: python3 server.py, then open http://127.0.0.1:8000.
No external Python dependencies. Intended for local use on a trusted computer.
"""
import argparse
import ast
import json
import mimetypes
import os
import random
import secrets
import tempfile
import time
from dataclasses import asdict
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from urllib.parse import urlparse

from academy import (ProfileStore, THEMES, badge_progress, daily_questions,
                     export_report, local_day, mistake_rows, recommended_level)
from expression_lab import LabRound, TASKS
from game import Duel, Round
from lessons import LESSONS
from questions import QUESTIONS, TOPICS, STUDY_TIPS
from statistics import Statistics

ROOT = Path(__file__).parent

class BrowserGame:
    """One browser session; completed results are persisted separately per profile."""
    def __init__(self, store):
        self.store=store; self.pid=store.active_id; self.page='menu'; self.mode='mixed'
        self.round=None; self.duel=None; self.duel_ids=[]; self.summary_index=0
        self.score=0; self.lives=3; self.results=[]; self.seen=set(); self.pool=QUESTIONS
        self.message=''; self.paused=False; self.remaining=0; self.last=time.monotonic()
        self.challenge=[]; self.day=''; self.last_result=None

    @property
    def profile(self): return self.store.profiles[self.pid]

    def update_clock(self):
        now=time.monotonic()
        if self.page=='game' and not self.paused and self.remaining>0:
            self.remaining=max(0,self.remaining-(now-self.last))
            if self.remaining==0: self.submit([], '', True)
        self.last=now

    def new_round(self, question=None):
        if self.duel:
            question=self.duel.question; self.score=self.duel.active['score']; self.lives=self.duel.active['lives']
        if question is None:
            pool=self.pool
            if self.mode=='daily':question=self.challenge[len(self.results)]
            else:
                if self.mode=='progressive':
                    level=recommended_level(self.profile['results']);pool=[q for q in pool if q.difficulty==level]
                unseen=[q for q in pool if q.id not in self.seen];question=random.choice(unseen or pool)
        self.seen.add(question.id)
        self.round=LabRound(question) if self.mode=='lab' else Round(question)
        self.remaining=0 if self.mode=='tutorial' else self.profile['settings']['timer']
        self.last=time.monotonic();self.paused=False;self.page='game';self.message=''

    def start(self,data):
        mode=data.get('mode','mixed')
        if mode not in ('mixed','practice','progressive','daily','lab','tutorial','duel'):raise ValueError('Unknown mode.')
        self.mode=mode;self.score=0;self.lives=3;self.results=[];self.seen=set();self.duel=None;self.last_result=None
        pid=data.get('profile_id')
        if pid is not None:
            if pid not in self.store.profiles:raise ValueError('Unknown profile.')
            self.pid=pid
        if mode=='duel':
            ids=data.get('players',[])
            if len(ids)!=2 or len(set(ids))!=2 or any(i not in self.store.profiles for i in ids):raise ValueError('Choose two different profiles.')
            length=data.get('rounds',5)
            if length not in (5,15,len(QUESTIONS)):raise ValueError('Choose 5, 15 or 54 rounds.')
            self.duel_ids=ids;self.duel=Duel(QUESTIONS,length)
            for i,pid in enumerate(ids):self.duel.players[i]['name']=self.store.profiles[pid]['name']
            self.page='handoff';self.remaining=0;return
        self.pool=TASKS if mode=='lab' else QUESTIONS
        topics=data.get('topics',[])
        if topics:
            self.pool=[q for q in self.pool if q.topic in topics]
            if not self.pool:raise ValueError('Unknown topic.')
        if mode=='daily':self.day=local_day();self.challenge=daily_questions(QUESTIONS,self.day)
        self.new_round()

    def submit(self, selected, answer, timed_out=False):
        if self.page!='game' or not self.round or self.round.submitted:raise ValueError('This round is not awaiting an answer.')
        if self.paused and not timed_out:raise ValueError('Resume before submitting.')
        if self.mode=='lab':won,points=self.round.submit(answer,timed_out)
        else:
            if not isinstance(selected,list) or any(type(i) is not int or i<0 or i>=len(self.round.cards) for i in selected):raise ValueError('Invalid card selection.')
            self.round.selected=set(selected)-self.round.eliminated;won,points=self.round.submit(timed_out)
        q=self.round.question
        if self.mode=='tutorial':points=0
        mistakes=mistake_rows(self.round) if self.mode!='lab' else []
        if self.mode=='lab' and not won:
            mistakes=[dict(kind='Expression answer',code=answer,output=self.round.actual,target=q.target,explanation=self.round.error or 'Example answer: '+q.example,concept=q.topic)]
        if timed_out:mistakes.insert(0,dict(kind='Time ran out',code='',output='No completed submission',target=q.target,explanation='Try untimed practice first, then build speed.',concept='Time management'))
        row=dict(topic=q.topic,question_id=q.id,difficulty=q.difficulty,won=won,points=points,
                 mode=self.mode,timed_out=timed_out,mistakes=mistakes,tutorial=self.mode=='tutorial',
                 missed=0 if self.mode=='lab' else len(self.round.correct-self.round.selected),
                 incorrect=0 if self.mode=='lab' else len(self.round.selected-self.round.correct))
        pid=self.duel_ids[self.duel.turn] if self.duel else self.pid
        if self.mode=='tutorial':self.profile['tutorial_done']=True;self.store.save()
        else:
            if self.mode=='daily':row['date']=self.day
            self.store.record(pid,row)
        if self.duel:
            self.duel.record(row);self.score=self.duel.active['score'];self.lives=self.duel.active['lives']
        elif self.mode!='tutorial':self.score+=points;self.lives-=not won
        self.results.append(row);self.last_result=row;self.page='review';self.remaining=0;self.paused=False
        if self.mode=='daily':self.store.complete_daily(self.pid,self.day,self.score,len(self.results)==5)

    def next(self):
        if self.page!='review':raise ValueError('Review the current round first.')
        if self.duel:
            if self.duel.finished:self.end();return
            self.duel.advance();self.page='handoff';return
        if self.mode=='tutorial':self.page='menu';return
        if self.lives<=0 or (self.mode=='daily' and len(self.results)>=5):self.end();return
        self.new_round()

    def end(self):
        self.remaining=0;self.paused=False;self.summary_index=0
        self.page='summary' if self.results else 'menu'

    def summary(self, rows):
        good,practice=Statistics.feedback(rows)
        return dict(rounds=len(rows),wins=sum(r['won'] for r in rows),losses=sum(not r['won'] for r in rows),
                    points=sum(r['points'] for r in rows),strengths=good,practice=practice,
                    topics=[dict(topic=q.topic,wins=sum(r['won'] for r in rows if r['topic']==q.topic),
                                 played=sum(r['topic']==q.topic for r in rows)) for q in TOPICS])

    def state(self):
        self.update_clock();p=self.profile
        out=dict(page=self.page,mode=self.mode,profile_id=self.pid,profile=p,profiles=[dict(id=i,name=x['name']) for i,x in self.store.profiles.items()],
                 themes=THEMES,lessons=LESSONS,topics=[dict(topic=q.topic,difficulty=q.difficulty) for q in TOPICS],
                 badges=badge_progress(p['results']),summary=self.summary(p['results']),message=self.message,
                 warning=self.store.warning,score=self.score,lives=self.lives,remaining=self.remaining,paused=self.paused,
                 challenge_index=len(self.results)+1,tutorial_needed=not p['tutorial_done'],daily=p['daily'].get(local_day(),{}),day=local_day(),
                 last_result=self.last_result)
        if self.duel:
            out['duel']=dict(players=self.duel.players,turn=self.duel.turn,number=self.duel.round_number,total=self.duel.total_rounds,
                             finished=self.duel.finished,result=self.duel.result_message,summary_index=self.summary_index,profile_ids=self.duel_ids)
        if self.page=='summary':
            rows=self.duel.players[self.summary_index]['results'] if self.duel else self.results
            out['summary']=self.summary(rows)
        if self.page in ('game','review') and self.round:
            q=self.round.question
            out['question']=dict(id=q.id,topic=q.topic,difficulty=q.difficulty,target=q.target,type=type(ast.literal_eval(q.target)).__name__)
            if self.mode=='lab':
                out['question'].update(prompt=q.prompt,context=q.context,required=q.required)
                if self.round.submitted:out['question'].update(actual=self.round.actual,error=self.round.error,example=q.example)
            else:
                out['cards']=[dict(code=c.code,removed=i in self.round.eliminated,selected=i in self.round.selected,
                                  **(dict(output=c.output,explanation=c.explanation,concept=c.concept,match=i in self.round.correct) if self.round.submitted else {})) for i,c in enumerate(self.round.cards)]
            out['hints']=list(self.round.hints)
        return out

    def action(self,data):
        self.update_clock();action=data.get('action')
        if action=='start':self.start(data)
        elif action=='ready':
            if self.page!='handoff':raise ValueError('No handover is waiting.')
            self.new_round()
        elif action=='submit':self.submit(data.get('selected',[]),str(data.get('answer','')))
        elif action=='change_topic':
            if self.duel or self.page!='review' or self.lives<=0 or self.mode not in ('mixed','practice'):
                raise ValueError('Finish this session before changing its topic.')
            topic=data.get('topic');pool=[q for q in QUESTIONS if q.topic==topic]
            if not pool:raise ValueError('Unknown topic.')
            self.mode='practice';self.pool=pool;self.new_round()
        elif action=='next':self.next()
        elif action=='end':self.end()
        elif action=='summary_next':
            if self.page=='summary' and self.duel and self.summary_index==0:self.summary_index=1
            else:self.page='menu';self.duel=None
        elif action=='pause':
            if self.page=='game':self.paused=bool(data.get('paused'));self.last=time.monotonic()
        elif action=='hint':
            if self.page!='game':raise ValueError('Start a round first.')
            if self.mode!='lab':
                picks=data.get('selected',[])
                if not isinstance(picks,list) or any(type(i) is not int or not 0<=i<len(self.round.cards) for i in picks):raise ValueError('Invalid card selection.')
                self.round.selected=set(picks)-self.round.eliminated
            self.message=self.round.hint('concept' if self.mode=='lab' else data.get('kind','count'))
        elif action=='select_profile':
            pid=data.get('id')
            if pid not in self.store.profiles:raise ValueError('Unknown profile.')
            self.pid=pid;self.store.select(pid);self.page='menu';self.duel=None
        elif action=='create_profile':
            self.pid=self.store.create(str(data.get('name','')));self.store.select(self.pid);self.page='menu';self.duel=None
        elif action=='rename_profile':self.store.rename(self.pid,str(data.get('name','')))
        elif action=='settings':
            key=data.get('key');value=data.get('value')
            if key=='timer':
                if type(value) is not int or value not in (0,45,90):raise ValueError('Invalid timer.')
            elif key in ('sound','music','large_text','high_contrast','animations'):
                if type(value) is not bool:raise ValueError('Invalid setting.')
            else:raise ValueError('Unknown setting.')
            self.profile['settings'][key]=value;self.store.save()
        elif action=='purchase':self.store.purchase(self.pid,data.get('theme'))
        elif action=='tutorial_done':self.profile['tutorial_done']=True;self.store.save()
        elif action!='state':raise ValueError('Unknown action.')
        return self.state()

class WebApp:
    def __init__(self,path=None):self.store=ProfileStore(path);self.sessions={};self.lock=RLock()
    def session(self,key):
        with self.lock:
            if key not in self.sessions:
                if len(self.sessions)>=100:self.sessions.pop(next(iter(self.sessions)))
                key=secrets.token_urlsafe(32);self.sessions[key]=BrowserGame(self.store)
            return key,self.sessions[key]

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send_bytes(self,status,body,mime='application/json',cookie=None,download=None):
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store' if mime.startswith('application/json') else 'no-cache')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        if cookie:self.send_header('Set-Cookie',f'cq_session={cookie}; HttpOnly; SameSite=Strict; Path=/')
        if download:self.send_header('Content-Disposition','attachment; filename="codequest-report.'+download+'"')
        self.end_headers();self.wfile.write(body)
    def get_session(self):
        cookies=SimpleCookie()
        try:cookies.load(self.headers.get('Cookie',''))
        except Exception:pass
        key=cookies['cq_session'].value if 'cq_session' in cookies else ''
        return self.server.app.session(key)
    def do_GET(self):
        route=urlparse(self.path).path
        if route in ('/api/state','/api/export.txt','/api/export.csv'):
            key,game=self.get_session()
            with self.server.app.lock:
                if route=='/api/state':self.send_bytes(200,json.dumps(game.state()).encode(),cookie=key);return
                fmt=route.rsplit('.',1)[1]
                with tempfile.TemporaryDirectory() as folder:
                    path=Path(folder)/('report.'+fmt);export_report(path,game.profile,fmt)
                    self.send_bytes(200,path.read_bytes(),'text/plain; charset=utf-8' if fmt=='txt' else 'text/csv; charset=utf-8',key,fmt)
            return
        path=(ROOT/'static'/('index.html' if route=='/' else route.lstrip('/'))).resolve()
        if not path.is_relative_to((ROOT/'static').resolve()) or not path.is_file():self.send_bytes(404,b'Not found','text/plain');return
        self.send_bytes(200,path.read_bytes(),mimetypes.guess_type(path)[0] or 'application/octet-stream')
    def do_POST(self):
        if self.path!='/api/action':self.send_bytes(404,b'{}');return
        origin=self.headers.get('Origin')
        if origin and urlparse(origin).netloc!=self.headers.get('Host'):
            self.send_bytes(403,b'{"error":"Invalid request origin."}');return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>16384:raise ValueError('Invalid request size.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError('Expected an object.')
            key,game=self.get_session()
            with self.server.app.lock:response=game.action(data)
            self.send_bytes(200,json.dumps(response).encode(),cookie=key)
        except (ValueError,TypeError,KeyError) as error:self.send_bytes(400,json.dumps(dict(error=str(error))).encode())
        except OSError:self.send_bytes(500,b'{"error":"The server could not access its data files."}')

def make_server(port=8000,path=None,host='127.0.0.1'):
    server=ThreadingHTTPServer((host,port),Handler);server.app=WebApp(path);return server

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=int(os.environ.get('PORT','8000')))
    parser.add_argument('--strictPort',action='store_true',help=argparse.SUPPRESS);parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--data',type=Path,default=None)
    args=parser.parse_args();server=make_server(args.port,args.data,args.host)
    print(f'CodeQuest: http://{args.host}:{server.server_port} (Ctrl+C to stop)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
