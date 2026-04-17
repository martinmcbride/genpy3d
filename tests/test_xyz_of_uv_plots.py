import math
import unittest
from genpy3d.drawing_opengl import make_opengl_3dimage, VIEW_2_2_1, VIEW_1_1_1
from genpy3d.axes_opengl import Axes
from genpy3d.plot_opengl import Plot_xyz_of_uv
from tests.image_test_helper import run_image_test


class Test_xyz_of_uv_Plots(unittest.TestCase):

    def test_default_xyz_of_uv_plot(self):

        def creator(file):
            def draw(view_parameters):
                fx = lambda u, v: u
                fy = lambda u, v: v

                def fz(u, v):
                    x = u - 0.5
                    y = v - 0.5
                    r = math.sqrt(x*x + y*y)
                    return math.sin(math.pi*r)*0.9

                axes = Axes().draw(view_parameters)
                Plot_xyz_of_uv(axes).of_function(fx, fy, fz).with_grid().draw()

            make_opengl_3dimage(file, draw, 500)

        self.assertTrue(run_image_test('test_default_xyz_of_uv_plot.png', creator))

    #
    # def test_wide_clipped_xyz_of_uv_plot(self):
    #
    #     def creator(file):
    #         def draw(view_parameters):
    #             axes = Axes().of_size((2, 2, 1)).of_extent((1, 1, 0.5)).draw(view_parameters)
    #             Plot_xyz_of_uv(axes).of_function(lambda x, y: 0.25 + 0.4*math.sin(x*10)*math.sin(y*10)).draw()
    #
    #         make_opengl_3dimage(file, draw, 500, view_parameters=VIEW_2_2_1)
    #
    #     self.assertTrue(run_image_test('test_wide_clipped_xyz_of_uv_plot.png', creator))
    #
    #
    # def test_grid_xyz_of_uv_plot(self):
    #
    #     def creator(file):
    #         def draw(view_parameters):
    #             axes = Axes().draw(view_parameters)
    #             Plot_xyz_of_uv(axes).of_function(lambda x, y: 0.5 + 0.4*math.sin(x*10)*math.sin(y*10)).with_grid(grid_color=(0, 0, 0)).draw()
    #
    #         make_opengl_3dimage(file, draw, 500)
    #
    #     self.assertTrue(run_image_test('test_grid_xyz_of_uv_plot.png', creator))
    #
    #
    #
