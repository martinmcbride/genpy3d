import math
from dataclasses import dataclass
from typing import Callable, Type

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from genpy3d.axes_opengl import Axes
from genpy3d.color_tables import get_viridis_color, get_grey_color


@dataclass
class Plot_z_of_xy:
    axes: Type[Axes]
    precision: float = 100
    grid = False
    grid_color = (0.3, 0.3, 0.3)
    line_radius = 0.004
    grid_precision=500
    fore_colormap: Callable = get_viridis_color
    back_colormap: Callable = get_grey_color
    plotfunc: Callable = lambda x, y: 0
    x_grid_count: int = 20
    y_grid_count: int = 20

    def __post_init__(self):
        self.x_range_min, self.x_range_max = self.axes.start[0], self.axes.start[0] + self.axes.extent[0]
        self.y_range_min, self.y_range_max = self.axes.start[1], self.axes.start[1] + self.axes.extent[1]

    def of_function(self, func, grid_color=get_viridis_color, back_color=get_grey_color, precision=100):
        self.plotfunc = func
        self.grid_color = grid_color
        self.back_color = back_color
        self.precision = precision
        return self

    def with_grid(self, x_grid_count=20, y_grid_count=20, grid_color=(0.3, 0.3, 0.3), line_radius=0.004, grid_precision=500):
        self.grid = True
        self.x_grid_count = x_grid_count
        self.y_grid_count = y_grid_count
        self.grid_color = grid_color
        self.line_radius = line_radius
        self.grid_precision = grid_precision
        return self

    def _get_color(self, colormap, z):
        z = (z - self.axes.start[2]) / self.axes.extent[2]
        z = max(0, min(z, 1.0))
        return colormap(z)

    def _clip(self):
        # Define 6 clipping planes for the axes cuboid

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

    def _draw_cylinder(self, p1, p2):
        """Draw a cylinder from p1 to p2"""
        # Vector from p1 to p2
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)

        if length == 0:
            return

        # Save current matrix
        glPushMatrix()
        glTranslatef(*p1)

        # Compute rotation axis and angle
        import numpy as np
        axis = np.cross([0, 0, 1], [dx, dy, dz])
        angle = math.degrees(math.acos(dz / length)) if length != 0 else 0

        if np.linalg.norm(axis) > 1e-6:
            glRotatef(angle, *axis)

        # Draw cylinder along z-axis
        quad = gluNewQuadric()
        gluCylinder(quad, self.line_radius, self.line_radius, length, 8, 1)
        gluDeleteQuadric(quad)

        glPopMatrix()

    def _plot_surface(self):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        step = (self.x_range_max - self.x_range_min) / (self.precision - 1)
        for x in np.linspace(self.x_range_min, self.x_range_max, self.precision):
            glBegin(GL_TRIANGLE_STRIP)
            for y in np.linspace(self.y_range_min, self.y_range_max, self.precision):
                z1 = self.plotfunc(x, y)
                z2 = self.plotfunc(x + step, y)

                glColor3f(*self._get_color(self.fore_colormap, z1))
                glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
                glColor3f(*self._get_color(self.fore_colormap, z2))
                glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
            glEnd()

        glCullFace(GL_FRONT)

        for x in np.linspace(self.x_range_min, self.x_range_max, self.precision):
            glBegin(GL_TRIANGLE_STRIP)
            for y in np.linspace(self.y_range_min, self.y_range_max, self.precision):
                z1 = self.plotfunc(x, y)
                z2 = self.plotfunc(x + step, y)

                glColor3f(*self._get_color(self.back_colormap, z1))
                glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
                glColor3f(*self._get_color(self.back_colormap, z2))
                glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
            glEnd()

        glDisable(GL_CULL_FACE)

    def _plot_lines(self):
        if self.grid:
            glColor3f(self.grid_color[0], self.grid_color[1], self.grid_color[1])
            for x in np.linspace(self.x_range_min, self.x_range_max, self.x_grid_count):
                points = []
                for y in np.linspace(self.y_range_min, self.y_range_max, 500):
                    z = self.plotfunc(x, y)
                    points.append(self.axes.transform_from_graph((x, y, z)))
                for i in range(len(points) - 1):
                    self._draw_cylinder(points[i], points[i + 1])

            for y in np.linspace(self.y_range_min, self.y_range_max, self.y_grid_count):
                points = []
                for x in np.linspace(self.x_range_min, self.x_range_max, 500):
                    z = self.plotfunc(x, y)
                    points.append(self.axes.transform_from_graph((x, y, z)))
                for i in range(len(points) - 1):
                    self._draw_cylinder(points[i], points[i + 1])


    def draw(self):
        self._clip()
        self._plot_surface()
        self._plot_lines()
        self._unclip()
