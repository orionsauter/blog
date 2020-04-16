'''
Interactive play for Pyquet
'''

import pydealer as deal
import Pyquet as pq

class Human(pq.Player):
    
    def pick_discards(self, n):
        valid = False
        while not valid:
            valid = True
            choices = list(self.hand)
            print(' '.join([c.abbrev for c in choices]))
            abbrevs = input(
                'Pick up to {} cards to discard: '.format(n)).split(' ')
            discards = [c for c in choices if c.abbrev in abbrevs]
            if len(discards) > n:
                valid = False
        return discards

    def pick_trick_card(self, lead=None):
        valid = False
        while not valid:
            valid = True
            choices = list(self.hand)
            if lead is not None:
                print('Lead card: {}'.format(lead.abbrev))
                choices = [c for c in choices if c.suit == lead.suit]
            if len(choices) == 0:
                choices = list(self.hand)
            print(' '.join([c.abbrev for c in choices]))
            abbrev = input('Pick card to play: ')
            play = [c for c in choices if c.abbrev == abbrev]
            if len(play) != 1:
                valid = False
        self.hand, _ = deal.tools.get_card(self.hand, str(play[0]))
        return play[0]

p1 = Human('Hugh Mann')
p2 = pq.Player('RandBot')
pq.Game(p1, p2, False)
