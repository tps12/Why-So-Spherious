from math import *

from projection.sinusoid import SineProjection
from projection.flat import FlatProjection
from util.quat import quat

class Presenter(object):   
    def __init__(self, model, view):
        projections = [SineProjection, FlatProjection]
        
        self._view = view
        self._view.set_projection_options(projections,
                                          self._set_projection)

        self._rotation = quat(1)
        
        self._view.map_size_changed = self.view_map_size_changed
        self._view.map_dragged = self.map_dragged

        self._set_projection(projections[0])

    def run(self):
        while True:
            class Dot:
                color = None
                location = None

            axes = [None for i in range(3)]
            for i in range(3):
                dot = Dot()
                axis = tuple([1 if j == i else 0 for j in range(3)])
                dot.color = tuple([255*c for c in axis])
                dot.location = self._rotate_and_project(axis)
                axes[i] = dot
            
            if self._view.step(axes):
                break

    def _rotate(self, v):
        q = quat(0,v[0],v[1],v[2])
        return ((self._rotation*q)/self._rotation).q[1:4]

    def _set_projection(self, cls):
        self._projection = cls(self._view.map_size)
        self.view_map_size_changed(self._view.map_size)

    def _rotate_and_project(self, v):
        return self._projection.vector_to_xy(self._rotate(v))

    def view_map_size_changed(self, size):
        self._projection = self._projection.__class__(size)
        self._view.fill_background_rows((0,0,128),
                                        self._projection.get_background_rows())

        self._view.draw_controls()

        self._view.paint_background()

    def map_dragged(self, start, end):
        th, u = self._projection.get_xy_rotation(start[0], start[1],
                                                 end[0], end[1])
        x, y, z = [c * sin(th/2) for c in u]
        rot = quat(cos(th/2), x, y, z) * self._rotation
        if not any((isnan(c) for c in rot.q)):
            self._rotation = rot
        self.view_map_size_changed(self._view.map_size)
