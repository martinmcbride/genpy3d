from dataclasses import dataclass

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

from genpy3d.render_text import draw_text_pixels


@dataclass(frozen=True)
class VIEW_1_1_1:
    lookat: tuple = (2, 2, 1)
    offset: tuple = (0, 0, -.1)
    scale: tuple = 1
    aspect_ratio: float = 0.85 #height/width
    text_offset: tuple = ((0.1, 0.15, 0.1), (0.2, 0, 0), (0, 0.08, 0))
    axis_text_offset: tuple = ((0.1, 0.26, 0.1), (0.3, 0, 0.1), (0, 0.18, 0))

ViewParameters = VIEW_1_1_1

@dataclass(frozen=True)
class VIEW_2_2_1:
    lookat: tuple = (2, 2, 1)
    offset: tuple = (0, 0, 0.65)
    scale: tuple = 0.53
    aspect_ratio: float = 0.68 #height/width
    text_offset: tuple = ((0.15, 0.25, 0.15), (0.3, 0, 0), (0, 0.12, 0))
    axis_text_offset: tuple = ((0.16, 0.45, 0.16), (0.55, 0, 0.16), (0, 0.4, 0))

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
        draw_func(view_parameters)

        draw_text_pixels(
            "Hello from glDrawPixels!",
            x=50,
            y=50,
            font_size=42,
            color=(255, 255, 255, 255)
        )

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

    draw(view_parameters)

    glutDisplayFunc(get_display_function(draw, width, outfile, view_parameters))

    glutMainLoopEvent()
