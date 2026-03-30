from dataclasses import dataclass

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

@dataclass
class ViewParameters:
    lookat: tuple = (2, 2, 2)
    focal_length: float = 40
    offset: tuple = (0, 0, 0.1)
    scale: tuple = 1
    aspect_ratio: float = 1 #height/width

VIEW_1_1_1 = ViewParameters()
VIEW_2_2_1 = ViewParameters(offset=(0, 0, 0.85), scale=0.57, aspect_ratio=0.84)

def save_image(width, height, output_file):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

    image = Image.frombytes("RGB", (width, height), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(output_file)


def get_display_function(draw_func, width, height, output_file, view_parameters):

    def display():

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(view_parameters.lookat[0], view_parameters.lookat[1], view_parameters.lookat[2], 0, 0, 0, 0, 0, 1)

        glRotatef(0, 0, 0, 1)
        glScalef(view_parameters.scale, view_parameters.scale, view_parameters.scale)
        glTranslatef(view_parameters.offset[0], view_parameters.offset[1], view_parameters.offset[2])
        draw_func(width, height)

        glFlush()

        save_image(width, height, output_file)
        glutDestroyWindow(glutGetWindow())

    return display


def init(width, height, view_parameters=ViewParameters()):
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(view_parameters.focal_length, width / height, 0.1, 100)

    glMatrixMode(GL_MODELVIEW)


def make_opengl_3dimage(outfile, draw, width, height=None, background=0, channels=3, view_parameters=ViewParameters()):
    if height is None:
        height = int(width * view_parameters.aspect_ratio)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"PyOpenGL")

    init(width, height, view_parameters)

    draw(width, height)

    print(view_parameters)
    glutDisplayFunc(get_display_function(draw, width, height, outfile, view_parameters))

    glutMainLoopEvent()
