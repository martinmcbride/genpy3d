import unittest
from genpy3d.drawing_opengl import make_opengl_3dimage, VIEW_2_2_1, VIEW_1_1_1
from genpy3d.axes_opengl import Axes
from tests.image_test_helper import run_image_test


class TestAxes(unittest.TestCase):

    def test_default_axes(self):

        def creator(file):
            def draw(view_parameters):
                Axes().draw(view_parameters)

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_default_axes.png', creator))

    def test_reverse_x_axis(self):

        def creator(file):
            def draw(view_parameters):
                Axes().of_start((1, 0, 0)).with_reverse_axes((1, 0, 0)).draw(view_parameters)

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_reverse_x_axis.png', creator))


    def test_wide_axes(self):

        def creator(file):
            def draw(view_parameters):
                Axes().of_size((2, 2, 1)).draw(view_parameters)

            make_opengl_3dimage(file, draw, 500, view_parameters=VIEW_2_2_1)

        self.assertTrue(run_image_test('test_wide_axes.png', creator))

    def test_reverse_wide_y_axis(self):

        def creator(file):
            def draw(view_parameters):
                Axes().of_start((0, 2, 3)).with_reverse_axes((0, 1, 0)).of_size((2, 2, 1)).draw(view_parameters)

            make_opengl_3dimage(file, draw, 500, view_parameters=VIEW_2_2_1)

        self.assertTrue(run_image_test('test_reverse_wide_y_axis.png', creator))


