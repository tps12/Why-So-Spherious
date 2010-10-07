# Calculations involving great circles based on example code by Chris Veness:
# http://www.movable-type.co.uk/scripts/latlong.html
# Used under a Creative Commons license:
# http://creativecommons.org/licenses/by/3.0/

# Weighted average of points on a sphere uses algorithm by
# Samuel Buss and Jay Fillmore
# http://www.math.ucsd.edu/~sbuss/ResearchWeb/spheremean/paper.pdf

from math import *

class Planet:
    def __init__(self, radius, tile_size, value):
        self.radius = float(radius)
        self.dtheta = tile_size / self.radius
        self.row_count = int(pi / self.dtheta)
        self.row_lengths = [l for l in
                            [int(2 * self.row_count * sin(row * self.dtheta) + 0.5)
                             for row in range(0,int(pi/self.dtheta))]
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
            if end > self.row_lengths[int(nrow)]:
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

    def get_coordinates_from_lat_lon(self, lat, lon, size=None):
        row = lat/-self.dtheta + self.row_count/2
        column = (lon + pi) / (2 * pi) * self.row_lengths[int(row)]
        return self.get_coordinates(row, column, size)

    def get_row_column(self, x, y, size=None):
        size = size or (0,0)
        row = y + size[1]/2
        return row, x - self.row_offsets[int(row)] + size[0]/2

    def get_lat_lon(self, x, y, size=None):
        row, column = self.get_row_column(x, y, size)
        return (-(row - self.row_count/2) * self.dtheta,
                2 * pi * column/self.row_lengths[int(row)] - pi)

    def bearing(self, x1, y1, size1, x2, y2, size2):
        lat1, lon1 = self.get_lat_lon(x1, y1, size1)
        lat2, lon2 = self.get_lat_lon(x2, y2, size2)

        y = sin(lon2-lon1) * cos(lat2)
        x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1)
        return atan2(y, x)

    def midpoint(self, x1, y1, size1, x2, y2, size2, size=None):
        lat1, lon1 = self.get_lat_lon(x1, y1, size1)
        lat2, lon2 = self.get_lat_lon(x2, y2, size2)

        bx = cos(lat2) * cos(lon2 - lon1)
        by = cos(lat2) * sin(lon2 - lon1)
        latm = atan2(sin(lat1) + sin(lat2),
                     sqrt((cos(lat1) + bx)*(cos(lat1) + bx) + by*by))
        lonm = lon1 + atan2(by, cos(lat1) + bx)
        if lonm > pi:
            lonm -= 2*pi
        if lonm < -pi:
            lonm += 2*pi
        
        return self.get_coordinates_from_lat_lon(latm, lonm, size)

    def xy_to_vector(self, x, y, size=None):
        lat, lon = self.get_lat_lon(x, y, size)
        cos_lat = cos(lat)
        return (cos_lat * cos(lon),
                cos_lat * sin(lon),
                sin(lat))

    def vector_to_xy(self, v, size=None):
        lat = atan2(v[2], sqrt(v[0]*v[0] + v[1]*v[1]))
        lon = atan2(v[1], v[0])
        return self.get_coordinates_from_lat_lon(lat, lon, size)

    def magnitude(self, p):
        return sqrt(sum([x*x for x in p]))

    def weighted_average(self, xy_points, weights, sizes, size=None):
        ps = [self.xy_to_vector(xy_points[i][0], xy_points[i][1], sizes[i])
              for i in range(len(xy_points))]
        add_vectors = lambda p1, p2: tuple([p1[i]+p2[i] for i in range(len(p1))])
        vector_diff = lambda p1, p2: tuple([p1[i]-p2[i] for i in range(len(p1))])
        weighted_sum = reduce(
            add_vectors,
            [tuple([weights[i] * c for c in ps[i]]) for i in range(len(ps))])
        q = tuple([x / self.magnitude(weighted_sum) for x in weighted_sum])
        last_u = None
        while True:
            p_stars = []
            for p in ps:
                cos_th = sum([p[i] * q[i] for i in range(len(p))])
                th = acos(cos_th)
                p_stars.append(tuple([c * th / sin(th) for c in p]))
            u = reduce(
                add_vectors,
                [tuple([weights[i] * c
                        for c in vector_diff(p_stars[i], q)])
                 for i in range(len(p_stars))])
            mag_u = self.magnitude(u)
            if mag_u == last_u:
                return self.vector_to_xy(q, size)
            else:
                last_u = mag_u

    def bearing(self, lat1, lon1, lat2, lon2):
        return atan2(sin(lon2-lon1) * cos(lat2),
                     cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1))

    def apply_bearing(self, d, theta, x, y, size=None):
        lat, lon = self.get_lat_lon(x, y, size)

        da = d/self.radius
        lat2 = asin(sin(lat)*cos(da) +
                    cos(lat)*sin(da)*cos(theta))
        lon2 = lon + atan2(sin(theta)*sin(da)*cos(lat),
                           cos(da) - sin(lat)*sin(lat2))
        if lon2 > pi:
            lon2 -= 2*pi
        if lon2 < -pi:
            lon2 += 2*pi

        return (((self.bearing(lat2,lon2,lat,lon) + pi) % (2*pi),) +
                self.get_coordinates_from_lat_lon(lat2, lon2, size))

    def apply_heading(self, v, theta, x, y, size=None):
        row, column = self.get_row_column(x, y, size)
        ntheta = theta

        # vertical component
        vy = v * sin(theta)
        nrow = row + vy
        if nrow < 0:
            nrow = -nrow
            ntheta = (theta + pi) % (2 * pi)
        elif nrow >= self.row_count:
            nrow = self.row_count - (nrow - self.row_count)
            ntheta = (theta + pi) % (2 * pi)
        m = self.get_slope(row, nrow)
        
        # horizontal component
        vx = v * cos(theta)
        ncolumn = (column + vx) * m
        if theta != ntheta:
            if ncolumn > self.row_lengths[int(nrow)]/2:
                ncolumn -= self.row_lengths[int(nrow)]/2
            else:
                ncolumn += self.row_lengths[int(nrow)]/2
        if ncolumn < 0:
            ncolumn += self.row_lengths[int(nrow)]
        elif ncolumn > self.row_lengths[int(nrow)] - 1:
            ncolumn -= self.row_lengths[int(nrow)]
        x, y = self.get_coordinates(nrow, ncolumn, size)
        return ntheta, x, y

