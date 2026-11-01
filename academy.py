"""Profiles, daily challenges, progress, cosmetics and exports. Standard library only."""
import csv
import hashlib
import json
import random
import uuid
from datetime import datetime
from pathlib import Path
from statistics import Statistics

DEFAULT_SETTINGS = dict(timer=0, music=False, large_text=False, high_contrast=False, sound=False, animations=True)
THEMES = {
    'Classic parchment': dict(font='Courier', motif='parchment', label='ARCHIVE / ORIGINAL', price=0, fill='#fff5dc', ink='#302336', edge='#a27453'),
    'Midnight slate': dict(font='Courier', motif='terminal', label='FISHER / NIGHT SHIFT', price=60, fill='#182a40', ink='#fff4df', edge='#729fc7'),
    'Forest study': dict(font='Courier', motif='botanical', label='VICTORIA PARK / FIELD NOTES', price=80, fill='#183b31', ink='#f5f2d5', edge='#86c69e'),
    'Royal purple': dict(font='Courier', motif='royal', label='QUADRANGLE / HONOURS', price=100, fill='#352049', ink='#fff2e0', edge='#c7a2e4'),
}
LEVELS = ['Beginner', 'Intermediate', 'Advanced']

def local_day():
    return datetime.now().astimezone().date().isoformat()

def validate_result(row):
    return (isinstance(row, dict) and isinstance(row.get('topic'), str)
            and type(row.get('won')) is bool and type(row.get('points')) is int)

class ProfileStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path.home()/'.codequest'/'profiles.json'
        self.warning = ''
        self.data = dict(version=1, active='', profiles={})
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict) or raw.get('version') != 1 or not isinstance(raw.get('profiles'), dict):
                raise ValueError('Invalid profile file')
            for pid,p in raw['profiles'].items():
                if not isinstance(pid,str) or not isinstance(p,dict) or not isinstance(p.get('name'),str):
                    raise ValueError('Invalid profile')
                if not isinstance(p.get('results'),list) or not all(validate_result(r) for r in p['results']):
                    raise ValueError('Invalid results')
                if type(p.get('coins')) is not int or p['coins'] < 0:
                    raise ValueError('Invalid balance')
                p['settings'] = dict(DEFAULT_SETTINGS, **{k:v for k,v in p.get('settings',{}).items() if k in DEFAULT_SETTINGS})
                for key in ('large_text','high_contrast','sound','animations','music'):
                    if type(p['settings'][key]) is not bool: p['settings'][key] = DEFAULT_SETTINGS[key]
                if p['settings']['timer'] not in (0,45,90): p['settings']['timer']=0
                p['owned'] = [name for name in p.get('owned',[]) if name in THEMES]
                if 'Classic parchment' not in p['owned']: p['owned'].insert(0,'Classic parchment')
                if p.get('theme') not in p['owned']: p['theme']='Classic parchment'
                if not isinstance(p.get('daily'),dict): p['daily']={}
                p.setdefault('tutorial_done',False)
            if not raw['profiles'] or raw.get('active') not in raw['profiles']:
                raise ValueError('No active profile')
            self.data=raw
        except FileNotFoundError:
            legacy=self.path.with_name('progress.json')
            previous=[]
            try:
                old=json.loads(legacy.read_text(encoding='utf-8'))
                if isinstance(old,list) and all(validate_result(r) for r in old): previous=old
            except (OSError,ValueError): pass
            self.create('Student',previous,save=False)
            self.save()
        except (OSError,ValueError,TypeError,AttributeError):
            self.create('Student',save=False)
            self.warning='Profiles could not be loaded. The original file has been preserved; this session is temporary.'
            # Do not replace damaged data automatically.
            self.read_only=True

    @property
    def profiles(self): return self.data['profiles']
    @property
    def active_id(self): return self.data['active']
    @property
    def active(self): return self.profiles[self.active_id]

    def create(self,name,results=None,save=True):
        name=name.strip()
        if not name or len(name)>24: raise ValueError('Use a name between 1 and 24 characters.')
        if any(p['name'].casefold()==name.casefold() for p in self.profiles.values()):
            raise ValueError('That name already exists.')
        pid=uuid.uuid4().hex
        previous=list(results or [])
        self.profiles[pid]=dict(name=name,results=previous,coins=sum(max(0,r['points'])//10 for r in previous),
            owned=['Classic parchment'],theme='Classic parchment',settings=dict(DEFAULT_SETTINGS),daily={},tutorial_done=False)
        if not self.active_id:self.data['active']=pid
        if save:self.save()
        return pid

    def select(self,pid):
        if pid not in self.profiles: raise ValueError('Unknown player.')
        self.data['active']=pid;self.save()

    def rename(self,pid,name):
        name=name.strip()
        if not name or len(name)>24:raise ValueError('Use a name between 1 and 24 characters.')
        if any(i!=pid and p['name'].casefold()==name.casefold() for i,p in self.profiles.items()):
            raise ValueError('That name already exists.')
        self.profiles[pid]['name']=name;self.save()

    def save(self):
        if getattr(self,'read_only',False): return False
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temp=self.path.with_suffix('.tmp')
            temp.write_text(json.dumps(self.data,indent=2),encoding='utf-8');temp.replace(self.path)
            self.warning='';return True
        except OSError:
            self.warning='Changes work this session, but could not be saved to disk.';return False

    def record(self,pid,result):
        if not validate_result(result):raise ValueError('Invalid result.')
        p=self.profiles[pid]
        row=dict(result)
        row.setdefault('date',local_day());row.setdefault('timestamp',datetime.now().astimezone().isoformat(timespec='seconds'))
        # A daily question earns coins only on its first attempt that day.
        eligible=not (row.get('mode')=='daily' and any(
            r.get('mode')=='daily' and r.get('date')==row['date'] and r.get('question_id')==row.get('question_id')
            for r in p['results']))
        row['coins_earned']=max(0,row['points'])//10 if eligible else 0
        p['results'].append(row);p['coins']+=row['coins_earned'];self.save()
        return row

    def purchase(self,pid,name):
        if name not in THEMES:raise ValueError('Unknown card theme.')
        p=self.profiles[pid]
        if name not in p['owned']:
            cost=THEMES[name]['price']
            if p['coins']<cost:raise ValueError(f'You need {cost-p["coins"]} more coins.')
            p['coins']-=cost;p['owned'].append(name)
        p['theme']=name;self.save()

    def complete_daily(self,pid,day,score,completed):
        p=self.profiles[pid];old=p['daily'].get(day,{})
        p['daily'][day]=dict(best=max(score,old.get('best',0)),completed=completed or old.get('completed',False))
        self.save()

class ProfileStatistics(Statistics):
    def __init__(self,store,pid):self.store=store;self.pid=pid;self.results=store.profiles[pid]['results']
    @property
    def warning(self):return self.store.warning
    def record(self,topic,won,points,**details):
        return self.store.record(self.pid,dict(details,topic=topic,won=won,points=points))

def badge_progress(results):
    perfect=sum(r['won'] and r['points']==100 and not r.get('tutorial') for r in results)
    wins=sum(r['won'] and not r.get('tutorial') for r in results)
    badges=[dict(name='First Victory',description='Win one scored round.',value=min(1,wins),goal=1),
            dict(name='5 Perfect Rounds',description='Win five rounds without hints.',value=min(5,perfect),goal=5)]
    for title,topic in [('Python Apprentice','Arithmetic'),('Slice Master','Slicing'),('Function Wizard','Functions')]:
        ids={r['question_id'] for r in results if r['won'] and r['topic']==topic and r.get('question_id') and not r.get('tutorial')}
        badges.append(dict(name=title,description='Win three different '+topic+' questions.',value=min(3,len(ids)),goal=3))
    return badges

def recommended_level(results):
    recent=[r for r in results if r.get('difficulty') in LEVELS and r.get('mode')=='progressive'][-4:]
    if not recent:return 'Beginner'
    current=LEVELS.index(recent[-1]['difficulty'])
    at_level=[r for r in recent if r['difficulty']==LEVELS[current]]
    if len(at_level)>=2 and not at_level[-1]['won'] and not at_level[-2]['won']:
        current=max(0,current-1)
    elif len(at_level)>=3 and all(r['won'] for r in at_level[-3:]):
        current=min(2,current+1)
    return LEVELS[current]

def daily_questions(questions,day):
    rng=random.Random(int(hashlib.sha256(day.encode()).hexdigest(),16))
    chosen=[rng.choice([q for q in questions if q.difficulty==level]) for level in LEVELS]
    chosen+=rng.sample([q for q in questions if q not in chosen],2)
    rng.shuffle(chosen);return chosen

def mistake_rows(round_):
    rows=[]
    for i,c in enumerate(round_.cards):
        missed=i in round_.correct and i not in round_.selected
        wrong=i in round_.selected and i not in round_.correct
        if missed or wrong:
            rows.append(dict(kind='Missed match' if missed else 'Incorrect selection',code=c.code,
                output=c.output,target=round_.question.target,explanation=c.explanation,concept=getattr(c,'concept','') or round_.question.topic))
    return rows

class Countdown:
    """A pause-aware countdown; elapsed time is supplied by the UI clock."""
    def __init__(self,seconds):self.remaining=float(seconds);self.enabled=seconds>0
    def advance(self,elapsed,active=True):
        if self.enabled and active:self.remaining=max(0,self.remaining-max(0,elapsed))
        return self.enabled and self.remaining<=0

def export_report(path,profile,format='txt'):
    path=Path(path);rows=profile['results']
    temp=path.with_suffix(path.suffix+'.tmp')
    try:
        if format=='csv':
            columns=['timestamp','mode','topic','difficulty','question_id','won','points','missed','incorrect','timed_out','coins_earned']
            with temp.open('w',newline='',encoding='utf-8-sig') as f:
                writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader()
                for row in rows:
                    safe={k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in row.items()}
                    writer.writerow(safe)
        else:
            lines=['CODEQUEST PROGRESS REPORT',profile['name'],f'Generated: {datetime.now().astimezone().isoformat(timespec="seconds")}',
                   f'Rounds: {len(rows)}',f'Wins: {sum(r["won"] for r in rows)}',f'Points: {sum(r["points"] for r in rows)}','']
            good,practice=Statistics.feedback(rows)
            lines+=['Practise next: '+practice,'Did well: '+good,'','BADGES']
            lines += [f'{b["name"]}: {b["value"]}/{b["goal"]}' for b in badge_progress(rows)]
            lines+=['','MISTAKES TO REVISIT']
            for row in rows:
                for m in row.get('mistakes',[]):
                    lines+=[row['topic']+' | '+m['kind'],m['code'],f'Target: {m["target"]}; actual: {m["output"]}',m['explanation'],'']
            temp.write_text('\n'.join(lines),encoding='utf-8')
        temp.replace(path)
    except OSError:
        temp.unlink(missing_ok=True);raise
