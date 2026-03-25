import math
from dataclasses import dataclass

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
    axis_colors: tuple = ((0.4, 0.4, 0.4),)*3
    axis_line_width: float = 3
    div_colors: tuple = ((0.6, 0.6, 0.6),)*3
    div_line_width: float = 3

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
        return [(point[i] - self.start[i]) * self.size[i] / self.extent[i] for i in range(3)]

    def set_axis_style(self, width=4, r=(1, 0, 0), g=(0, 1, 0), b=(0, 0, 1)):
        self.axis_line_width =width
        self.axis_colors = (r, g, b)

    def set_div_style(self, width=3, r=(1, 0.5, 0.5), g=(0.5, 1, 0.5), b=(0.5, 0.5, 1)):
        self.div_line_width =width
        self.div_colors = (r, g, b)

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
            glVertex3f(pos[0], 0, 0)
            glVertex3f(pos[0], pos[1], 0)
            pos = self.transform_from_graph((m, 0, self.start[2]+self.extent[2]))
            glVertex3f(pos[0], 0, 0)
            glVertex3f(pos[0], 0, pos[2])

        glColor3f(*self.div_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glVertex3f(0, pos[1], 0)
            glVertex3f(pos[0], pos[1], 0)
            pos = self.transform_from_graph((0, m, self.start[2]+self.extent[2]))
            glVertex3f(0, pos[1], 0)
            glVertex3f(0, pos[1], pos[2])

        glColor3f(*self.div_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glVertex3f(0, 0, pos[2])
            glVertex3f(0, pos[1], pos[2])
            pos = self.transform_from_graph((self.start[0]+self.extent[0], 0, m))
            glVertex3f(0, 0, pos[2])
            glVertex3f(pos[0], 0, pos[2])

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
            glVertex3f(pos[0], pos[1], 0)
            glVertex3f(pos[0], pos[1]+tick, 0)

        glColor3f(*self.axis_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glVertex3f(pos[0], pos[1], 0)
            glVertex3f(pos[0]+tick, pos[1], 0)

        glColor3f(*self.axis_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glVertex3f(0, pos[1], pos[2])
            glVertex3f(0, pos[1]+tick, pos[2])

        glEnd()

    def _draw_axis_labels(self):

        glColor3f(*self.axis_colors[0])
        markers = self._get_divs(self.start[0], self.extent[0], self.divs[0])
        for m in markers:
            pos = self.transform_from_graph((m, self.start[1]+self.extent[1], 0))
            glRasterPos3f(pos[0] + self.text_offset[0][0], pos[1] + self.text_offset[0][1], 0)
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        glColor3f(*self.axis_colors[1])
        markers = self._get_divs(self.start[1], self.extent[1], self.divs[1])
        for m in markers:
            pos = self.transform_from_graph((self.start[0]+self.extent[0], m, 0))
            glRasterPos3f(pos[0] + self.text_offset[1][0], pos[1] + self.text_offset[1][1], 0)
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        glColor3f(*self.axis_colors[2])
        markers = self._get_divs(self.start[2], self.extent[2], self.divs[2])
        for m in markers:
            pos = self.transform_from_graph((0, self.start[1]+self.extent[1], m))
            glRasterPos3f(0, pos[1] + self.text_offset[2][1],  pos[2] + self.text_offset[2][2])
            label = f"{m:.1f}"
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))


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

        return self
