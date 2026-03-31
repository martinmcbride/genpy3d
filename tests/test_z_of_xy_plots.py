import math
import unittest
from genpy3d.drawing_opengl import make_opengl_3dimage, VIEW_2_2_1, VIEW_1_1_1
from genpy3d.axes_opengl import Axes
from genpy3d.plot_opengl import Plot_z_of_xy
from tests.image_test_helper import run_image_test


class TestAxes(unittest.TestCase):

    def test_default_z_of_xy_plot(self):

        def creator(file):
            def draw():
                axes = Axes().draw(VIEW_1_1_1)
                Plot_z_of_xy(axes).of_function(lambda x, y: 0.5 + 0.4*math.sin(x*10)*math.sin(y*10)).draw()

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_default_z_of_xy_plot.png', creator))


    def test_wide_clipped_z_of_xy_plot(self):

        def creator(file):
            def draw():
                axes = Axes().of_size((2, 2, 1)).of_extent((1, 1, 0.5)).draw(VIEW_1_1_1)
                Plot_z_of_xy(axes).of_function(lambda x, y: 0.25 + 0.4*math.sin(x*10)*math.sin(y*10)).draw()

            make_opengl_3dimage(file, draw, 500, view_parameters=VIEW_2_2_1)

        self.assertTrue(run_image_test('test_wide_clipped_z_of_xy_plot.png', creator))


    def test_grid_z_of_xy_plot(self):

        def creator(file):
            def draw():
                axes = Axes().draw(VIEW_1_1_1)
                Plot_z_of_xy(axes).of_function(lambda x, y: 0.5 + 0.4*math.sin(x*10)*math.sin(y*10)).with_grid().draw()

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_default_z_of_xy_plot.png', creator))



