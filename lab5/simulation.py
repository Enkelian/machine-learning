from lab5.board import Board
from lab5.monster import Monster
from lab5.vec2D import Vec2D
import time, os
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.gridspec as gridspec

from lab5.witcher import Witcher


class Simulation:

    def __init__(self):
        self.board = Board()
        self.monster = Monster(Vec2D(7, 2), self.board, "DETERMINISTIC")
        self.witcher = Witcher(Vec2D(3, 3), self.board, self.monster, cautious=0.9)
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

        self.xs = [[] for _ in range(self.PLOTS_NO)]
        self.ys = [[] for _ in range(self.PLOTS_NO)]
        self.lines = [self.axes[i].plot([], [], 'r')[0] for i in range(self.PLOTS_NO)]
        self.ITERS = 20000
        self.AVG_WINDOW = 100

        ani = FuncAnimation(self.fig, self.update, frames=self.ITERS, init_func=self.init, blit=True, interval=0)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()

    def simulate(self, delay, iters, show=True):
        state1 = self.board.state
        action1 = self.witcher.get_action(state1)
        for i in range(iters):
            # if show:
            #     self.board.print()
            reward, state2 = self.board.resolve_state(show)
            action2 = self.witcher.get_action(state2)
            self.witcher.update_Q(state1, action1, reward, state2, action2)
            for entity in self.board.entities:
                entity.action()
            state1, action1 = state2, action2
            # if show:
            #     time.sleep(delay)
            #     os.system("clear")

    def simulation_step(self, delay, state1, action1, frame, show=False):
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

        starts = [0, 0, -100, 0]
        limits = [200, 4, 100, 1]
        for i in range(self.PLOTS_NO):
            self.axes[i].set_ylim(starts[i], limits[i])

        return self.lines

    def update(self, frame):

        state = self.board.state
        action = self.witcher.get_action(state)
        while not self.board.finished:
            state, action = self.simulation_step(0, state, action, frame)

        if frame % 1000 == 0:
            self.witcher.show_move_heatmap(f'heatmap_{frame}')

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
