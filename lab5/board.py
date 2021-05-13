from lab5.vec2D import Vec2D
import sys

from lab5.witcher import Witcher

MAX_ITERS = 1000


class Board:
    def __init__(self, upper_right=Vec2D(8, 7)):
        self.upper_right = upper_right
        self.walls = [upper_right]
        self.entities = []
        self.attacked_fields = []
        self.safe_space = upper_right - Vec2D(1, 1)
        self.iteration = 0
        self.state = None
        self.finished = False
        self.loser = None

        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    self.walls.append(upper_right - Vec2D(i, j))

        for i in range(upper_right.x + 1):
            self.walls.append(Vec2D(i, 0))
            self.walls.append(Vec2D(i, upper_right.y))

        for i in range(upper_right.y + 1):
            self.walls.append(Vec2D(0, i))
            self.walls.append(Vec2D(upper_right.x, i))

    def count_walls_in_dir(self, pos, direction):
        return self.is_wall_at(pos + direction) \
               + self.is_wall_at(pos + Vec2D(direction.x, 0)) \
               + self.is_wall_at(pos + Vec2D(0, direction.y))

    def is_wall_at(self, pos):
        return pos in self.walls

    def is_within_board(self, pos):
        return pos.is_less_eq_than(self.upper_right) and pos.is_more_eq_than(self.lower_left)

    def is_wall_horizontal(self, pos):
        return self.is_wall_at(pos + Vec2D(1, 0)) or self.is_wall_at(pos + Vec2D(-1, 0))

    def is_wall_vertical(self, pos):
        return self.is_wall_at(pos + Vec2D(0, 1)) or self.is_wall_at(pos + Vec2D(0, -1))

    def is_attacked_field(self, pos):
        return pos in self.attacked_fields

    def get_entity_at(self, pos):
        for entity in self.entities:
            if entity.position == pos:
                return entity
        return None

    def print(self):
        board_str = ""
        for x in range(self.upper_right.x + 1):
            for y in range(self.upper_right.y + 1):
                pos = Vec2D(x, y)
                entity = self.get_entity_at(pos)
                c = "-"
                if self.is_wall_at(pos):
                    c = "x"
                elif self.is_attacked_field(pos):
                    c = "*"
                elif entity is not None:
                    c = entity.type
                board_str += c
            board_str += "\n"
        sys.stdout.write("\r{0}".format(board_str))
        sys.stdout.flush()

    def add_entity(self, entity):
        if self.is_wall_at(entity.position):
            return NotImplementedError
        self.entities.append(entity)

    def clear_attacked_fields(self):
        self.attacked_fields.clear()

    def attack_fields(self, fields):
        self.attacked_fields = self.attacked_fields + fields

    def next_state(self):
        self.state = self.get_entity_of_type("W").position, self.get_entity_of_type("M").position
        return self.state

    def resolve_state(self, visible=True):
        reward = 0
        for field in self.attacked_fields:
            entity = self.get_entity_at(field)
            if entity is not None:
                reward += entity.get_hit()

        if self.iteration == MAX_ITERS:
            reward += self.get_entity_of_type("W").get_hit()

        reward += self.get_entity_of_type("W").move_reward

        self.iteration += 1
        self.clear_attacked_fields()
        self.check_if_ended(visible)

        return reward, self.next_state()

    def check_if_ended(self, visible):

        for entity in self.entities:
            if not entity.alive:
                self.loser = entity.type

        if self.loser is not None:
            self.finished = True

        if visible and self.finished:
            print("------------------------ENDED------------------------")
            print(f'LOSER IS {self.loser}')
            print(f'ITERATIONS {self.iteration}')

    def reset_state(self, loser):
        for entity in self.entities:
            entity.finish(loser)
        self.iteration = 0
        self.clear_attacked_fields()
        self.loser = None
        self.finished = False

    def are_entities_near(self):
        return self.get_entities_distance().is_small()

    def get_entities_distance(self):
        return self.entities[0].position - self.entities[1].position

    def get_entity_of_type(self, entity_type):
        for entity in self.entities:
            if entity.type == entity_type:
                return entity

    def get_size(self):
        return self.upper_right.x * self.upper_right.y
