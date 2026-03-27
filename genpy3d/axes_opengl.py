import math
from dataclasses import dataclass

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def _draw_arrow(x,y,z,color):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x,y,z)

    if x != 0:
        glRotatef(90,0,1,0)
    elif y != 0:
        glRotatef(-90,1,0,0)

    glutSolidCone(0.08,0.2,30,30)
    glPopMatrix()

@dataclass
class Axes:
    start: tuple = (0, 0, 0) # (x, y, z) origin in user space
    extent: tuple = (1, 1, 1) # (x, y, z) extent of axes in user space
    size: tuple = (1, 1, 1) # (x, y, z) size of axes in device space
    divs: tuple = (0.2, 0.2, 0.2) # (x, y, z) divisions in use space
    text_offset: tuple = ((0.03, 0.06, 0), (0.12, 0.03, 0), (0.03, 0.06, 0))
    axis_text_offset: tuple = ((0.03, 0.18, 0), (0.18, 0.03, 0), (0.03, 0.18, 0))
    axis_colors: tuple = ((0.4, 0.4, 0.4),)*3
    axis_line_width: float = 3
    div_colors: tuple = ((0.6, 0.6, 0.6),)*3
    div_line_width: float = 3
    reverse_axis: tuple = (False, False, False)

    def of_start(self, start):
        self.start = start
        return self

    def of_extent(self, extent):
        self.extent = extent
        return self

    def of_divs(self, divs):
        self.divs = divs
        return self

    def of_size(self, size):
        self.size = size
        return self

    def transform_from_graph(self, point):
        return [((self.start[i] + self.extent[i] - point[i]) * self.size[i] / self.extent[i])
                if self.reverse_axis[i] else
                ((point[i] - self.start[i]) * self.size[i] / self.extent[i])
                for i in range(3)]

    def set_axis_style(self, width=4, r=(1, 0, 0), g=(0, 1, 0), b=(0, 0, 1)):
        self.axis_line_width =width
        self.axis_colors = (r, g, b)

    def set_div_style(self, width=3, r=(1, 0.5, 0.5), g=(0.5, 1, 0.5), b=(0.5, 0.5, 1)):
        self.div_line_width =width
        self.div_colors = (r, g, b)

    def _get_device_start(self, axis):
        return 0

    def _get_device_end(self, axis):
        return self.size[axis]

    def _get_divs(self, start, extent, div):
        close = abs(extent/10)
        divs = []
        n = math.ceil(start/div)*div
        while n <= start + extent:
            if abs(n-start) > close and abs(n-(start + extent)) > close:
                divs.append(n)
            n += div
        return divs

    def _draw_backplanes(self):

        glColor3f(0, 0, 0)
        glLineWidth(self.div_line_width)

        glBegin(GL_LINES)

        glColor3f(*self.div_colors[0])
        markers = self._get_divs(self.start[0], self.extent[0], self.divs[0])
        for m in markers:
            pos = self.transform_from_graph((m, self.start[1]+self.extent[1], 0))
            glVertex3f(pos[0], self._get_device_start(1), 0)
            glVertex3f(pos[0], self._get_device_end(1), 0)
            pos = self.transform_from_graph((m, 0, self.start[2]+self.extent[2]))
            glVertex3f(pos[0], 0, self._get_device_start(2))
            glVertex3f(pos[0], 0, self._get_device_end(2))

        glColor3f(*self.div_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glVertex3f(self._get_device_start(0), pos[1], 0)
            glVertex3f(self._get_device_end(0), pos[1], 0)
            pos = self.transform_from_graph((0, m, self.start[2]+self.extent[2]))
            glVertex3f(0, pos[1], self._get_device_start(2))
            glVertex3f(0, pos[1], self._get_device_end(2))

        glColor3f(*self.div_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glVertex3f(0, self._get_device_start(1), pos[2])
            glVertex3f(0, self._get_device_end(1), pos[2])
            pos = self.transform_from_graph((self.start[0]+self.extent[0], 0, m))
            glVertex3f(self._get_device_start(0), 0, pos[2])
            glVertex3f(self._get_device_end(0), 0, pos[2])

        glEnd()

    def _draw_axis_ticks(self):

        tick = 0.03
        glColor3f(0, 0, 0)
        glLineWidth(self.axis_line_width)

        glBegin(GL_LINES)

        glColor3f(*self.axis_colors[0])
        markers = self._get_divs(self.start[0], self.extent[0], self.divs[0])
        for m in markers:
            pos = self.transform_from_graph((m, self.start[1]+self.extent[1], 0))
            glVertex3f(pos[0], self._get_device_end(1), 0)
            glVertex3f(pos[0], self._get_device_end(1)+tick, 0)

        glColor3f(*self.axis_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glVertex3f(self._get_device_end(0), pos[1], 0)
            glVertex3f(self._get_device_end(0)+tick, pos[1], 0)

        glColor3f(*self.axis_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glVertex3f(0, self._get_device_end(1), pos[2])
            glVertex3f(0, self._get_device_end(1)+tick, pos[2])

        glEnd()

    def _draw_axis_labels(self):

        # Draw x tick labels
        glColor3f(*self.axis_colors[0])
        markers = self._get_divs(self.start[0], self.extent[0], self.divs[0])
        for m in markers:
            pos = self.transform_from_graph((m, self.start[1]+self.extent[1], 0))
            glRasterPos3f(pos[0] + self.text_offset[0][0], self._get_device_end(1)  + self.text_offset[0][1], 0)
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        # Draw x axis label
        pos = self.transform_from_graph((self.start[0]+self.extent[0]/2, self.start[1]+self.extent[1], 0))
        glRasterPos3f(pos[0] + self.axis_text_offset[0][0], self._get_device_end(1) + self.axis_text_offset[0][1], 0)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord("X"))

        # Draw Y tick labels
        glColor3f(*self.axis_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glRasterPos3f(self._get_device_end(0) + self.text_offset[1][0], pos[1] + self.text_offset[1][1], 0)
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        # Draw y axis label
        pos = self.transform_from_graph((self.start[0] + self.extent[0], self.start[1] + self.extent[1]/2, 0))
        glRasterPos3f(self._get_device_end(0) + self.axis_text_offset[1][0], pos[1] + self.axis_text_offset[1][1], 0)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord("Y"))

        # Draw z tick labels
        glColor3f(*self.axis_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glRasterPos3f(0, self._get_device_end(1) + self.text_offset[2][1],  pos[2] + self.text_offset[2][2])
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        # Draw z axis label
        pos = self.transform_from_graph((0, self.start[1]+self.extent[1], self.start[2]+self.extent[2]/2))
        glRasterPos3f(0, self._get_device_end(1) + self.axis_text_offset[2][1],  pos[2] + self.axis_text_offset[2][2])
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord("Z"))


    def draw(self):
        glLineWidth(self.axis_line_width)

        glBegin(GL_LINES)

        # X axis
        glColor3f(*self.axis_colors[0])
        glVertex3f(0, 0, 0)
        glVertex3f(self.size[0], 0, 0)
        glVertex3f(0, self.size[1], 0)
        glVertex3f(self.size[0], self.size[1], 0)
        glVertex3f(0, 0, self.size[2])
        glVertex3f(self.size[0], 0, self.size[2])

        # Y axis
        glColor3f(*self.axis_colors[1])
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.size[1], 0)
        glVertex3f(self.size[0], 0, 0)
        glVertex3f(self.size[0], self.size[1], 0)
        glVertex3f(0, 0, self.size[2])
        glVertex3f(0, self.size[1], self.size[2])

        # Z axis
        glColor3f(*self.axis_colors[2])
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.size[2])
        glVertex3f(self.size[0], 0, 0)
        glVertex3f(self.size[0], 0, self.size[2])
        glVertex3f(0, self.size[1], 0)
        glVertex3f(0, self.size[1], self.size[2])

        glEnd()

        self._draw_axis_ticks()
        self._draw_backplanes()
        self._draw_axis_labels()

        # _draw_arrow(self.size[0],0,0,self.colors[0])
        # _draw_arrow(0,self.size[1],0,self.colors[1])
        # _draw_arrow(0,0,self.size[2],self.colors[2])

        draw_surface()

        return self


def get_color(z, z_min, z_max):
    # Normalize z to range [0, 1]
    t = (z - z_min) / (z_max - z_min)

    # Simple gradient: blue → cyan → green → yellow → red
    r = t
    g = 1.0 - abs(t - 0.5) * 2
    b = 1.0 - t

    return r, g, b

def get_back_color(z, z_min, z_max):

    return 0.5, 0.5, 0.5

def clip_unit():
    #glClearColor(0.0, 0.0, 0.0, 1.0)

    # Define 6 clipping planes for the unit cube

    # x >= 0  →  +x plane
    glClipPlane(GL_CLIP_PLANE0, [1.0, 0.0, 0.0, 0.0])
    glEnable(GL_CLIP_PLANE0)

    # x <= 1  →  -x + 1 >= 0
    glClipPlane(GL_CLIP_PLANE1, [-1.0, 0.0, 0.0, 1.0])
    glEnable(GL_CLIP_PLANE1)

    # y >= 0
    glClipPlane(GL_CLIP_PLANE2, [0.0, 1.0, 0.0, 0.0])
    glEnable(GL_CLIP_PLANE2)

    # y <= 1
    glClipPlane(GL_CLIP_PLANE3, [0.0, -1.0, 0.0, 1.0])
    glEnable(GL_CLIP_PLANE3)

    # z >= 0
    glClipPlane(GL_CLIP_PLANE4, [0.0, 0.0, 1.0, 0.0])
    glEnable(GL_CLIP_PLANE4)

    # z <= 1
    glClipPlane(GL_CLIP_PLANE5, [0.0, 0.0, -1.0, 1.0])
    glEnable(GL_CLIP_PLANE5)

def unclip_unit():
    glDisable(GL_CLIP_PLANE0)
    glDisable(GL_CLIP_PLANE1)
    glDisable(GL_CLIP_PLANE2)
    glDisable(GL_CLIP_PLANE3)
    glDisable(GL_CLIP_PLANE4)
    glDisable(GL_CLIP_PLANE5)


def draw_surface():
    def f(x, y):
        return 0.7 - y*0.4*math.sin(20*x)

    glColor3f(0.2, 0.7, 1.0)

    step = 0.02
    range_min, range_max = 0, 1

    clip_unit()

    glEnable(GL_CULL_FACE)

    glCullFace(GL_BACK)

    for x in np.arange(range_min, range_max, step):
        glBegin(GL_TRIANGLE_STRIP)
        for y in np.arange(range_min, range_max, step):
            z1 = f(x, y)
            z2 = f(x + step, y)

            glColor3f(*get_color(z1, 0, 1))
            glVertex3f(x, y, z1)
            glColor3f(*get_color(z2, 0, 1))
            glVertex3f(x + step, y, z2)
        glEnd()

    glCullFace(GL_FRONT)

    for x in np.arange(range_min, range_max, step):
        glBegin(GL_TRIANGLE_STRIP)
        for y in np.arange(range_min, range_max, step):
            z1 = f(x, y)
            z2 = f(x + step, y)

            glColor3f(*get_back_color(z1, 0, 1))
            glVertex3f(x, y, z1)
            glColor3f(*get_back_color(z2, 0, 1))
            glVertex3f(x + step, y, z2)
        glEnd()

    unclip_unit()

    glDisable(GL_CULL_FACE)
