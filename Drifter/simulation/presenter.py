from math import *

from landmass.layer import Layer
from projection.sinusoid import SineProjection
from projection.flat import FlatProjection
from shapes.dot import Dot
from shapes.shape import Shape
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
            axes = [None for i in range(3)]
            for i in range(3):
                axis = tuple([1 if j == i else 0 for j in range(3)])
                axes[i] = Dot(tuple([255*c for c in axis]),
                              self._rotate_and_project(axis))

            layer = Layer([(0.2,pi/4),
                           (0.1,pi/2),
                           (0.2,5*pi/8),
                           (0.25,7*pi/8),
                           (0.25,pi),
                           (0.15,3*pi/4),
                           (0.1,5*pi/4),
                           (0.3,5*pi/4),
                           (0.2,3*pi/2),
                           (0.15,7*pi/4)])

            ps = layer.project((1,0,0),(0.99,0.01,0))
            for s in self._rotate_and_project_poly(ps):
                x, y = self._view.map_size
                for p in s:
                    x = min(x, p[0])
                    y = min(y, p[1])
                s.append(s[0])
                shapes = [Shape((0,200,200), (x,y),
                                [(p[0]-x,p[1]-y) for p in s])]
            
            if self._view.step(axes, shapes):
                break

    def _rotate(self, v):
        q = quat(0,v[0],v[1],v[2])
        return ((self._rotation*q)/self._rotation).q[1:4]

    def _set_projection(self, cls):
        self._projection = cls(self._view.map_size)
        self.view_map_size_changed(self._view.map_size)

    def _rotate_and_project(self, v):
        return self._projection.vector_to_xy(self._rotate(v))

    def _rotate_and_project_poly(self, vs):
        return self._projection.poly_to_xy_lists([self._rotate(v) for v in vs])

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
