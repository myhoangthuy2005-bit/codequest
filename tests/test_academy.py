import csv
import json
import tempfile
import unittest
from pathlib import Path
from academy import (ProfileStore,ProfileStatistics,Countdown,THEMES,badge_progress,
                     daily_questions,recommended_level,export_report,mistake_rows)
from questions import QUESTIONS
from expression_lab import evaluate,ExpressionError,LabRound,TASKS,evaluate_task
from game import Round

class ProfilesTests(unittest.TestCase):
    def test_migration_separation_settings_coins_and_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'profiles.json'
            path.with_name('progress.json').write_text(json.dumps([dict(topic='Lists',won=True,points=100)]))
            store=ProfileStore(path);one=store.active_id;two=store.create('Second player')
            self.assertEqual(store.profiles[one]['coins'],10)
            store.record(two,dict(topic='Slicing',won=True,points=80,question_id='s1'))
            store.profiles[two]['settings']['timer']=90;store.select(two)
            reloaded=ProfileStore(path)
            self.assertEqual(reloaded.active_id,two)
            self.assertEqual(reloaded.active['coins'],8)
            self.assertEqual(reloaded.active['settings']['timer'],90)
            self.assertEqual(len(reloaded.profiles[one]['results']),1)
            self.assertEqual(reloaded.profiles[one]['results'][0]['topic'],'Lists')
    def test_duplicate_names_and_shop_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            s=ProfileStore(Path(folder)/'p.json');pid=s.active_id
            with self.assertRaises(ValueError):s.create(' student ')
            with self.assertRaises(ValueError):s.create('')
            with self.assertRaises(ValueError):s.purchase(pid,'Midnight slate')
            s.active['coins']=100
            s.purchase(pid,'Midnight slate');self.assertEqual(s.active['coins'],40)
            s.purchase(pid,'Midnight slate');self.assertEqual(s.active['coins'],40)
            self.assertEqual(ProfileStore(s.path).active['theme'],'Midnight slate')
    def test_corrupt_profile_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'p.json';p.write_text('{broken')
            s=ProfileStore(p);self.assertTrue(s.warning);s.save()
            self.assertEqual(p.read_text(),'{broken')
    def test_daily_replays_do_not_farm_coins(self):
        with tempfile.TemporaryDirectory() as folder:
            s=ProfileStore(Path(folder)/'p.json')
            r=dict(topic='Lists',won=True,points=100,mode='daily',date='2026-11-01',question_id='q1')
            s.record(s.active_id,r);s.record(s.active_id,r)
            self.assertEqual(s.active['coins'],10)
            r['date']='2026-11-02';s.record(s.active_id,r);self.assertEqual(s.active['coins'],20)
            s.complete_daily(s.active_id,'2026-11-01',300,True)
            s.complete_daily(s.active_id,'2026-11-01',100,False)
            self.assertEqual(s.active['daily']['2026-11-01'],dict(best=300,completed=True))
    def test_reports_export_profile_only_and_preserve_details(self):
        with tempfile.TemporaryDirectory() as folder:
            s=ProfileStore(Path(folder)/'p.json');second=s.create('Secret Other')
            s.record(second,dict(topic='Private',won=True,points=100))
            mistake=dict(kind='Missed match',code='2 + 3',target='5',output='5',explanation='Add both values.',concept='Arithmetic')
            s.record(s.active_id,dict(topic='Arithmetic',won=False,points=0,mistakes=[mistake],question_id='=formula'))
            txt=Path(folder)/'report.txt';csv_path=Path(folder)/'report.csv'
            export_report(txt,s.active,'txt');export_report(csv_path,s.active,'csv')
            self.assertIn('Add both values.',txt.read_text());self.assertNotIn('Secret Other',txt.read_text())
            with csv_path.open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1);self.assertEqual(rows[0]['question_id'],"'=formula")

