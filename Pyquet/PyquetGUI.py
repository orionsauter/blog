import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import sys
import numpy as np
import pydealer as deal
import Pyquet as pq
from Human import Human
from Neural import Neural

layout = {
    'card width': 100,
    'card height': 145,
    'card spacing': 35,
    'window width': 550,
    'window height': 475,
    'button height': 20}
layout['vertical borders'] = (layout['window width'] - \
    11*layout['card spacing'] - layout['card width'])/2
layout['horizontal borders'] = (layout['window height'] - \
    3*layout['card height'] - layout['button height'])/5
layout['pending start height'] = layout['card height'] + \
                                 2*layout['horizontal borders']
layout['hand start width'] = layout['vertical borders']
layout['hand start height'] = 2*layout['card height'] + \
                              3*layout['horizontal borders']
layout['button position'] = layout['window height'] - \
                            layout['button height'] - \
                            layout['horizontal borders']
layout['centered card'] = (layout['window width'] - layout['card width'])/2

class HumanGUI(Human):
    def __init__(self, *args, **kwargs):
        self.root = kwargs.pop('root', None)
        self.pending = []
        self.waiting = True
        self.cimgs = dict()
        button = ttk.Button(self.root, text='Done',
            command=lambda: setattr(self, 'waiting', False))
        button.place(x=layout['window width']/2,
                     y=layout['button position'])
        super().__init__(*args, **kwargs)
        
    def pick_card(self, card):
        if card in self.hand.cards:
            self.pending += [card]
            self.hand.get(card.abbrev)
        elif card in self.pending:
            self.pending.remove(card)
            self.hand.insert(card)

    def showCard(self, card, x, y, state='normal'):
        if card.abbrev in self.cimgs.keys():
            button = self.cimgs[card.abbrev]
            button.place(x=x, y=y)
        else:
            path = 'cards/{}.png'.format(
                str(card).lower().replace(' ','_'))
            img = tk.PhotoImage(file=path)
            button = ttk.Button(self.root, image=img,
                command=lambda: self.pick_card(card))
            button.image = img # Prevent garbage collection
            button.state = state
            button.place(x=x, y=y)
            self.cimgs[card.abbrev] = button
        return button

    def showHand(self):
        for i in range(len(self.hand.cards)):
            self.showCard(self.hand.cards[i],
                       layout['hand start width'] + layout['card spacing']*i,
                       layout['hand start height'])

    def showPending(self):
        npend = len(self.pending)
        if npend == 0:
            return
        start = (layout['window width'] - \
            npend*layout['card spacing'] - layout['card width'])/2
        for i in range(npend):
            self.showCard(self.pending[i],
                        start + layout['card spacing']*i,
                        layout['pending start height'])

    def display(self):
        self.showHand()
        self.showPending()
        self.root.update()

    def pick_discards(self, n):
        while True:
            while self.waiting:
                time.sleep(0.1)
                self.display()
            self.waiting = True
            if len(self.pending) > n:
                messagebox.showerror('Error', 'Too many discards')
            else:
                discards = self.pending
                [self.cimgs.pop(c.abbrev).destroy() for c in self.pending]
                self.pending = []
                return discards

    def pick_trick_card(self, lead=None):
        choices = list(self.hand)
        if lead is not None:
            choices = [c for c in choices if c.suit == lead.suit]
        if len(choices) == 0:
            choices = list(self.hand)
        while True:
            while self.waiting:
                time.sleep(0.1)
                self.display()
            self.waiting = True
            if len(self.pending) != 1:
                messagebox.showerror('Error', 'Choose exactly 1 card')
            elif self.pending[0] not in choices:
                messagebox.showerror('Error', 'You must follow suit')
            else:
                play = self.pending[0]
                self.pending = []
                self.hand, _ = deal.tools.get_card(self.hand, str(play))
                return play

cardNames = np.array(['7','8','9','10','Jack','Queen','King','Ace'])
def TupleList(tups):
    triples = ['triplet of {}s'.format(rank) for rank in cardNames[tups==3]]
    quadruples = ['quadruplet of {}s'.format(rank)
                  for rank in cardNames[tups==4]]
    return '\n'.join(triples + quadruples)

