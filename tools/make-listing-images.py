"""Make the 1920 x 1080 images of the extensions.blender.org listings, from the screenshots of Preview/:
each screenshot, scaled down, on the sky gradient of its theme. Run with Blender (it brings numpy):

    blender --background --factory-startup --python tools/make-listing-images.py

Writes Preview/listing/<theme>.png.
"""
import importlib.util
import os

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTH, HEIGHT = 1920, 1080
SCALE = 0.9

spec = importlib.util.spec_from_file_location('generate_themes', os.path.join(ROOT, 'tools', 'generate-themes.py'))
themes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(themes)

SHOTS = {'miami26_bay': 'bay', 'miami26_bay_light': 'bay-light',
         'miami26_sunset': 'sunset', 'miami26_sunset_light': 'sunset-light'}


def rgb(hex_color):
    return np.array([int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0])


def to_linear(c):
    # Blender stores sRGB images as display values in their pixels: keep them as they are.
    return c


def main():
    out_dir = os.path.join(ROOT, 'Preview', 'listing')
    os.makedirs(out_dir, exist_ok=True)
    for theme in themes.THEMES:
        name = SHOTS[theme['id']]
        shot = bpy.data.images.load(os.path.join(ROOT, 'Preview', f'{name}.png'))
        w, h = int(shot.size[0] * SCALE), int(shot.size[1] * SCALE)
        shot.scale(w, h)
        pixels = np.array(shot.pixels[:], dtype=np.float32).reshape(h, w, 4)

        # Vertical sky gradient, bottom row first (Blender images start at the bottom).
        top, bottom = rgb(theme['ui']['viewport_top']), rgb(theme['ui']['viewport_bottom'])
        t = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None, None]
        canvas = np.broadcast_to(bottom + (top - bottom) * t, (HEIGHT, WIDTH, 4)).copy()

        x, y = (WIDTH - w) // 2, (HEIGHT - h) // 2
        canvas[y:y + h, x:x + w] = pixels

        image = bpy.data.images.new(f'listing_{name}', WIDTH, HEIGHT, alpha=False)
        image.pixels[:] = canvas.ravel()
        image.filepath_raw = os.path.join(out_dir, f'{name}.png')
        image.file_format = 'PNG'
        image.save()
        print(f'Preview/listing/{name}.png written')


main()
