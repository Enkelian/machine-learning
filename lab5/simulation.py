import os
import time

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from lab5.board import Board
from lab5.monster import Monster
from lab5.vec2D import Vec2D
from lab5.witcher import Witcher

modes = {
    'det': {    #in Q-learning gives 0.99 success probability for deterministic
        'g': 0.9,
        'a': 1,
        'c': 1
    },
    'cat': {    #in sarsa 0.96 success probability for stochastic
        'g': 0.9,
        'a': 0.1,
        'c': 0.99
    },
    'exp': {  # reached 0.9 in Q learning stochastic, 0.88 in sarsa
        'g': 0.7,
        'a': 0.5,
        'c': 0.95
    },
    'cat2': {   #in sarsa 0.94 success probability for stochastic
        'g': 0.9,
        'a': 0.01,
        'c': 0.99
    },
    'exp2': {    #sarsa 0.86 and slowly increasing,
        'g': 0.1,
        'a': 0.9,
        'c': 0.98
    },
    'exp3': {   #sarsa
        'g': 0.2,
        'a': 0.5,
        'c': 0.95
    },
    'exp4': {
        'g': 0.4,
        'a': 0.5,
        'c': 0.95
    }
}
m = 'exp'
is_sarsa = False
monster_mode = "STOCHASTIC"
class Simulation:
    def __init__(self):
        self.board = Board(upper_right=Vec2D(10, 9))
        self.monster = Monster(Vec2D(7, 5), self.board, monster_mode)
        self.witcher = Witcher(Vec2D(3, 3), self.board, self.monster,
                               gamma=modes[m]['g'], alpha=modes[m]['a'], cautious=modes[m]['c'], is_sarsa=is_sarsa)
        self.board.add_entity(self.monster)
        self.board.add_entity(self.witcher)
        self.history = []
        self.PLOTS_NO = len(Witcher.history)
        self.fig = plt.figure(1, constrained_layout=True)

        spec = gridspec.GridSpec(ncols=1, nrows=self.PLOTS_NO, figure=self.fig)
        self.axes = []

        for i in range(self.PLOTS_NO):
            self.axes.append(self.fig.add_subplot(spec[i, 0]))
            self.axes[i].title.set_text(list(Witcher.history.keys())[i])
        self.fig.suptitle(f'gamma={modes[m]["g"]}, alpha={modes[m]["a"]}, cautious={modes[m]["c"]}, is_sarsa={is_sarsa}', fontsize=16)

        self.xs = [[] for _ in range(self.PLOTS_NO)]
        self.ys = [[] for _ in range(self.PLOTS_NO)]
        self.lines = [self.axes[i].plot([], [], 'r')[0] for i in range(self.PLOTS_NO)]
        self.ITERS = 4000
        self.AVG_WINDOW = 50
        self.SHOW_LAST = 5
        self.SAVE = 50

        ani = FuncAnimation(self.fig, self.update, frames=self.ITERS, init_func=self.init, blit=True, interval=0)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()

    def simulation_step(self, state1, action1, frame, show=False, delay=0.3):
        if show:
            self.board.print()
        reward, state2 = self.board.resolve_state(show)
        action2 = self.witcher.get_action(state2)
        self.witcher.update_Q(state1, action1, reward, state2, action2)
        for entity in self.board.entities:
            entity.action()

        if show:
            time.sleep(delay)
            os.system("clear")
        return state2, action2

    def init(self):
        for i in range(self.PLOTS_NO):
            self.axes[i].set_xlim(1, self.ITERS)

        starts = [0, -60, 0, 0]
        limits = [300, 100, 4, 1]
        for i in range(self.PLOTS_NO):
            self.axes[i].set_ylim(starts[i], limits[i])

        return self.lines

    def update(self, frame):

        show = frame > self.ITERS - self.SHOW_LAST
        state = self.board.state
        action = self.witcher.get_action(state)
        while not self.board.finished:
            state, action = self.simulation_step(state, action, frame, show=show)

        if frame == self.ITERS - self.SAVE:
            self.fig.savefig(f'stats{os.sep}is_sarsa_{is_sarsa}_monster_mode_{monster_mode}_mode_{m}')

        if frame % 500 == 0 or (frame < 100 and frame % 10 == 0):
            self.witcher.save_move_heatmap(f'moves{os.sep}heatmap_is_sarsa_{is_sarsa}_monster_mode_{monster_mode}_mode_{m}_frame_{frame}')

        self.board.reset_state(self.board.loser)

        for i in range(self.PLOTS_NO):
            self.xs[i].append(frame)

        i = 0
        for stat_type in Witcher.history:
            to_avg = Witcher.history[stat_type] if frame < self.AVG_WINDOW else Witcher.history[stat_type][
                                                                                -self.AVG_WINDOW:]
            self.ys[i].append(np.average(to_avg))
            i += 1

        for i in range(self.PLOTS_NO):
            self.lines[i].set_data(self.xs[i], self.ys[i])

        return self.lines
