from genpy3d.drawing_opengl import make_opengl_3dimage
from genpy3d.plot_opengl import Axes

import sys
print(sys.prefix)


def draw(width, height):
    Axes().of_size((1, 1.1, 0.8)).of_start((1, 2, 3)).draw()

make_opengl_3dimage("cube.png", draw, 600, 500)