def Round(elder, ynger):
    deck = deal.Deck()
    # Remove 2-6
    _ = deck.deal(20, end='bottom')

    deck.shuffle(times=7)
    elder.reset()
    ynger.reset()
    human = elder if elder.isHuman else ynger
    # Traditional dealing by 3s
    for n in range(4):
        elder.hand.insert_list(deck.deal(3))
        ynger.hand.insert_list(deck.deal(3))
    elder.hand.sort()
    ynger.hand.sort()
    elder.seen.extend(elder.hand.cards)
    ynger.seen.extend(ynger.hand.cards)

    discards = elder.pick_discards(5)
    elder.hand.discard(discards, deck)
    print(elder.hand)
    n = len(discards)
    messagebox.showinfo('Discards',
        '{} discarded {} cards. {} remain'.format(elder.name, n, 8-n))
    discards = ynger.pick_discards(8-n)
    ynger.hand.discard(discards, deck)
    n = len(discards)
    messagebox.showinfo('Discards',
        '{} discarded {} cards.'.format(ynger.name, n))
    human.display()

    # Point
    pt1 = elder.hand.point()
    pt2 = ynger.hand.point()
    if pt1 > pt2:
        elder.score += pt1
        messagebox.showinfo('Declarations',
            '{} won point: {} vs {}.'.format(elder.name, pt1, pt2))
    elif pt2 > pt1:
        ynger.score += pt2
        messagebox.showinfo('Declarations',
            '{} won point: {} vs {}.'.format(ynger.name, pt2, pt1))

    # Sequence
    seq1 = elder.hand.sequence()
    seq2 = ynger.hand.sequence()
    magic1, score1 = pq.Score_Sequence(seq1)
    magic2, score2 = pq.Score_Sequence(seq2)
    if magic1 > magic2:
        elder.score += score1
        messagebox.showinfo('Declarations',
            '{} has a run of {} up to {}.'.format(
                elder.name, seq1[0], cardNames[seq1[1]-7]))
    elif magic2 > magic1:
        ynger.score += score2
        messagebox.showinfo('Declarations',
            '{} has a run of {} up to {}.'.format(
                ynger.name, seq2[0], cardNames[seq2[1]-7]))

    # Tuples
    tup1 = elder.hand.tuples()
    tup2 = ynger.hand.tuples()
    magic1, score1 = pq.Score_Tuples(tup1)
    magic2, score2 = pq.Score_Tuples(tup2)
    if magic1 > magic2:
        elder.score += score1
        messagebox.showinfo('Declarations',
            '{} wins tuples:\n'.format(elder.name) + \
            TupleList(tup1))
    elif magic2 > magic1:
        ynger.score += score2
        messagebox.showinfo('Declarations',
            '{} wins tuples:\n'.format(ynger.name) + \
            TupleList(tup2))

    lead = elder
    fllw = ynger
    for trick in range(12):
        play1 = lead.pick_trick_card()
        lead.score += 1
        fllw.seen.append(play1)
        if lead is human:
            human.pending = [play1]
        else:
            oppDisp = human.showCard(play1,
                layout['centered card'],
                layout['horizontal borders'],
                state='disabled')
        human.root.update()
        play2 = fllw.pick_trick_card(play1)
        lead.seen.append(play2)
        if lead is human:
            oppDisp = human.showCard(play2,
                layout['centered card'],
                layout['horizontal borders'],
                state='disabled')
        else:
            human.pending = [play2]
        human.display()
        if play1.suit == play2.suit:
            if pq.RANKS[play1.value] > pq.RANKS[play2.value]:
                lead.tricks += 1
            else:
                fllw.tricks += 1
                fllw.score += 1
                lead, fllw = fllw, lead
                play1, play2 = play2, play1
        else:
            lead.tricks += 1
        # Whoever won is now lead
        messagebox.showinfo('Tricks',
            '{} won the trick for total of {} vs {}'.format(lead.name,
                                                            lead.tricks,
                                                            fllw.tricks))
        
        if lead is human:
            human.cimgs[play2].destroy()
        else:
            human.cimgs[play1].destroy()
        [c.destroy() for c in human.pending]
        human.root.update()
            
    # Winner of last trick is marked as lead
    lead.score += 1
    if lead.tricks == 12:
        lead.score += 40
        messagebox.showinfo('Tricks', '{} got a capot!'.format(lead.name))
    elif fllw.tricks == 12:
        fllw.score += 40
        messagebox.showinfo('Tricks', '{} got a capot!'.format(fllw.name))
    elif lead.tricks > fllw.tricks:
        lead.score += 10
    elif lead.tricks < fllw.tricks:
        fllw.score += 10
    
    return

# Play 6 rounds and calculate final winner score
def Game(p1, p2):
    elder = p1
    ynger = p2
    for sortie in range(6):
        Round(elder, ynger)
        p1.reset()
        p2.reset()
        elder, ynger = ynger, elder
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

##if __name__ == '__main__':
##    p1 = Player('One')
##    p2 = Player('Two')
##    results = np.array([Game(p1, p2, True) for i in range(10)])
##    print(np.sum(results, axis=0))

deck = deal.Deck()
deck.shuffle(times=7)

root = tk.Tk()
root.geometry('{:d}x{:d}'.format(layout['window width'],
                                 layout['window height']))
p1 = HumanGUI('Hugh Mann', root=root)
p2 = Neural('NeuroticBot')
Game(p1, p2)
root.mainloop()
