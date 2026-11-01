"""Interface-independent round rules."""
import random

class Round:
    def __init__(self, question):
        self.question = question
        self.cards = random.sample(question.cards, len(question.cards))
        self.grid = [self.cards[:3], self.cards[3:]]
        self.selected = set()
        self.hinted = False
        self.hints = set(); self.penalty = 0; self.eliminated = set()
        self.submitted = False

    @property
    def correct(self):
        return {i for i, card in enumerate(self.cards) if card.output == self.question.target}

    def hint(self, kind='count'):
        if self.submitted:raise ValueError('This round is complete.')
        costs={'count':40,'concept':20,'eliminate':30}
        if kind not in costs:raise ValueError('Unknown hint.')
        if kind not in self.hints:
            if kind=='eliminate':
                wrong=[i for i in range(len(self.cards)) if i not in self.correct and i not in self.eliminated]
                if not wrong:return 'No incorrect card is available to remove.'
                removed=random.choice(wrong);self.eliminated.add(removed);self.selected.discard(removed)
            self.penalty=min(80,self.penalty+costs[kind]);self.hints.add(kind)
        self.hinted=True
        if kind=='count':message=f'{len(self.correct)} cards match the target.'
        elif kind=='concept':
            from questions import STUDY_TIPS
            message=STUDY_TIPS[self.question.topic]
        else:message='One incorrect card is disabled.'
        return message+f' Perfect-round reward: {100-self.penalty} points.'

    def submit(self,timed_out=False):
        if self.submitted:raise ValueError('This round has already been submitted.')
        if not self.selected and not timed_out:raise ValueError('Choose at least one card first.')
        self.submitted=True
        won=not timed_out and self.selected==self.correct
        return won, max(20,100-self.penalty) if won else 0

class Duel:
    """Resolve a numbered round only after both local players submit once."""
    def __init__(self, questions=None, max_rounds=None):
        self.players = [dict(name=f'Player {i+1}', lives=3, score=0, results=[]) for i in range(2)]
        self.turn = random.randrange(2)
        self.winner = None
        self.finished = False
        self.reason = ''
        self.completed_rounds = 0
        self.awaiting_next = False
        self.plan = []
        if questions:
            topics = {}
            for q in questions:
                topics.setdefault(q.topic, []).append(q)
            # Same topic and difficulty within each numbered round, different
            # variants. Each player sees every authored question exactly once.
            for group in topics.values():
                variants = random.sample(group, len(group))
                shifted = variants[1:] + variants[:1]
                self.plan.extend(zip(variants, shifted))
            random.shuffle(self.plan)
        self.total_rounds = max_rounds if max_rounds is not None else (len(self.plan) or 27)
        if type(self.total_rounds) is not int or self.total_rounds < 1:
            raise ValueError('A duel needs at least one round.')
        if self.plan and self.total_rounds > len(self.plan):
            raise ValueError('Not enough question pairs for the requested rounds.')

    @property
    def active(self):
        return self.players[self.turn]

    @property
    def round_number(self):
        return min(self.completed_rounds + 1, self.total_rounds)

    @property
    def question(self):
        if self.finished or self.awaiting_next:
            raise ValueError('Advance to the next turn before requesting a question.')
        if not self.plan:
            raise ValueError('This duel has no question bank.')
        return self.plan[self.completed_rounds][self.turn]

    @property
    def result_message(self):
        if not self.finished:
            return 'Duel ended early · No winner declared'
        title = 'Draw!' if self.winner is None else self.players[self.winner]['name'] + ' wins!'
        return title + ' · ' + self.reason

    def record(self, result):
        if self.finished or self.awaiting_next:
            raise ValueError('This turn is already complete.')
        self.active['results'].append(result.copy())
        self.active['score'] += result['points']
        if not result['won']:
            self.active['lives'] -= 1
        self.awaiting_next = True
        counts = [len(p['results']) for p in self.players]
        if counts[0] != counts[1]:
            return  # The other player must finish this same numbered round.
        self.completed_rounds += 1
        empty = [p['lives'] == 0 for p in self.players]
        if any(empty):
            self.finished = True
            if empty[0] != empty[1]:
                self.winner = 1 if empty[0] else 0
                self.reason = 'only one player has lives left'
                return
            self.reason = 'both reached zero lives; points decide'
        elif self.completed_rounds >= self.total_rounds:
            self.finished = True
            self.reason = 'all rounds completed; points decide'
        if self.finished:
            scores = [p['score'] for p in self.players]
            self.winner = None if scores[0] == scores[1] else (0 if scores[0] > scores[1] else 1)
            if self.winner is None:
                self.reason += '; equal points'

    def advance(self):
        if self.finished:
            raise ValueError('The duel is finished.')
        if not self.awaiting_next:
            raise ValueError('Submit the current round first.')
        self.turn = 1-self.turn
        self.awaiting_next = False
