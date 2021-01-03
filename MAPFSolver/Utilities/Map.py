class Map:
    def __init__(self, h, w, obstacles):
        self._h = h
        self._w = w
        self._obstacles_xy = obstacles

    def neighbours(self, xy):
        x, y = xy
        neighbours = []
        if x > 0 and not (x-1, y) in self._obstacles_xy:
            neighbours.append((x-1, y))
        if x < self._w-1 and not (x+1, y) in self._obstacles_xy:
            neighbours.append((x+1, y))
        if y > 0 and not (x, y-1) in self._obstacles_xy:
            neighbours.append((x, y-1))
        if y < self._h-1 and not (x, y+1) in self._obstacles_xy:
            neighbours.append((x, y+1))

        return neighbours

    def get_height(self):
        return self._h

    def get_width(self):
        return self._w

    def get_obstacles_xy(self):
        return self._obstacles_xy

    def is_obstacle(self, pos):
        return pos in self._obstacles_xy

    def __str__(self):
        return "Map(h=" + str(self._h) + ", w=" + str(self._w) + ", obstacles=" + str(self._obstacles_xy) + ")"
