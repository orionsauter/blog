'''
Neural net Piquet bot based on https://medium.com/@dhruvp/how-to-write-a-neural-network-to-play-pong-from-scratch-956b57d4f6e0
Dimensions:
    96 inputs per eval
    13 evals per round
    6 rounds per game
'''
import numpy as np
import Pyquet as pq
from Human import Human
import pydealer as deal
import pickle as pkl
import argparse

parser = argparse.ArgumentParser(description='Train or run a neural net bot.')
parser.add_argument('--play', action='store_true')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

deck = deal.Deck()
# Remove 2-6
_ = deck.deal(20, end='bottom')
all_cards = deal.Stack(cards=deck)

def card_to_idx(card):
    idx = 8 * (pq.SUITS[card.suit]-1) + pq.RANKS[card.value]-6
    return idx

idx_to_card = {card_to_idx(c):c for c in deck}

def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))

def relu(vector):
    vector[vector < 0] = 0
    return vector

def apply_neural_nets(observation_matrix, weights):
    """ Based on the observation_matrix and weights,
        compute the new hidden layer values and the
        new output layer values"""
    hidden_layer_values = np.dot(weights['1'], observation_matrix)
    hidden_layer_values = relu(hidden_layer_values)
    output_layer_values = np.dot(hidden_layer_values.T, weights['2'])
    output_layer_values = sigmoid(output_layer_values)
    return hidden_layer_values, output_layer_values

def compute_gradient(gradient_log_p, hidden_layer_values,
                     observation_values, weights):
    """ See here: http://neuralnetworksanddeeplearning.com/chap2.html"""
    delta_L = gradient_log_p
    dC_dw2 = np.dot(hidden_layer_values.T, delta_L)
    delta_l2 = np.dot(delta_L, weights['2'].T)
##    delta_l2 = np.outer(delta_L, weights['2'])
    delta_l2 = relu(delta_l2)
    dC_dw1 = np.dot(delta_l2.T, observation_values)
    return {
        '1': dC_dw1,
        '2': dC_dw2
    }

def update_weights(weights, expectation_g_squared, g_dict,
                   decay_rate, learning_rate):
    """ See here: http://sebastianruder.com/optimizing-gradient-descent/index.html#rmsprop"""
    epsilon = 1e-5
    for layer_name in weights.keys():
        g = g_dict[layer_name]
        expectation_g_squared[layer_name] = decay_rate * expectation_g_squared[layer_name] + (1 - decay_rate) * g**2
        weights[layer_name] += (learning_rate * g)/(np.sqrt(expectation_g_squared[layer_name] + epsilon))
        g_dict[layer_name] = np.zeros_like(weights[layer_name]) # reset batch gradient buffer

def discount_rewards(rewards, gamma):
    """ Actions you took 20 steps before the end result are less
        important to the overall result than an action you took a step ago.
        This implements that logic by discounting the reward on previous
        actions based on how long ago they were taken"""
    discounted_rewards = np.zeros_like(rewards)
    running_add = 0
    for t in reversed(range(0, len(rewards))):
        if rewards[t] != 0:
            running_add = 0 # reset the sum, since this was a game boundary (pong specific!)
        running_add = running_add * gamma + rewards[t]
        discounted_rewards[t] = running_add
    return discounted_rewards

def discount_with_rewards(gradient_log_p, episode_rewards, gamma):
    """ discount the gradient with the normalized rewards """
    discounted_episode_rewards = discount_rewards(episode_rewards, gamma)
    # standardize the rewards to be unit normal (helps control the gradient estimator variance)
    discounted_episode_rewards -= np.mean(discounted_episode_rewards)
    discounted_episode_rewards /= np.std(discounted_episode_rewards)
    return gradient_log_p * discounted_episode_rewards

