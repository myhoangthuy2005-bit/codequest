"""Persistent progress with file I/O, validation and recoverable errors."""
import json
from pathlib import Path

class Statistics:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path.home() / '.codequest' / 'progress.json'
        self.results = []
        self.warning = ''
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(data, list) or any(not isinstance(r, dict) or
                not isinstance(r.get('topic'), str) or type(r.get('won')) is not bool or
                type(r.get('points')) is not int for r in data):
                raise ValueError('Invalid progress format')
            self.results = data
        except FileNotFoundError:
            pass
        except (OSError, ValueError):
            self.warning = 'Saved progress could not be loaded. This session starts fresh.'

    def record(self, topic, won, points, **details):
        self.results.append(dict(details, topic=topic, won=won, points=points))
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix('.tmp')
            temp.write_text(json.dumps(self.results, indent=2), encoding='utf-8')
            temp.replace(self.path)
            self.warning = ''
        except OSError:
            self.warning = 'Progress is available this session, but could not be saved.'

    def summary(self):
        wins = sum(r['won'] for r in self.results)
        points = sum(r['points'] for r in self.results)
        topics = sorted({r['topic'] for r in self.results})
        lines = [f'Rounds: {len(self.results)}    Wins: {wins}    Losses: {len(self.results)-wins}', f'Total points: {points}', '']
        for topic in topics:
            rows = [r for r in self.results if r['topic'] == topic]
            correct = sum(r['won'] for r in rows)
            lines.append(f'{topic}: {correct}/{len(rows)} perfect rounds')
        missed = sorted({r['topic'] for r in self.results if not r['won']})
        lines += ['', 'Suggested practice: ' + (', '.join(missed) or 'Keep exploring new topics!')]
        if wins:
            lines += ['Achievement: First Victory']
        if wins >= 5:
            lines += ['Achievement: 5 Perfect Rounds']
        return '\n'.join(lines)

    @staticmethod
    def feedback(results):
        """Summarise observed success and mistakes, without claiming mastery."""
        topics=sorted({r['topic'] for r in results})
        strengths=[]; practice=[]
        for topic in topics:
            rows=[r for r in results if r['topic']==topic]
            wins=sum(r['won'] for r in rows)
            if wins: strengths.append(topic)
            if wins<len(rows): practice.append(topic)
        return (', '.join(strengths) or 'No perfect rounds yet — keep practising.',
                ', '.join(practice) or ('No missed topics this session. Try a harder chapter!' if results else 'Play a round to get personalised suggestions.'))

    @staticmethod
    def badges(results):
        """Badges use demonstrated results; topic badges need distinct questions."""
        definitions=[('First Victory','Win one round.',any(r['won'] for r in results)),
                     ('5 Perfect Rounds','Win five rounds without hints.',sum(r['won'] and r['points']==100 for r in results)>=5)]
        for title,topic in [('Python Apprentice','Arithmetic'),('Slice Master','Slicing'),('Function Wizard','Functions')]:
            distinct={r.get('question_id') for r in results if r['won'] and r['topic']==topic and r.get('question_id')}
            definitions.append((title,'Win all three different '+topic+' questions.',len(distinct)>=3))
        return definitions
