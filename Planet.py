from math import *

class Planet:
    def __init__(self, radius, tile_size, value):
        dtheta = float(tile_size) / radius
        self.row_count = int(pi / dtheta)
        self.row_lengths = [int(2 * self.row_count * sin(row * dtheta) + 0.5)
                            for row in range(0,self.row_count)]
        self.rows = [[value for i in range(0, row_length)]
                     for row_length in self.row_lengths]
        self.max_row = max(self.row_lengths)
        self.row_offsets = [int((self.max_row - row_length)/2.0 + 0.5)
                            for row_length in self.row_lengths]
        

    def adjacent(self, row, column):
        # wrap left
        if column > 0:
            yield (row, column-1)
        elif self.row_lengths[row] > 1:
            yield (row, self.row_lengths[row]-1)

        # wrap right
        if column < self.row_lengths[row]-1:
            yield (row, column+1)
        elif self.row_lengths[row] > 1:
            yield (row, 0)

        # adjacent rows
        for nrow in (row-1,row+1):
            if self.row_lengths[nrow]:
                m = float(self.row_lengths[nrow])/self.row_lengths[row]
                start = int(column * m)
                end = int((column + 1) * m)
                end = end + 1 if end == start else end
                if start < 0:
                    for c in range (start, 0):
                        yield (nrow, self.row_lengths[nrow] + c)
                    start = 0
                if end > self.row_lengths[nrow]:
                    for c in range(self.row_lengths[nrow], end):
                        yield (nrow, c - self.row_lengths[nrow])
                    end = self.row_lengths[nrow]
                for c in range(start, end):
                    yield (nrow, c)
