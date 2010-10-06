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

    def midpoint(self, x1, y1, size1, x2, y2, size2, size=None):
        lat1, lon1 = self.get_lat_lon(x1, y1, size1)
        lat2, lon2 = self.get_lat_lon(x2, y2, size2)
        return self.get_coordinates_from_lat_lon(
            (lat1 + lat2)/2, (lon1 + lon2)/2, size)

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