def RoundNeural(elder, ynger, quiet=False):

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

    inds = [card_to_idx(c) for c in elder.hand.cards]
    obs = np.zeros((elder.input_dimensions, 1))
    obs[inds] = 1
    hidden_layer_values, probs = apply_neural_nets(obs, elder.weights)
    elder.episode_observations.append(obs.T)
    elder.episode_hidden_layer_values.append(hidden_layer_values.T)
    probs = probs.flatten() / np.sum(probs)
    dinds = np.random.choice(range(elder.output_dimensions),
                             p=probs, size=5, replace=False)
    loss_function_gradient = np.zeros_like(probs)
    loss_function_gradient[dinds] = 1.0/len(dinds)
    loss_function_gradient -= probs
    elder.episode_gradient_log_ps.append(loss_function_gradient.T)
    discards = [idx_to_card[i] for i in dinds]
    elder.hand.discard(discards, deck)
    
    inds = [card_to_idx(c) for c in ynger.hand.cards]
    obs = np.zeros((ynger.input_dimensions, 1))
    obs[inds] = 1
    hidden_layer_values, probs = apply_neural_nets(obs, ynger.weights)
    ynger.episode_observations.append(obs.T)
    ynger.episode_hidden_layer_values.append(hidden_layer_values.T)
    probs = probs.flatten() / np.sum(probs)
    dinds = np.random.choice(range(ynger.output_dimensions),
                             p=probs, size=3, replace=False)
    loss_function_gradient = np.zeros_like(probs)
    loss_function_gradient[dinds] = 1.0/len(dinds)
    loss_function_gradient -= probs
    ynger.episode_gradient_log_ps.append(loss_function_gradient.T)
    discards = [idx_to_card[i] for i in dinds]
    ynger.hand.discard(discards, deck)

    # Point
    pt1 = elder.hand.point()
    pt2 = ynger.hand.point()
    if pt1 > pt2:
        elder.score += pt1
    elif pt2 > pt1:
        ynger.score += pt2

    # Sequence
    seq1 = elder.hand.sequence()
    seq2 = ynger.hand.sequence()
    magic1, score1 = pq.Score_Sequence(seq1)
    magic2, score2 = pq.Score_Sequence(seq2)
    if magic1 > magic2:
        elder.score += score1
    elif magic2 > magic1:
        ynger.score += score2

    # Tuples
    tup1 = elder.hand.tuples()
    tup2 = ynger.hand.tuples()
    magic1, score1 = pq.Score_Tuples(tup1)
    magic2, score2 = pq.Score_Tuples(tup2)
    if magic1 > magic2:
        elder.score += score1
    elif magic2 > magic1:
        ynger.score += score2
    if not quiet:
        print(elder)
        print(ynger)

    elder.episode_rewards.append(elder.score)
    ynger.episode_rewards.append(ynger.score)
    
    if not quiet:
        print('Tricks')

    lead = elder
    fllw = ynger
    for trick in range(12):
        bad_inds = [card_to_idx(c) for c in all_cards if c not in lead.hand.cards]
        obs = np.zeros((lead.input_dimensions, 1))
        seen_inds = [card_to_idx(c) + 64 for c in lead.seen]
        obs[seen_inds] = 1
        hidden_layer_values, probs = apply_neural_nets(obs, lead.weights)
        lead.episode_observations.append(obs.T)
        lead.episode_hidden_layer_values.append(hidden_layer_values.T)
        if np.all(probs == 0):
            probs = np.ones_like(probs)
        probs[0,bad_inds] = 0
        probs = probs.flatten() / np.sum(probs)
        ind = np.random.choice(range(lead.output_dimensions), p=probs)
        loss_function_gradient = np.zeros_like(probs)
        loss_function_gradient[ind] = 1.0
        loss_function_gradient -= probs
        lead.episode_gradient_log_ps.append(loss_function_gradient.T)
        play1 = idx_to_card[ind]
        lead.hand = pq.Hand(cards=deal.tools.get_card(lead.hand, str(play1))[0])
        lead.score += 1
        fllw.seen.append(play1)
        
        bad_inds = [card_to_idx(c) for c in all_cards if c not in fllw.hand.cards]
        if any([c.suit == play1.suit for c in fllw.hand]):
            bad_inds += [card_to_idx(c) for c in all_cards if c.suit != play1.suit]
        obs = np.zeros((fllw.input_dimensions, 1))
        lead_ind = card_to_idx(play1) + 32
        obs[lead_ind] = 1
        seen_inds = [card_to_idx(c) + 64 for c in fllw.seen]
        obs[seen_inds] = 1
        hidden_layer_values, probs = apply_neural_nets(obs, fllw.weights)
        fllw.episode_observations.append(obs.T)
        fllw.episode_hidden_layer_values.append(hidden_layer_values.T)
        if np.all(probs == 0):
            probs = np.ones_like(probs)
        probs[0,bad_inds] = 0
        probs = probs.flatten() / np.sum(probs)
        ind = np.random.choice(range(fllw.output_dimensions), p=probs)
        loss_function_gradient = np.zeros_like(probs)
        loss_function_gradient[ind] = 1.0
        loss_function_gradient -= probs
        fllw.episode_gradient_log_ps.append(loss_function_gradient.T)
        play2 = idx_to_card[ind]
        fllw.hand = pq.Hand(cards=deal.tools.get_card(fllw.hand, str(play2))[0])
        if play1.suit == play2.suit:
            if pq.RANKS[play1.value] > pq.RANKS[play2.value]:
                lead.tricks += 1
                lead.episode_rewards.append(1)
                fllw.episode_rewards.append(0)
            else:
                fllw.tricks += 1
                lead.episode_rewards.append(0)
                fllw.episode_rewards.append(1)
                fllw.score += 1
                lead, fllw = fllw, lead
                play1, play2 = play2, play1
        else:
            lead.tricks += 1
            lead.episode_rewards.append(1)
            fllw.episode_rewards.append(0)
            
        if not quiet:
            print(lead.name, play1, lead.score)
            print(fllw.name, play2, fllw.score)
            
    # Winner of last trick is marked as lead
    lead.score += 1
    lead.episode_rewards[-1] += 1
    if lead.tricks == 12:
        lead.score += 40
        for i in range(-12, 0):
            lead.episode_rewards[i] += 40
    elif fllw.tricks == 12:
        fllw.score += 40
        for i in range(-12, 0):
            fllw.episode_rewards[i] += 40
    elif lead.tricks > fllw.tricks:
        lead.score += 10
        for i in range(-12, 0):
            lead.episode_rewards[i] += 10
    elif lead.tricks < fllw.tricks:
        fllw.score += 10
        for i in range(-12, 0):
            fllw.episode_rewards[i] += 10
    if not quiet:
        print(elder.score, ynger.score)
    
    return

