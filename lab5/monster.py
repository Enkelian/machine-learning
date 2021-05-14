from lab5.entity import Entity
from lab5.vec2D import Vec2D
import random


class Monster(Entity):
    type = "M"
    max_health = 3
    max_cooldown = 4

    def __init__(self, starting_position, board, mode="DETERMINISTIC"):
        super(Monster, self).__init__(starting_position, board)
        self.possible_moves = [Vec2D(-1, -1), Vec2D(1, -1), Vec2D(-1, 1), Vec2D(1, 1)]
        self.move_vec = self.possible_moves[0]
        self.current_mode = mode
        self.action_counter = 0
        self.health = Monster.max_health
        self.idle = False
        self.cooldown_count = Monster.max_cooldown

    def deterministic_move(self):
        new_position = self.position + self.move_vec

        walls_count = self.board.count_walls_in_dir(self.position, self.move_vec)

        if walls_count == 1 or walls_count == 3:
            self.move_vec = self.move_vec.times_scalar(-1)
        elif self.board.is_wall_at(new_position):
            if self.board.is_wall_vertical(new_position):
                self.move_vec = Vec2D(-self.move_vec.x, self.move_vec.y)
            elif self.board.is_wall_horizontal(new_position):
                self.move_vec = Vec2D(self.move_vec.x, -self.move_vec.y)

        self.move(self.move_vec)

    def stochastic_move(self):
        self.move_vec = random.choice(self.possible_moves)
        if self.can_move(self.move_vec):
            self.move(self.move_vec)
        else:
            self.stochastic_move()

    def perform_attack(self):
        attack = [self.position + Vec2D(self.move_vec.x, 0), self.position + Vec2D(-self.move_vec.x, 0)]
        self.board.attack_fields(attack)

    def action(self):
        if self.idle:
            self.cooldown_count -= 1
            self.activate_if_possible()
            return

        if self.current_mode == "DETERMINISTIC":
            if self.action_counter < 2:
                self.deterministic_move()
                self.action_counter += 1
            else:
                self.perform_attack()
                self.action_counter = 0
        else:
            if random.random() > 0.33:
                self.stochastic_move()
            else:
                self.perform_attack()

    def get_hit_count(self):
        res = Monster.max_health - self.health
        self.health = Monster.max_health
        return res

    def get_hit(self):
        self.health -= 1
        # print(f'MONSTER HIT. HEALTH={self.health}')
        self.idle = True
        if self.health == 0:
            self.alive = False
            # return 100
        self.position = self.board.safe_space
        return 10

    def activate_if_possible(self):
        if self.cooldown_count == 0:
            self.idle = False
            self.cooldown_count = self.max_cooldown
            self.teleport()

    def teleport(self):
        self.position = self.starting_position
        self.move_vec = self.possible_moves[0]
        while not self.board.are_entities_near():
            self.deterministic_move()

    def finish(self, loser):
        self.move_vec = self.possible_moves[0]
        self.position = self.starting_position
        self.alive = True
