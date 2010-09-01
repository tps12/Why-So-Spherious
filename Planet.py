from math import *

class Planet:
    def __init__(self, radius, tile_size):
        dtheta = float(tile_size) / radius
        self.row_count = int(pi / dtheta)
        self.row_lengths = [int(2 * self.row_count * sin(row * dtheta) + 0.5)
                            for row in range(0,self.row_count)]
        self.rows = [[0 for i in range(0, row_length)]
                     for row_length in self.row_lengths]
        self.max_row = max(self.row_lengths)
        self.row_offsets = [int((self.max_row - row_length)/2.0 + 0.5)
                            for row_length in self.row_lengths]
        
