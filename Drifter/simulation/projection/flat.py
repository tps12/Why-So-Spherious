from math import *

from numpy import *
from numpy.linalg import *

class FlatProjection(object):
    name = _('Flat')

    def __init__(self, size):
        w, h = size

        self._radius = min(w/2, h)/2
    
    def vector_to_xy(self, v):
        x = self._radius * (v[1] + 1)
        y = self._radius * (1 - v[2])
        if v[0] < 0:
            x = 4 * self._radius - x
        return x, y

    def poly_to_xy_lists(self, vs):
        ps = [self.vector_to_xy(v) for v in vs]
        return [[p for p in ps if p[0] < 2 * self._radius],
                [p for p in ps if p[0] >= 2 * self._radius]]

    def get_background_rows(self):
        rows = []
        r2 = self._radius * self._radius
        for i in range(-self._radius, self._radius):
            d = sqrt(r2 - i*i)
            rows.append([(self._radius - d, d * 2),
                         (3 * self._radius - d, d * 2)])
        return rows

    def _on_side(self, x, y):
        y -= self._radius
        xl = x - self._radius
        if xl * xl + y * y < self._radius * self._radius:
            return -1
        xr = xl - self._radius * 2
        if xr * xr + y * y < self._radius * self._radius:
            return 1
        return 0

    def _xy_to_vector(self, x, y):
        sign = 1
        if x > 2 * self._radius:
            x -= 4 * self._radius
            sign = -1
        v = [0,
             float(sign * x) / self._radius - 1,
             1 - float(y) / self._radius]
        v[0] = sign * sqrt(1 - v[1]*v[1] - v[2]*v[2])
        return tuple(v) 

    def _get_rotation(self, v1, v2):
        th = acos(dot(v1, v2))
        axis = cross(v1, v2)
        axis = axis / norm(axis)
        return th, axis

    def get_xy_rotation(self, x1, y1, x2, y2):
        side1 = self._on_side(x1, y1)
        if side1 and side1 == self._on_side(x2, y2):
            return self._get_rotation(
                self._xy_to_vector(x1, y1),
                self._xy_to_vector(x2, y2))
        return 0, (1,0,0)
