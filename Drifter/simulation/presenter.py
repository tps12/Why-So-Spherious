from math import *

from projection.sinusoid import SineProjection
from projection.flat import FlatProjection
from util.quat import quat

class Presenter(object):   
    def __init__(self, model, view):
        self._view = view
        self._view.set_projection_options([SineProjection, FlatProjection],
                                          lambda p: None)

        self._rotation = quat(1)
        
        self._view.map_size_changed = self.view_map_size_changed
        self.view_map_size_changed(self._view.map_size)

        self._view.map_dragged = self.map_dragged

    def run(self):
        while True:
            if self._view.step():
                break

    def _rotate(self, v):
        q = quat(0,v[0],v[1],v[2])
        return ((self._rotation*q)/self._rotation).q[1:4]

    def view_map_size_changed(self, size):
        self._projection = SineProjection(size)
        self._view.fill_background_rows((0,0,128),
                                        self._projection.get_background_rows())
        for i in range(3):
            axis = tuple([1 if j == i else 0 for j in range(3)])
            color = tuple([255*c for c in axis])
            self._view.draw_dot(color,
                                self._projection.vector_to_xy(self._rotate(axis)))

        self._view.draw_controls()

    def map_dragged(self, start, end):
        th, u = self._projection.get_xy_rotation(start[0], start[1],
                                                 end[0], end[1])
        x, y, z = [c * sin(th/2) for c in u]
        rot = quat(cos(th/2), x, y, z) * self._rotation
        if not any((isnan(c) for c in rot.q)):
            self._rotation = rot
        self.view_map_size_changed(self._view.map_size)
