from OpenGL.GL import *
from OpenGL.GLUT import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import sys

window_width = 600
window_height = 480

def load_font(size=32):
    """
    Try to load a TrueType font.
    Falls back to Pillow's default bitmap font if not found.
    """
    possible_fonts = [
        "DejaVuSans.ttf",
        "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            pass

    return ImageFont.load_default()


def create_text_image(text, font_size=32, color=(255, 255, 255, 255)):
    """
    Render text to a Pillow RGBA image and return width, height, pixel data.

    The image is flipped vertically because glDrawPixels expects pixel rows
    starting at the bottom, while Pillow stores rows starting at the top.
    """
    font = load_font(font_size)

    temp_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    bbox = temp_draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text(
        (-bbox[0], -bbox[1]),
        text,
        font=font,
        fill=color
    )

    # Flip vertically for OpenGL's bottom-up pixel convention
    img = ImageOps.flip(img)

    return text_width, text_height, img.tobytes("raw", "RGBA")


def draw_text_pixels(text, x, y, font_size=32, color=(255, 255, 255, 255)):
    """
    Draw text using glDrawPixels.

    x and y are measured from the top-left corner of the window.
    """
    glDisable(GL_DEPTH_TEST)

    width, height, pixels = create_text_image(text, font_size, color)

    # Convert top-left coordinates to OpenGL bottom-left window coordinates
    gl_x = x
    gl_y = y

    # Set the raster position in window coordinates
    glWindowPos2i(gl_x, gl_y)

    # Make sure rows are byte-aligned
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    # Draw the RGBA pixels
    glDrawPixels(
        width,
        height,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        pixels
    )


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Enable alpha blending so text transparency works
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Draw text
    draw_text_pixels(
        "Hello from glDrawPixels!",
        x=50,
        y=50,
        font_size=42,
        color=(255, 255, 255, 255)
    )

    draw_text_pixels(
        "This text was rasterized with Pillow.",
        x=50,
        y=120,
        font_size=28,
        color=(255, 220, 80, 255)
    )

    draw_text_pixels(
        "OpenGL draws it using glDrawPixels.",
        x=50,
        y=170,
        font_size=28,
        color=(120, 200, 255, 255)
    )

    glutSwapBuffers()


def reshape(width, height):
    global window_width, window_height

    window_width = width
    window_height = height

    glViewport(0, 0, width, height)


def init_opengl():
    glClearColor(0.08, 0.08, 0.1, 1.0)

    # Text is usually drawn as a 2D overlay, so depth testing is unnecessary
    glDisable(GL_DEPTH_TEST)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Text with glDrawPixels")

    init_opengl()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(display)

    glutMainLoop()


if __name__ == "__main__":
    main()