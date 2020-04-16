'''
Game of Piquet
Rules from https://www.pagat.com/notrump/piquet.html
'''

import pydealer as deal
import numpy as np
import itertools as it
from collections import deque

RANKS = deal.DEFAULT_RANKS['values']
SUITS = deal.DEFAULT_RANKS['suits']

class Hand(deal.Stack):

    def __str__(self):
        abbr = [c.abbrev for c in self.cards]
        return ' '.join(abbr)
    
    def sort(self, ranks=None):
        '''
        Adaptation of pydealer.tools.sort_cards to sort
        on suits, then rank.
        '''
        ranks = ranks or deal.DEFAULT_RANKS

        if ranks.get('values') is None:
            self.cards = sorted(
                self.cards,
                key=lambda x: ranks['suits'][x.suit] if x.suit != None else 0
            )
        elif ranks.get('suits') is None:
            self.cards = sorted(
                self.cards,
                key=lambda x: ranks['values'][x.value]
            )
        else:
            self.cards = sorted(
                self.cards,
                key=lambda x: (ranks['suits'][x.suit] if x.suit != None else 0,
                               ranks['values'][x.value])
            )

        return self.cards

    # Point: Number of cards in largest suit
    def point(self):
        counts = {'C':0, 'D':0, 'H':0, 'S':0}
        for card in self.cards:
            counts[card.suit[0]] += 1
        return max(counts.values())

    # Tuples: Groups of equal rank cards
    def tuples(self):
        tups = np.zeros((8,))
        for card in self.cards:
            tups[RANKS[card.value] - 6] += 1
        return tups

    # Sequence: Ordered cards in a single suit
    def sequence(self):
        max_seq = 0
        max_rnk = 0
        for suit in SUITS.keys():
            ranks = [RANKS[card.value] for card in self.cards
                     if card.suit == suit]
            if len(ranks) < 2:
                continue
            runs = [len(list(g)) for k,g in it.groupby(np.diff(ranks))]
            if np.max(runs) >= max_seq:
                i = np.argmax(runs)
                if np.max(runs) == max_seq and \
                    ranks[np.cumsum(runs)[i]] < max_rnk:
                    continue
                max_seq = runs[i]
                max_rnk = ranks[np.cumsum(runs)[i]]
        return max_seq+1, max_rnk

    def remove(self, to_remove):
        self.cards = deque([c for c in self.cards if c not in to_remove])
        return

    def discard(self, cards, talon):
        nremoved = len(self.cards)
        self.remove(cards)
        nremoved -= len(self.cards)
        self.insert_list(talon.deal(nremoved))
        self.sort()
        return talon

class Player:
    def reset(self):
        # Seen not yet implemented
        self.seen = dict()
        for r in RANKS.keys():
            if RANKS[r] < 7:
                continue
            for s in SUITS.keys():
                self.seen['{} of {}'.format(r, s)] = False
        self.hand = Hand()
        self.tricks = 0
        
    def __init__(self, name=None, hand=None):
        self.name = name
        self.score = 0
        self.reset()
        if hand is not None:
            self.hand = hand
            for card in self.hand:
                self.seen[str(card)] = True
            
    def __str__(self):
        return '{}\tScore: {}\tHand: {}'.format(self.name,
                                               self.score,
                                               self.hand)

    def pick_discards(self, n):
        choices = list(self.hand)
        discards = np.random.choice(choices, n, replace=False)
        return discards

    def pick_trick_card(self, lead=None):
        choices = list(self.hand)
        if lead is not None:
            choices = [c for c in choices if c.suit == lead.suit]
        if len(choices) == 0:
            choices = list(self.hand)
        play = np.random.choice(choices)
        self.hand, _ = deal.tools.get_card(self.hand, str(play))
        return play

'''
Need longest sequence with ties broken by highest value.
Construct magic number to reduce to one comparison:
    1   2   3   4   5     6     7
7   6   48  162 384 750   1296  2058
8   7   56  189 448 875   1512  2401
9   8   64  216 512 1000  1728  2744
10  9   72  243 576 1125  1944  3087
11  10  80  270 640 1250  2160  3430
12  11  88  297 704 1375  2376  3773
13  12  96  324 768 1500  2592  4116
14  13  104 351 832 1625  2808  4459
'''
def Score_Sequence(seq):
    magic = (seq[1] + (seq[0]*seq[0]))*seq[0]
    score = 0
    if seq[0] > 4:
        score = 10 + seq[0]
    elif seq[0] > 2:
        score = seq[0]
    return magic, score

