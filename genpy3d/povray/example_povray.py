from generativepy.geometry import Transform, Triangle

from generativepy.drawing import setup, make_image, make_image_frame

from generativepy.nparray import save_nparray_image, overlay_nparrays

from generativepy.povray import (
    make_povray_image,
    Camera3d,
    Lights3d,
    Scene3d,
    Axes3d,
    Plot3dZofXY,
    make_povray_frame,
)
from vapory import (
    Texture,
    Pigment,
    Finish,
    Cylinder,
    Union,
    Lathe,
    Torus,
    Scene,
    Background,
    LightSource,
    Box,
    Sphere,
    Text,
)
from generativepy.color import Color

import math
import numpy as np


def make_axis(axis, color=[1, 0, 0], start=-1, end=3, divs=1):
    texture = Texture(Pigment("color", color), Finish("phong", 1))
    startxyz = [0] * 3
    endxyz = [0] * 3
    startxyz[axis] = start
    endxyz[axis] = end
    return Cylinder(startxyz, endxyz, 0.03, texture)


def make_cube(pos=[0, 0, 0], color=[1, 0, 0]):
    texture = Texture(Pigment("color", color), Finish("phong", 1))
    x = 0.2
    c1 = [s - x for s in pos]
    c2 = [s + x for s in pos]
    return Box(c1, c2, texture)


def make_sphere(pos=[0, 0, 0], color=[1, 0, 0]):
    texture = Texture(Pigment("color", color), Finish("phong", 1))
    x = 0.3
    return Sphere(pos, x, texture)


def make_axes():
    return Union(
        make_axis(0, [1, 0, 0]),
        make_axis(1, [0, 1, 0]),
        make_axis(2, [0, 0, 1]),
        make_cube([1, 0, 0], [1, 0, 0]),
        make_cube([0, 1, 0], [0, 1, 0]),
        make_cube([0, 0, 1], [0, 0, 1]),
        make_sphere([-1, 0, 0], [1, 0, 0]),
        make_sphere([0, -1, 0], [0, 1, 0]),
        make_sphere([0, 0, -1], [0, 0, 1]),
        "rotate",
        [-90, 0, 0],
        "translate",
        [0, 0, 0],
    )


def make_plot():
    bands = 8
    length = 3
    xvals = [i * length / (bands - 1) for i in range(bands)]
    yvals = [math.sqrt(x) for x in xvals]
    lathe = Lathe(
        "linear_spline",
        bands,
        *zip(yvals, xvals),
        Texture(
            Pigment(
                "color",
                [0.2, 0.2, 0.8, 0.5],
            ),
            Finish("phong", 1),
        ),
    )
    grid_texture = Texture(
        Pigment(
            "color",
            [1, 1, 0],
        ),
    )

    torus_list = []
    for x, y in zip(xvals, yvals):
        torus = Torus(
            y,
            0.03,
            grid_texture,
            "translate",
            [0, x, 0],
        )
        torus_list.append(torus)

    curve_list = []
    for i in range(len(xvals) - 1):
        for j in range(12):
            angle = 2 * math.pi * j / 12
            a = (yvals[i] * math.cos(angle), xvals[i], yvals[i] * math.sin(angle))
            b = (
                yvals[i + 1] * math.cos(angle),
                xvals[i + 1],
                yvals[i + 1] * math.sin(angle),
            )
            cylinder = Cylinder(a, b, 0.03, grid_texture)
            curve_list.append(cylinder)

    return Union(
        lathe, *torus_list, *curve_list, "rotate", [90, 0, 0], "scale", [1, -1, 1]
    )


def draw(pixel_width, pixel_height, frame_no, frame_count):
    camera = Camera3d().standard_plot().get()
    lights = Lights3d().standard_plot().get()
    axes = (
        Axes3d()
        .of_start((-2, -4, -1))
        .of_extent((4, 8, 3))
        .with_divisions((0.5, 1, 0.5))
    )
    plot = (
        Plot3dZofXY(axes).function(lambda x, y: math.cos(2 * x) * math.cos(2 * y)).get()
    )
    return Scene3d().camera(camera).add(lights).add([axes.get(), plot]).get()


#    return Scene3d().camera(camera).add(lights).add([axes, plot, text]).get()


#    return scene(camera, standard_lights(), [make_axes(), make_plot()], Color(1))


# make_povray_image("test.png", draw, 1000, 1000)
image1 = make_povray_frame(draw, 500, 500)


def draw_scalene(ctx, pixel_width, pixel_height, fn, frame_count):
    setup(ctx, pixel_width, pixel_height, width=400, background=Color(1))

    Transform(ctx).scale(1, -1, (0, 200))
    color = Color(0, 0, 1)
    a = (100, 50)
    b = (300, 50)
    c = (150, 350)
    Triangle(ctx).of_corners(a, b, c).fill(color.light1).stroke(color, line_width=4)


image2 = make_image_frame(draw_scalene, 500, 500)

print("image1", image1.shape, image1.dtype)
print("image2", image2.shape, image2.dtype)

image = overlay_nparrays(image1, image2)
print("image", image.shape, image.dtype)
# m0 = image2[:, :, 0]
# m1 = image2[:, :, 1]
# m2 = image2[:, :, 2]
# # mask_color = (255, 255, 255)
# # mask = 1 if (m0==mask_color[0] and m1==mask_color[1] and m2==mask_color[2]) else 0
#
# mask = m0 & m1 & m2
# mask = np.repeat(mask[:, :, np.newaxis], 4, axis=2)
# white = np.full_like(mask, 255)
#
# print("white", white.shape)
# print("mask", mask.shape)
# print("image1", image1.shape)
# print("image2", image2.shape)
#
# image = np.where(mask==white, image1, image2)

save_nparray_image("bitmap.png", image)
