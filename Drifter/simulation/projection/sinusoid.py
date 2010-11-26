from math import *

from numpy import *
from numpy.linalg import *

class SineProjection(object):
    name = _('Sinusoidal')

    def __init__(self, size):
        w, h = size

        self.dtheta = pi / min(w/2, h)
        self.row_count = int(pi / self.dtheta)
        self.row_lengths = [l for l in
                            [int(2 * self.row_count * sin(row * self.dtheta) + 0.5)
                             for row in range(0,int(pi/self.dtheta))]
                            if l > 0]
        self.row_count = len(self.row_lengths)
        self.max_row = max(self.row_lengths)
        self.row_offsets = [int((self.max_row - row_length)/2.0 + 0.5)
                            for row_length in self.row_lengths]
    
    def get_coordinates(self, row, column):
        return (column + self.row_offsets[int(row)],
                row)

    def get_coordinates_from_lat_lon(self, lat, lon):
        row = min(lat/-self.dtheta + self.row_count/2, self.row_count-1)
        column = (lon + pi) / (2 * pi) * self.row_lengths[int(row)]
        return self.get_coordinates(row, column)

    def vector_to_xy(self, v):
        lat = atan2(v[2], sqrt(v[0]*v[0] + v[1]*v[1]))
        lon = atan2(v[1], v[0])
        return self.get_coordinates_from_lat_lon(lat, lon)

    def _wrap(self, v1, v2):
        # projection wraps if projected midpoint far from midpoint of projections
        th, axis = self.get_rotation(v1, v2)
        mid = self._rotate(v1, axis, th/2)

        p1, m, p2 = [self.vector_to_xy(v) for v in (v1, mid, v2)]
        return abs((p1[0]+p2[0])/2 - m[0]) > self.max_row / 100.0
        
    def _rotate(self, p, axis, theta):
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
        L2 = sum([i*i for i in axis])
        return array([(axis[0]*sum(p * axis) +
                       (p[0]*(axis[1]*axis[1]+axis[2]*axis[2]) +
                        axis[0]*(-axis[1]*p[1]-axis[2]*p[2])) * cos(theta) +
                       sqrt(L2)*(-axis[2]*p[1]+axis[1]*p[2]) * sin(theta))/L2,
                      (axis[1]*sum(p * axis) +
                       (p[1]*(axis[0]*axis[0]+axis[2]*axis[2]) +
                        axis[1]*(-axis[0]*p[0]-axis[2]*p[2])) * cos(theta) +
                       sqrt(L2)*(axis[2]*p[0]-axis[0]*p[2]) * sin(theta))/L2,
                      (axis[2]*sum(p * axis) +
                       (p[2]*(axis[0]*axis[0]+axis[1]*axis[1]) +
                        axis[2]*(-axis[0]*p[0]-axis[1]*p[1])) * cos(theta) +
                       sqrt(L2)*(-axis[1]*p[0]+axis[0]*p[1]) * sin(theta))/L2])

    def poly_to_xy_lists(self, vs):
        ps = []
        last = None
        for v in vs:
            if last is not None:
                if self._wrap(last, v):
                    ps.append([self.vector_to_xy(v)])
                else:
                    ps[-1].append(self.vector_to_xy(v))
            else:
                ps.append([self.vector_to_xy(v)])
            last = v
        return ps

    def get_row_column(self, x, y):
        row = y
        return (row,
                x - self.row_offsets[int(row)]
                if 0 <= row < self.row_count else None)

    def in_projection(self, x, y):
        row, column = self.get_row_column(x, y)
        return (0 <= row < self.row_count and
                0 <= column < self.row_lengths[int(row)])

    def get_lat_lon(self, x, y):
        row, column = self.get_row_column(x, y)
        return (-(row - self.row_count/2) * self.dtheta,
                2 * pi * column/self.row_lengths[int(row)] - pi)

    def xy_to_vector(self, x, y):
        lat, lon = self.get_lat_lon(x, y)
        cos_lat = cos(lat)
        return (cos_lat * cos(lon),
                cos_lat * sin(lon),
                sin(lat))

    def get_rotation(self, v1, v2):
        th = acos(dot(v1, v2))
        axis = cross(v1, v2)
        axis = axis / norm(axis)
        return th, axis

    def get_xy_rotation(self, x1, y1, x2, y2):
        if self.in_projection(x1, y1) and self.in_projection(x2, y2):
            return self.get_rotation(
                self.xy_to_vector(x1, y1),
                self.xy_to_vector(x2, y2))
        else:
            return 0, (1,0,0)

    def get_background_rows(self):
        return [[(self.row_offsets[i], self.row_lengths[i])]
                 for i in range(self.row_count)]