# 
# 
# @dataclass
# class Plot_xyz_of_uv:
#     axes: Type[Axes]
#     precision: float = 100
#     grid = False
#     grid_color = (0.3, 0.3, 0.3)
#     line_radius = 0.004
#     grid_precision=500
#     fore_colormap: Callable = get_viridis_color
#     back_colormap: Callable = get_grey_color
#     plotfunc_x: Callable = lambda x, y: 0
#     plotfunc_y: Callable = lambda x, y: 0
#     plotfunc_z: Callable = lambda x, y: 0
#     extent_u = (0, 1)
#     extent_v = (0, 1)
#     x_grid_count: int = 20
#     y_grid_count: int = 20
# 
#     def of_function(self, func_x, func_y, func_z, extent_u=(0, 1), extent_v=(0, 1), grid_color=get_viridis_color, back_color=get_grey_color, precision=100):
#         self.plotfunc_x = func_x
#         self.plotfunc_y = func_y
#         self.plotfunc_z = func_z
#         self.extent_u = extent_u
#         self.extent_v = extent_v
#         self.grid_color = grid_color
#         self.back_color = back_color
#         self.precision = precision
#         return self
# 
#     def with_grid(self, x_grid_count=20, y_grid_count=20, grid_color=(0.3, 0.3, 0.3), line_radius=0.004, grid_precision=500):
#         self.grid = True
#         self.x_grid_count = x_grid_count
#         self.y_grid_count = y_grid_count
#         self.grid_color = grid_color
#         self.line_radius = line_radius
#         self.grid_precision = grid_precision
#         return self
# 
#     def _get_color(self, colormap, z):
#         z = (z - self.axes.start[2]) / self.axes.extent[2]
#         z = max(0, min(z, 1.0))
#         return colormap(z)
# 
#     def _clip(self):
#         # Define 6 clipping planes for the axes cuboid
# 
#         # x >= 0  →  +x plane
#         glClipPlane(GL_CLIP_PLANE0, [1.0, 0.0, 0.0, 0.0])
#         glEnable(GL_CLIP_PLANE0)
# 
#         # x <= 1  →  -x + 1 >= 0
#         glClipPlane(GL_CLIP_PLANE1, [-1.0, 0.0, 0.0, self.axes.size[0]])
#         glEnable(GL_CLIP_PLANE1)
# 
#         # y >= 0
#         glClipPlane(GL_CLIP_PLANE2, [0.0, 1.0, 0.0, 0.0])
#         glEnable(GL_CLIP_PLANE2)
# 
#         # y <= 1
#         glClipPlane(GL_CLIP_PLANE3, [0.0, -1.0, 0.0, self.axes.size[1]])
#         glEnable(GL_CLIP_PLANE3)
# 
#         # z >= 0
#         glClipPlane(GL_CLIP_PLANE4, [0.0, 0.0, 1.0, 0.0])
#         glEnable(GL_CLIP_PLANE4)
# 
#         # z <= 1
#         glClipPlane(GL_CLIP_PLANE5, [0.0, 0.0, -1.0, self.axes.size[2]])
#         glEnable(GL_CLIP_PLANE5)
# 
#     def _unclip(self):
#         glDisable(GL_CLIP_PLANE0)
#         glDisable(GL_CLIP_PLANE1)
#         glDisable(GL_CLIP_PLANE2)
#         glDisable(GL_CLIP_PLANE3)
#         glDisable(GL_CLIP_PLANE4)
#         glDisable(GL_CLIP_PLANE5)
# 
#     def _draw_cylinder(self, p1, p2):
#         """Draw a cylinder from p1 to p2"""
#         # Vector from p1 to p2
#         dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
#         length = math.sqrt(dx * dx + dy * dy + dz * dz)
# 
#         if length == 0:
#             return
# 
#         # Save current matrix
#         glPushMatrix()
#         glTranslatef(*p1)
# 
#         # Compute rotation axis and angle
#         import numpy as np
#         axis = np.cross([0, 0, 1], [dx, dy, dz])
#         angle = math.degrees(math.acos(dz / length)) if length != 0 else 0
# 
#         if np.linalg.norm(axis) > 1e-6:
#             glRotatef(angle, *axis)
# 
#         # Draw cylinder along z-axis
#         quad = gluNewQuadric()
#         gluCylinder(quad, self.line_radius, self.line_radius, length, 8, 1)
#         gluDeleteQuadric(quad)
# 
#         glPopMatrix()
# 
#     def _plot_surface(self):
#         glEnable(GL_CULL_FACE)
#         glCullFace(GL_BACK)
# 
#         step = (self.x_range_max - self.x_range_min) / (self.precision - 1)
#         for x in np.linspace(self.x_range_min, self.x_range_max, self.precision):
#             glBegin(GL_TRIANGLE_STRIP)
#             for y in np.linspace(self.y_range_min, self.y_range_max, self.precision):
#                 z1 = self.plotfunc(x, y)
#                 z2 = self.plotfunc(x + step, y)
# 
#                 glColor3f(*self._get_color(self.fore_colormap, z1))
#                 glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
#                 glColor3f(*self._get_color(self.fore_colormap, z2))
#                 glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
#             glEnd()
# 
#         glCullFace(GL_FRONT)
# 
#         for x in np.linspace(self.x_range_min, self.x_range_max, self.precision):
#             glBegin(GL_TRIANGLE_STRIP)
#             for y in np.linspace(self.y_range_min, self.y_range_max, self.precision):
#                 z1 = self.plotfunc(x, y)
#                 z2 = self.plotfunc(x + step, y)
# 
#                 glColor3f(*self._get_color(self.back_colormap, z1))
#                 glVertex3f(*self.axes.transform_from_graph((x, y, z1)))
#                 glColor3f(*self._get_color(self.back_colormap, z2))
#                 glVertex3f(*self.axes.transform_from_graph((x + step, y, z2)))
#             glEnd()
# 
#         glDisable(GL_CULL_FACE)
# 
#     def _plot_lines(self):
#         if self.grid:
#             glColor3f(self.grid_color[0], self.grid_color[1], self.grid_color[1])
#             for x in np.linspace(self.x_range_min, self.x_range_max, self.x_grid_count):
#                 points = []
#                 for y in np.linspace(self.y_range_min, self.y_range_max, 500):
#                     z = self.plotfunc(x, y)
#                     points.append(self.axes.transform_from_graph((x, y, z)))
#                 for i in range(len(points) - 1):
#                     self._draw_cylinder(points[i], points[i + 1])
# 
#             for y in np.linspace(self.y_range_min, self.y_range_max, self.y_grid_count):
#                 points = []
#                 for x in np.linspace(self.x_range_min, self.x_range_max, 500):
#                     z = self.plotfunc(x, y)
#                     points.append(self.axes.transform_from_graph((x, y, z)))
#                 for i in range(len(points) - 1):
#                     self._draw_cylinder(points[i], points[i + 1])
# 
# 
#     def draw(self):
#         self._clip()
#         self._plot_surface()
#         self._plot_lines()
#         self._unclip()