class Neural(pq.Player):

    def __init__(self, *args, **kwargs):
        self.weights = kwargs.pop('weights', None)
        self.hand = kwargs.pop('hand', None)
        super().__init__(*args, **kwargs)
        self.reset()
        if self.hand is not None:
            for card in self.hand:
                self.seen[str(card)] = True
                
        # hyperparameters
        self.episode_number = 0
        self.batch_size = 20
        self.gamma = 0.99 # discount factor for reward
        self.decay_rate = 0.99
        self.num_hidden_layer_neurons = 200
        self.input_dimensions = 32 * 3
        self.output_dimensions = 32
        self.learning_rate = 1e-4
        self.memory = 1000

        self.reward_sum = 0
        self.running_reward = None
        self.prev_processed_observations = None

        self.episode_hidden_layer_values = []
        self.episode_observations = []
        self.episode_gradient_log_ps = []
        self.episode_rewards = []

        if self.weights is None:
            self.weights = {
                '1': np.random.randn(self.num_hidden_layer_neurons,
                    self.input_dimensions) / np.sqrt(self.input_dimensions),
                '2': np.random.randn(self.num_hidden_layer_neurons, \
                                     self.output_dimensions
                                     ) \
                    / np.sqrt(self.num_hidden_layer_neurons)
            }

    def pick_discards(self, n):
        inds = [card_to_idx(c) for c in self.hand.cards]
        obs = np.zeros((self.input_dimensions, 1))
        obs[inds] = 1
        hidden_layer_values, probs = apply_neural_nets(obs, self.weights)
        if np.all(probs == 0):
            probs = np.ones_like(probs)
        probs = probs.flatten() / np.sum(probs)
        dinds = np.random.choice(range(self.output_dimensions),
                                 p=probs, size=n, replace=False)
        discards = [idx_to_card[i] for i in dinds]
        return discards

    def pick_trick_card(self, lead=None):
        bad_inds = [card_to_idx(c) for c in all_cards if c not in self.hand.cards]
        if lead is not None and \
            any([c.suit == lead.suit for c in self.hand.cards]):
            bad_inds += [card_to_idx(c) for c in all_cards if c.suit != lead.suit]
        obs = np.zeros((self.input_dimensions, 1))
        if lead is not None:
            lead_ind = card_to_idx(lead) + 32
            obs[lead_ind] = 1
        seen_inds = [card_to_idx(c) + 64 for c in self.seen]
        obs[seen_inds] = 1
        hidden_layer_values, probs = apply_neural_nets(obs, self.weights)
        if np.all(probs == 0):
            probs = np.ones_like(probs)
        probs[0,bad_inds] = 0
        probs = probs.flatten() / np.sum(probs)
        ind = np.random.choice(range(self.output_dimensions), p=probs)
        play = idx_to_card[ind]
        self.hand = pq.Hand(cards=deal.tools.get_card(self.hand, str(play))[0])
        return play

    def trim(self):
        if len(self.episode_rewards) > self.memory:
            self.episode_hidden_layer_values = \
                self.episode_hidden_layer_values[-self.memory:]
            self.episode_observations = self.episode_observations[-self.memory:]
            self.episode_gradient_log_ps = \
                self.episode_gradient_log_ps[-self.memory:]
            self.episode_rewards = self.episode_rewards[-self.memory:]

    def train(self):

        # To be used with rmsprop algorithm
        # (http://sebastianruder.com/optimizing-gradient-descent/index.html#rmsprop)
        expectation_g_squared = {}
        g_dict = {}
        for layer_name in self.weights.keys():
            expectation_g_squared[layer_name] = \
                np.zeros_like(self.weights[layer_name])
            g_dict[layer_name] = np.zeros_like(self.weights[layer_name])

            p2 = Neural('Twin', weights=self.weights)
            
        for n in range(10000):
            elder = self
            ynger = p2
            for sortie in range(6):
                RoundNeural(elder, ynger, True)
                self.reset()
                p2.reset()
                elder, ynger = ynger, elder

            self.episode_number += 1

            # Combine the following values for the episode
            episode_hidden_layer_values = \
                np.vstack(self.episode_hidden_layer_values)
            episode_observations = np.vstack(self.episode_observations)
            episode_gradient_log_ps = np.vstack(self.episode_gradient_log_ps)
            episode_rewards = np.array(np.vstack(self.episode_rewards),
                                       dtype=np.float64)
            self.trim()

            # Tweak the gradient of the log_ps based on the discounted rewards
            episode_gradient_log_ps_discounted = \
                discount_with_rewards(episode_gradient_log_ps,
                                      episode_rewards, self.gamma)

            gradient = compute_gradient(
              episode_gradient_log_ps_discounted,
              episode_hidden_layer_values,
              episode_observations,
              self.weights
            )

            # Sum the gradient for use when we hit the batch size
            for layer_name in gradient:
                g_dict[layer_name] += gradient[layer_name]

            if self.episode_number % self.batch_size == 0:
                if (self.episode_number/self.batch_size) % 2 == 0:
                    p2 = Neural('Twin', weights=self.weights)
                else:
                    p2 = Neural('Baby')
                update_weights(self.weights, expectation_g_squared, g_dict, \
                               self.decay_rate, self.learning_rate)
                print(self.episode_number, self.score)
                self.score = 0
                
                ofile = open('Neural.pkl', 'wb')
                pkl.dump(self, ofile)
                ofile.close()

if __name__ == '__main__':
    try:
        ifile = open('Neural.pkl', 'rb')
        p1 = pkl.load(ifile)
        ifile.close()
    except FileNotFoundError:
        p1 = Neural('AI')
    if args.play:
        p2 = Human('Hugh Mann')
        pq.Game(p2, p1, False)
    elif args.test:
        p2 = pq.Player('RandBot')
        scores = np.array([pq.Game(p1, p2, True) for i in range(100)])
        print(np.sum(scores, axis=0))
    else:
        p1.train()
