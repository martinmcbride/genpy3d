import unittest
from genpy3d.drawing_opengl import make_opengl_3dimage
from genpy3d.axes_opengl import Axes
from genpy3d.plot_opengl import Plot_z_of_xy
from tests.image_test_helper import run_image_test


class TestAxes(unittest.TestCase):

    def test_default_axes(self):

        def creator(file):
            def draw(width, height):
                axes = Axes().of_size((1, 1, 1)).of_start((0, 0, 0)).draw()
                Plot_z_of_xy(axes).of_function(lambda x, y: 0.8).draw()

            make_opengl_3dimage(file, draw, 500, 500)

        self.assertTrue(run_image_test('test_default_axes.png', creator))


    def test_wide_axes(self):

        def creator(file):
            def draw(width, height):
                Axes().of_size((1, 1, 0.5)).of_start((0, 0, 0)).draw()

            make_opengl_3dimage(file, draw, 500, 500)

        self.assertTrue(run_image_test('test_wide_axes.png', creator))


