from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

def save_image(width, height, output_file):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

    image = Image.frombytes("RGB", (width, height), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(output_file)
    print(f"Saved {output_file}")


def get_display_function(draw_func, width, height, output_file):

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(2, 2, 2, 0, 0, 0, 0, 0, 1)

        glRotatef(0, 0, 0, 30)
        draw_func(width, height)

        glFlush()

        save_image(width, height, output_file)
        glutDestroyWindow(glutGetWindow())

    return display


def init(width, height):
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, width / height, 0.1, 100)

    glMatrixMode(GL_MODELVIEW)


def make_opengl_3dimage(outfile, draw, width, height, background=0, channels=3):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"PyOpenGL")

    init(width, height)

    draw(width, height)

    glutDisplayFunc(get_display_function(draw, width, height, outfile))

    glutMainLoop()
