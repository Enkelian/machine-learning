from lab5.entity import Entity
from lab5.vec2D import Vec2D
from lab5.action import Action

import random
from collections import defaultdict
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class Witcher(Entity):
    type = "W"
    history = {
        'iterations': [],
        'rewards': [],
        'hits': [],
        'success_probability': []
    }
    success_sum = 0
    game_no = 0

    def __init__(self, starting_position, board, monster, gamma=0.9, alpha=0.1, cautious=0.3, is_sarsa=True):
        super(Witcher, self).__init__(starting_position, board)
        self.possible_moves = {
            Action.RIGHT: Vec2D(1, 0),
            Action.UP: Vec2D(0, 1),
            Action.LEFT: Vec2D(-1, 0),
            Action.DOWN: Vec2D(0, -1)
        }
        self.monster = monster
        self.reward_sum = 0
        self.Q = defaultdict(lambda: np.zeros(len(self.possible_moves) + 1))
        self.gamma = gamma
        self.alpha = alpha
        self.cautious = cautious
        self.moves_heat = np.zeros((self.board.upper_right.x - 1, self.board.upper_right.y - 1))
        self.distance = self.get_distance_to(monster)
        self.move_reward = 0
        self.is_sarsa = is_sarsa

    def perform_attack(self):
        attack = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    attack.append(self.position + Vec2D(i, j))
        self.board.attack_fields(attack)

    def move(self, vec):
        self.moves_heat[(super(Witcher, self).move(vec) - Vec2D(1, 1)).to_tuple()] += 1
        prev_dist = self.distance
        self.distance = self.get_distance_to(self.monster)
        diff = prev_dist - self.distance
        self.move_reward += diff/10

    def action(self):
        self.move_reward = 0
        actions = list(Action)
        next_action = self.get_action((self.position, self.monster.position))
        if next_action == Action.ATTACK:
            self.perform_attack()
        else:
            vec = self.possible_moves[next_action]
            while not self.can_move(vec):
                vec = self.possible_moves[random.choice(actions[1:])]
            self.move(vec)

    def get_action(self, state):
        max = np.argmax(self.Q[state])
        actions = list(Action)
        return random.choice(actions) if self.Q[state][max] == 0 or random.random() > self.cautious else actions[max]

    def get_hit(self):
        self.alive = False
        return -60

    def finish(self, loser):
        self.add_history_entry(loser != self.type)
        self.position = self.starting_position
        self.alive = True
        self.moves_heat = np.zeros((self.board.upper_right.x, self.board.upper_right.y))
        self.reward_sum = 0
        self.move_reward = 0
        self.distance = 0

    def add_history_entry(self, won):
        Witcher.history['iterations'].append(self.board.iteration)
        Witcher.history['hits'].append(self.monster.get_hit_count())
        Witcher.history['rewards'].append(self.reward_sum)
        Witcher.success_sum += won
        Witcher.game_no += 1
        Witcher.history['success_probability'].append(Witcher.success_sum / Witcher.game_no)

    def update_Q(self, state1, action1, reward1, state2, action2):
        self.reward_sum += reward1
        if self.is_sarsa:
            self.Q[state1][action1.value] += \
                self.alpha * (reward1 + self.gamma * self.Q[state2][action2.value] - self.Q[state1][action1.value])
        else:
            self.Q[state1][action1.value] += \
                self.alpha * (reward1 + self.gamma * np.max(self.Q[state2]) - self.Q[state1][action1.value])

    def get_most_visited(self):
        np.max(self.moves_heat)

    def save_move_heatmap(self, name):
        fig = plt.figure(2)
        fig.clf()
        svm = sns.heatmap(self.moves_heat, vmax=self.get_most_visited())
        figure = svm.get_figure()
        figure.savefig(f'{name}.png')
