from lab5.vec2D import Vec2D


class Entity:
    type = "U"

    def __init__(self, starting_position, board):
        self.position = starting_position
        self.starting_position = starting_position
        self.board = board
        self.alive = True

    def move(self, vec):
        self.position = self.position + vec
        return self.position

    def get_distance_to(self, other):
        return self.position.get_distance_to(other.position)

    def can_move(self, vec):
        return not self.board.is_wall_at(self.position + vec)

    def action(self):
        pass

    def get_hit(self):
        pass

    def finish(self, loser):
        pass
