import unittest
from genpy3d.drawing_opengl import make_opengl_3dimage, VIEW_2_2_1, VIEW_1_1_1
from genpy3d.axes_opengl import Axes
from genpy3d.plot_opengl import Plot_z_of_xy
from tests.image_test_helper import run_image_test


class TestAxes(unittest.TestCase):

    def test_default_axes(self):

        def creator(file):
            def draw():
                Axes().draw(VIEW_1_1_1)

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_default_axes.png', creator))


    def test_wide_axes(self):

        def creator(file):
            def draw():
                Axes().of_size((2, 2, 1)).draw(VIEW_2_2_1)

            make_opengl_3dimage(file, draw, 500, view_parameters=VIEW_2_2_1)

        self.assertTrue(run_image_test('test_wide_axes.png', creator))