'''
Need largest tuple of highest rank.
Construct magic number to reduce to one comparison:
    1   2   3   4
0   8   22  48  92
1   9   24  51  96
2   10  26  54  100
3   11  28  57  104
4   12  30  60  108
5   13  32  63  112
6   14  34  66  116
7   15  36  69  120
'''
def Score_Tuples(tups):
    magic = (np.arange(7, 15) + tups*tups)*tups
    score = np.zeros_like(tups, dtype=np.int64)
    score[tups == 3] = 3
    score[tups == 4] = 14
    return np.max(magic), np.sum(score)

def Round(elder, ynger, quiet=False):
    deck = deal.Deck()
    # Remove 2-6
    _ = deck.deal(20, end='bottom')

    deck.shuffle(times=7)
    elder.reset()
    ynger.reset()
    # Traditional dealing by 3s
    for n in range(4):
        elder.hand.insert_list(deck.deal(3))
        ynger.hand.insert_list(deck.deal(3))
    elder.hand.sort()
    ynger.hand.sort()
    if not quiet:
        print(elder)
        print(ynger)

    if not quiet:
        print('Discards')
    discards = elder.pick_discards(5)
    elder.hand.discard(discards, deck)
    discards = ynger.pick_discards(3)
    ynger.hand.discard(discards, deck)
    if not quiet:
        print(elder)
        print(ynger)

    if not quiet:
        print('Declarations')
    # Point
    pt1 = elder.hand.point()
    pt2 = ynger.hand.point()
    if pt1 > pt2:
        elder.score += pt1
    elif pt2 > pt1:
        ynger.score += pt2
    if not quiet:
        print(elder)
        print(ynger)

    # Sequence
    seq1 = elder.hand.sequence()
    seq2 = ynger.hand.sequence()
    magic1, score1 = Score_Sequence(seq1)
    magic2, score2 = Score_Sequence(seq2)
    if magic1 > magic2:
        elder.score += score1
    elif magic2 > magic1:
        ynger.score += score2
    if not quiet:
        print(elder)
        print(ynger)

    # Tuples
    tup1 = elder.hand.tuples()
    tup2 = ynger.hand.tuples()
    magic1, score1 = Score_Tuples(tup1)
    magic2, score2 = Score_Tuples(tup2)
    if magic1 > magic2:
        elder.score += score1
    elif magic2 > magic1:
        ynger.score += score2
    if not quiet:
        print(elder)
        print(ynger)
    
    if not quiet:
        print('Tricks')

    lead = elder
    fllw = ynger
    for trick in range(12):
        play1 = lead.pick_trick_card()
        lead.score += 1
        play2 = fllw.pick_trick_card(play1)
        if play1.suit == play2.suit:
            if RANKS[play1.value] > RANKS[play2.value]:
                lead.tricks += 1
            else:
                fllw.tricks += 1
                fllw.score += 1
                lead, fllw = fllw, lead
        else:
            lead.tricks += 1
            
        if not quiet:
            print(lead.name, play1, lead.score)
            print(fllw.name, play2, fllw.score)
            
    # Winner of last trick is marked as lead
    lead.score += 1
    if lead.tricks == 12:
        lead.score += 40
    if fllw.tricks == 12:
        fllw.score += 40
    elif lead.tricks > fllw.tricks:
        lead.score += 10
    elif lead.tricks < fllw.tricks:
        fllw.score += 10
    if not quiet:
        print(elder.score, ynger.score)
    
    return

# Play 6 rounds and calculate final winner score
def Game(p1, p2, quiet):
    for sortie in range(6):
        Round(p1, p2, quiet)
        p1.reset()
        p2.reset()
    if p1.score > p2.score:
        if p2.score > 100:
            return [100 + p1.score - p2.score, 0]
        else:
            return [100 + p1.score + p2.score, 0]
    else:
        if p1.score > 100:
            return [0, 100 + p2.score - p1.score]
        else:
            return [0, 100 + p2.score + p1.score]

p1 = Player('One')
p2 = Player('Two')
results = np.array([Game(p1, p2, True) for i in range(10)])
print(np.sum(results, axis=0))
