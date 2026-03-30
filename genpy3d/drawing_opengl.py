from dataclasses import dataclass

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

@dataclass(frozen=True)
class ViewParameters:
    lookat: tuple = (2, 2, 1)
    offset: tuple = (0, 0, -.1)
    scale: tuple = 1
    aspect_ratio: float = 0.95 #height/width
    text_offset: tuple = ((0.03, 0.06, 0), (0.12, 0.03, 0), (0.03, 0.06, 0))
    axis_text_offset: tuple = ((0.03, 0.18, 0), (0.18, 0.03, 0), (0.03, 0.18, 0))

VIEW_1_1_1 = ViewParameters()
VIEW_2_2_1 = ViewParameters(offset=(0, 0, 0.85), scale=0.57, aspect_ratio=0.84)

def save_image(width, output_file, aspect_ratio):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, width, GL_RGB, GL_UNSIGNED_BYTE)

    image = Image.frombytes("RGB", (width, width), data)
    height = int(width * aspect_ratio)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image = image.crop((0, 0, width, height))
    image.save(output_file)


def get_display_function(draw_func, width, output_file, view_parameters):

    def display():

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(view_parameters.lookat[0], view_parameters.lookat[1], view_parameters.lookat[2], 0, 0, 0, 0, 0, 1)

        glRotatef(0, 0, 0, 1)
        glScalef(view_parameters.scale, view_parameters.scale, view_parameters.scale)
        glTranslatef(view_parameters.offset[0], view_parameters.offset[1], view_parameters.offset[2])
        draw_func()

        glFlush()

        save_image(width, output_file, view_parameters.aspect_ratio)
        glutDestroyWindow(glutGetWindow())

    return display


def init(width, view_parameters=ViewParameters()):
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, 1, 4)
    glMatrixMode(GL_MODELVIEW)


def make_opengl_3dimage(outfile, draw, width, background=0, channels=3, view_parameters=ViewParameters()):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(width, width)
    glutCreateWindow(b"PyOpenGL")

    init(width, view_parameters)

    draw()

    glutDisplayFunc(get_display_function(draw, width, outfile, view_parameters))

    glutMainLoopEvent()
