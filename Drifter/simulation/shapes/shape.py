class Shape(object):
    def __init__(self, color, location, points):
        self.color = color
        self.location = location
        self.points = points
        self.width = self.height = 0
        for p in self.points:
            self.width = max(self.width, p[0])
            self.height = max(self.height, p[1])