class LearningTests(unittest.TestCase):
    def test_daily_is_deterministic_unique_and_covers_levels(self):
        a=daily_questions(QUESTIONS,'2026-11-01');b=daily_questions(QUESTIONS,'2026-11-01')
        self.assertEqual([q.id for q in a],[q.id for q in b]);self.assertEqual(len(set(q.id for q in a)),5)
        self.assertEqual({q.difficulty for q in a},{'Beginner','Intermediate','Advanced'})
    def test_progression_moves_up_and_back(self):
        rows=[dict(mode='progressive',difficulty='Beginner',won=True)]*3
        self.assertEqual(recommended_level(rows),'Intermediate')
        rows += [dict(mode='progressive',difficulty='Intermediate',won=False)]*2
        self.assertEqual(recommended_level(rows),'Beginner')
    def test_clock_pause_and_timeout(self):
        c=Countdown(45);self.assertFalse(c.advance(20));self.assertEqual(c.remaining,25)
        self.assertFalse(c.advance(40,False));self.assertEqual(c.remaining,25)
        self.assertTrue(c.advance(25));self.assertEqual(c.remaining,0)
        self.assertFalse(Countdown(0).advance(100))
    def test_all_hint_types_cost_once_and_never_remove_correct_card(self):
        r=Round(QUESTIONS[0]);original=r.correct.copy()
        r.hint('count');r.hint('count');self.assertEqual(r.penalty,40)
        r.hint('concept');self.assertEqual(r.penalty,60)
        r.hint('eliminate');self.assertEqual(r.penalty,80)
        self.assertTrue(r.eliminated.isdisjoint(r.correct));self.assertEqual(r.correct,original)
        r.selected=r.correct.copy();self.assertEqual(r.submit(),(True,20))
    def test_timeout_is_wrong_even_if_selection_would_be_correct(self):
        r=Round(QUESTIONS[0]);r.selected=r.correct.copy()
        self.assertEqual(r.submit(timed_out=True),(False,0))
    def test_detailed_mistakes_have_code_concept_and_reason(self):
        r=Round(QUESTIONS[0]);wrong=next(i for i in range(6) if i not in r.correct)
        r.selected={wrong};mistakes=mistake_rows(r)
        self.assertTrue(any(m['kind']=='Incorrect selection' for m in mistakes))
        self.assertTrue(any(m['kind']=='Missed match' for m in mistakes))
        self.assertTrue(all(m['concept'] and m['explanation'] and m['code'] for m in mistakes))
    def test_badge_progress_caps_and_tutorial_does_not_count(self):
        rows=[dict(topic='Slicing',won=True,points=100,question_id=str(i)) for i in range(10)]
        progress={b['name']:b for b in badge_progress(rows)}
        self.assertEqual(progress['Slice Master']['value'],3)
        self.assertEqual(progress['5 Perfect Rounds']['value'],5)
        for r in rows:r['tutorial']=True
        self.assertEqual(badge_progress(rows)[0]['value'],0)

class LabTests(unittest.TestCase):
    def test_all_model_solutions_and_variable_requirement(self):
        for task in TASKS:
            self.assertEqual(repr(evaluate_task(task.example,task)),task.target)
            self.assertEqual(LabRound(task).submit(task.example),(True,100))
        r=LabRound(TASKS[0]);won,points=r.submit(TASKS[0].target)
        self.assertFalse(won);self.assertIn('provided variable',r.error)
    def test_safe_evaluator_rejects_code_and_resource_abuse(self):
        examples=['__import__("os")','(1).__class__','open("secret")','[x for x in range(4)]','"x" * 1000000000',
                  '2 ** 1000000000','list(range(100000000))','"%1000000000s" % 1','lambda: 2','n = 3']
        for expression in examples:
            with self.assertRaises(ExpressionError,msg=expression):evaluate(expression,{'n':3})
    def test_error_feedback_hint_and_single_submission(self):
        r=LabRound(TASKS[0]);r.hint();self.assertEqual(r.submit('n * 2'),(True,80))
        with self.assertRaises(ValueError):r.submit('n * 2')
        r=LabRound(TASKS[0]);self.assertEqual(r.submit('n / 0'),(False,0));self.assertIn('zero',r.error)
        self.assertEqual(LabRound(TASKS[0]).submit('',True),(False,0))
    def test_values_types_slices_and_short_circuit(self):
        self.assertEqual(evaluate('nums[1:3]',{'nums':[0,2,4,6]}),[2,4])
        self.assertIs(evaluate('False and 1 / 0',{}),False)
        self.assertEqual(evaluate('len(str(abs(n)))',{'n':-123}),3)
        self.assertEqual(evaluate('2 < n < 5',{'n':3}),True)

if __name__=='__main__':unittest.main()
