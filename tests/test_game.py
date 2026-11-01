import ast
import tempfile
import unittest
from pathlib import Path
from game import Round
from questions import QUESTIONS
from statistics import Statistics

class RulesTests(unittest.TestCase):
    def test_curated_outputs(self):
        # Only trusted, bundled content is executed here for authoring validation.
        for q in QUESTIONS:
            for card in q.cards:
                tree = ast.parse(card.code)
                ns = {}
                exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), '<card>', 'exec'), ns)
                actual = eval(compile(ast.Expression(tree.body[-1].value), '<card>', 'eval'), ns)
                self.assertEqual(repr(actual), card.output)
            self.assertGreater(sum(c.output == q.target for c in q.cards), 0)
    def test_score_hint_and_duplicate(self):
        r = Round(QUESTIONS[0]); r.selected = r.correct.copy()
        self.assertEqual(r.submit(), (True,100))
        with self.assertRaises(ValueError): r.submit()
        r = Round(QUESTIONS[0]); r.selected = r.correct.copy(); r.hint()
        self.assertEqual(r.submit(), (True,60))
    def test_partial_empty_and_wrong(self):
        r = Round(QUESTIONS[0])
        with self.assertRaises(ValueError): r.submit()
        r.selected = {next(iter(r.correct))}
        self.assertEqual(r.submit(), (False,0))
        r = Round(QUESTIONS[0]); r.selected = set(range(6))
        self.assertEqual(r.submit(), (False,0))
    def test_persistence_and_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'save.json'
            s=Statistics(path); s.record('Lists', True, 100)
            self.assertEqual(Statistics(path).results, s.results)
            path.write_text('{broken')
            self.assertTrue(Statistics(path).warning)
            path.write_text('[{"topic": "x", "won": "yes", "points": 2}]')
            self.assertEqual(Statistics(path).results, [])

if __name__ == '__main__': unittest.main()
