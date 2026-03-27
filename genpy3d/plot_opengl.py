from dataclasses import dataclass
from typing import Callable, Type

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

from genpy3d.axes_opengl import Axes
from genpy3d.color_tables import get_viridis_color, get_grey_color


@dataclass
class Plot_z_of_xy:
    axes: Type[Axes]
    plotfunc: Callable = lambda x, y: 0
    precision: float = 100
    fore_colormap: Callable = get_viridis_color
    back_colormap: Callable = get_grey_color

    def of_function(self, func):
        self.plotfunc = func
        return self

    def _get_color(self, colormap, z):
        z = (z - self.axes.start[2]) / self.axes.extent[2]
        z = max(0, min(z, 1.0))
        return colormap(z)

    def _clip(self):
        # Define 6 clipping planes for the axes cuboid

        print(self.axes.size)
        # x >= 0  →  +x plane
        glClipPlane(GL_CLIP_PLANE0, [1.0, 0.0, 0.0, 0.0])
        glEnable(GL_CLIP_PLANE0)

        # x <= 1  →  -x + 1 >= 0
        glClipPlane(GL_CLIP_PLANE1, [-1.0, 0.0, 0.0, self.axes.size[0]])
        glEnable(GL_CLIP_PLANE1)

        # y >= 0
        glClipPlane(GL_CLIP_PLANE2, [0.0, 1.0, 0.0, 0.0])
        glEnable(GL_CLIP_PLANE2)

        # y <= 1
        glClipPlane(GL_CLIP_PLANE3, [0.0, -1.0, 0.0, self.axes.size[1]])
        glEnable(GL_CLIP_PLANE3)

        # z >= 0
        glClipPlane(GL_CLIP_PLANE4, [0.0, 0.0, 1.0, 0.0])
        glEnable(GL_CLIP_PLANE4)

        # z <= 1
        glClipPlane(GL_CLIP_PLANE5, [0.0, 0.0, -1.0, self.axes.size[2]])
        glEnable(GL_CLIP_PLANE5)

    def _unclip(self):
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)
        glDisable(GL_CLIP_PLANE2)
        glDisable(GL_CLIP_PLANE3)
        glDisable(GL_CLIP_PLANE4)
        glDisable(GL_CLIP_PLANE5)

    def draw(self):
        glColor3f(0.2, 0.7, 1.0)

        step = 0.02
        x_range_min, x_range_max = self.axes.start[0], self.axes.start[0] + self.axes.extent[0]
        y_range_min, y_range_max = self.axes.start[1], self.axes.start[1] + self.axes.extent[1]

        self._clip()

        glEnable(GL_CULL_FACE)

        glCullFace(GL_BACK)

        for x in np.linspace(x_range_min, x_range_max, self.precision):
            glBegin(GL_TRIANGLE_STRIP)
            for y in np.linspace(y_range_min, y_range_max, self.precision):
                z1 = self.plotfunc(x, y)
                z2 = self.plotfunc(x + step, y)

                glColor3f(*self._get_color(self.fore_colormap, z1))
                glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
                glColor3f(*self._get_color(self.fore_colormap, z2))
                glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
            glEnd()

        glCullFace(GL_FRONT)

        for x in np.linspace(x_range_min, x_range_max, self.precision):
            glBegin(GL_TRIANGLE_STRIP)
            for y in np.linspace(y_range_min, y_range_max, self.precision):
                z1 = self.plotfunc(x, y)
                z2 = self.plotfunc(x + step, y)

                glColor3f(*self._get_color(self.back_colormap, z1))
                glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
                glColor3f(*self._get_color(self.back_colormap, z2))
                glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
            glEnd()

        self._unclip()

        glDisable(GL_CULL_FACE)
