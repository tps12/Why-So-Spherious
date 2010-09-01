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

        if row > 0:
            if self.row_lengths[row] == self.row_lengths[row-1]:
                yield (row-1,column)
            else:
                m = float(self.row_lengths[row-1])/self.row_lengths[row]
                start = (column - self.row_offsets[row]) * m + self.row_offsets[row-1]
                end = (column + 1 - self.row_offsets[row]) * m + self.row_offsets[row-1]
                for c in range(int(start), int(end)):
                    yield (row-1,c)
                
        if row < self.row_count-1:
            if self.row_lengths[row] == self.row_lengths[row+1]:
                yield (row+1,column)
            else:
                m = float(self.row_lengths[row+1])/self.row_lengths[row]
                start = (column - self.row_offsets[row]) * m + self.row_offsets[row+1]
                end = (column + 1 - self.row_offsets[row]) * m + self.row_offsets[row+1]
                for c in range(int(start), int(end)):
                    yield (row+1,c)
