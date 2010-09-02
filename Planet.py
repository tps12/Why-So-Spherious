from math import *

class Planet:
    def __init__(self, radius, tile_size, value):
        dtheta = float(tile_size) / radius
        self.row_count = int(pi / dtheta)
        self.row_lengths = [l for l in
                            [int(2 * self.row_count * sin(row * dtheta) + 0.5)
                             for row in range(0,int(pi/dtheta))]
                            if l > 0]
        self.row_count = len(self.row_lengths)
        self.rows = [[value  for i in range(0, row_length)]
                     for row_length in self.row_lengths]
        self.max_row = max(self.row_lengths)
        self.row_offsets = [int((self.max_row - row_length)/2.0 + 0.5)
                            for row_length in self.row_lengths]

    def get_slope(self, row, nrow):
        return float(self.row_lengths[int(nrow)])/self.row_lengths[int(row)]

    def get_adjacent_row(self, row, column, nrow):
        if nrow >= 0 and nrow < self.row_count - 1 and self.row_lengths[int(nrow)]:
            m = self.get_slope(row, nrow)
            start = int(column * m)
            end = int((column + 1) * m) + 1
            if start < 0:
                # do wrapped portion on right and limit start
                for c in range (start, 0):
                    yield (nrow, self.row_lengths[int(nrow)] + c)
                start = 0
            if end > self.row_lengths[nrow]:
                # do wrapped portion on left and limit end
                for c in range(self.row_lengths[int(nrow)], end):
                    yield (nrow, c - self.row_lengths[int(nrow)])
                end = self.row_lengths[int(nrow)]
            for c in range(start, end):
                yield (nrow, c)
    
    def adjacent(self, row, column):
        # wrap left
        if column > 0:
            yield (row, column-1)
        elif self.row_lengths[row] > 1:
            yield (row, self.row_lengths[int(row)]-1)

        # wrap right
        if column < self.row_lengths[int(row)]-1:
            yield (row, column+1)
        elif self.row_lengths[int(row)] > 1:
            yield (row, 0)

        # adjacent rows
        for nrow in (row-1,row+1):
            for adj in self.get_adjacent_row(row, column, nrow):
                yield adj

    def get_coordinates(self, row, column, size=None):
        size = size or (0,0)
        return (column + self.row_offsets[int(row)] - size[0]/2,
                row - size[1]/2)

    def get_row_column(self, x, y, size=None):
        size = size or (0,0)
        row = y + size[1]/2
        return row, x - self.row_offsets[int(row)] + size[0]/2

    def apply_heading(self, v, theta, x, y, size=None):
        row, column = self.get_row_column(x, y, size)

        # vertical component
        vy = v * sin(theta)
        nrow = row + vy
        if nrow < 0:
            nrow = -nrow
        elif nrow >= self.row_count:
            nrow = self.row_count - (nrow - self.row_count)
        m = self.get_slope(row, nrow)
        
        # horizontal component
        vx = v * cos(theta)
        ncolumn = (column + vx) * m
        if ncolumn < 0:
            ncolumn += self.row_lengths[int(nrow)]
        elif ncolumn > self.row_lengths[int(nrow)] - 1:
            ncolumn -= self.row_lengths[int(nrow)]
        x, y = self.get_coordinates(nrow, ncolumn, size)
        return theta, x, y

