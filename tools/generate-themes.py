"""Generate the four Miami '26 Blender themes, each as its own extension (a theme extension holds a
single XML file):

    python tools/generate-themes.py

Two palettes, each in a dark and a light version, the same as the Visual Studio and VS Code themes
(github.com/stillgbx/miami26-vs, github.com/stillgbx/miami26-vscode):
* Bay: a day on the bay. Turquoise water, sky blue, lavender towers, pink facades, warm sand.
* Sunset: dusk on the ocean front. Magenta, sunset orange, gold, periwinkle buildings, violet sky.

The themes are built on the Blender themes exported by tools/export-base-themes.py:
* The greys of the base, which draw the whole interface, follow the 'ramp' of the palette by lightness.
* The blue accent of Blender (selection, cursor, playhead) takes the hue of the palette accent.
* The orange of selected and active items takes the 'selection' hue of the palette.
* The text editor, the console and the 3D viewport background are set from the palette.
* Colors that carry a meaning are kept: axes, curve handles, bone, collection and strip colors, node
  categories, animation states.

Outputs, one folder per extension: extensions/<id>/blender_manifest.toml and <Theme_Name>.xml.
"""
import colorsys
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = '1.0.0'

BAY = {
    'id': 'miami26_bay',
    'name': "Miami '26 Bay",
    'file': 'Miami_26_Bay.xml',
    'base': 'dark',
    'tagline': 'Turquoise water, sky blue and lavender towers of a Miami bay',
    # The greys of the base by lightness: the night over the bay, up to the light text.
    'ramp': [(1.00, 'FFFFFF'), (0.93, 'E8F4F6'), (0.90, 'E2EFF2'), (0.76, 'B4CCD7'), (0.60, '7FA0B2'),
             (0.45, '3A6075'), (0.33, '21435A'), (0.24, '183245'), (0.188, '132838'), (0.157, '10222F'),
             (0.114, '0C1B26'), (0.094, '08151F'), (0.086, '07131D'), (0.03, '030A10'), (0.00, '000000')],
    'accent': '2ED3C6',      # the hue of the selection, cursor and playhead
    'selection': 'FF9CC2',   # the hue of selected and active objects: pink facades
    'ui': {
        'editor': '0C1B26', 'editor_margin': '0A1720', 'text': 'E8F4F6', 'line_number': '4E7186',
        'editor_selection': '1E4A5C', 'outliner_active': '2A5F73', 'caret': '2ED3C6',
        'viewport_top': '183A4D', 'viewport_bottom': '0C1B26',
        'success': '7EDC9E', 'error': 'FF6B8B',
    },
    'tokens': {
        'keyword': '2ED3C6', 'type': 'B9A6FF', 'function': '7CC4FF', 'tag': '7EDC9E', 'variable': 'DCEBF5',
        'operator': '8FE9E1', 'string': 'FFC98F', 'constant': 'FF9CC2', 'comment': '557489',
    },
}

BAY_LIGHT = {
    'id': 'miami26_bay_light',
    'name': "Miami '26 Bay Light",
    'file': 'Miami_26_Bay_Light.xml',
    'base': 'light',
    'tagline': 'The pastel sky and water of a Miami bay, in light',
    # Blender Light draws its backgrounds with mid greys: they become sky blues, its text a deep teal.
    'ramp': [(1.00, 'F2FAFA'), (0.90, 'E3F2F2'), (0.80, 'D7ECF0'), (0.70, 'C8E3EC'), (0.60, 'B9DAE8'),
             (0.45, '8DB8CB'), (0.39, '7AA6BA'), (0.30, '45697A'), (0.19, '1F3A48'), (0.10, '17323F'),
             (0.00, '0B2230')],
    'accent': '0B7F75',
    'selection': 'BF2F68',
    'ui': {
        'editor': 'E3F2F2', 'editor_margin': 'D7ECF0', 'text': '17323F', 'line_number': '6E95A3',
        'editor_selection': 'B2E0DA', 'outliner_active': '9DD6CF', 'caret': '0B7F75',
        # Light themes: the outliner names of active and selected items, dark on the pastel rows.
        'outliner_active_text': '0A4F49', 'outliner_selected_text': 'A3245A',
        'viewport_top': 'A9CFE2', 'viewport_bottom': 'D3EBEC',
        'success': '2A7F47', 'error': 'C62D58',
    },
    'tokens': {
        'keyword': '0A7A70', 'type': '5E45C4', 'function': '1C65AD', 'tag': '2A7F47', 'variable': '22394D',
        'operator': '2F7F79', 'string': 'A3561A', 'constant': 'BF2F68', 'comment': '5F7F8C',
    },
}

SUNSET = {
    'id': 'miami26_sunset',
    'name': "Miami '26 Sunset",
    'file': 'Miami_26_Sunset.xml',
    'base': 'dark',
    'tagline': 'Magenta, sunset orange and gold over a violet Miami sky',
    'ramp': [(1.00, 'FFFFFF'), (0.93, 'F6EEF6'), (0.90, 'F0E8F4'), (0.76, 'CBC2E0'), (0.60, '9A90BE'),
             (0.45, '5A5088'), (0.33, '3A3168'), (0.24, '2A2250'), (0.188, '211A3D'), (0.157, '1B1634'),
             (0.114, '15112A'), (0.094, '0F0C20'), (0.086, '0D0A1C'), (0.03, '06040E'), (0.00, '000000')],
    'accent': 'FF4FA3',
    'selection': 'FFA45C',   # sunset orange, close to the Blender orange
    'ui': {
        'editor': '15112A', 'editor_margin': '120E24', 'text': 'F6EEF6', 'line_number': '62598F',
        'editor_selection': '4A2A6A', 'outliner_active': '5E3585', 'caret': 'FF4FA3',
        'viewport_top': '2B1F52', 'viewport_bottom': '3D1B42',
        'success': '7EE0A8', 'error': 'FF5C6C',
    },
    'tokens': {
        'keyword': 'FF4FA3', 'type': 'A9B4F5', 'function': 'FFA45C', 'tag': 'D39BFF', 'variable': 'F3DDF0',
        'operator': 'FF8FC4', 'string': 'FFD27F', 'constant': 'FF7A6B', 'comment': '7C6FA3',
    },
}

SUNSET_LIGHT = {
    'id': 'miami26_sunset_light',
    'name': "Miami '26 Sunset Light",
    'file': 'Miami_26_Sunset_Light.xml',
    'base': 'light',
    'tagline': 'The sky of a Miami dusk, from lavender to peach, in light',
    'ramp': [(1.00, 'FFF4EE'), (0.90, 'FBECE4'), (0.80, 'F4DDE4'), (0.70, 'EDD0E0'), (0.60, 'E2C3DE'),
             (0.45, 'C69FC4'), (0.39, 'B08AA8'), (0.30, '74566F'), (0.19, '3A2350'), (0.10, '2E1A3D'),
             (0.00, '1E0F2A')],
    'accent': 'C2186A',
    'selection': 'C9612A',
    'ui': {
        'editor': 'FBECE4', 'editor_margin': 'F4DDE4', 'text': '2E1A3D', 'line_number': '9C7C96',
        'editor_selection': 'F2C3D6', 'outliner_active': 'EBAFC8', 'caret': 'C2186A',
        'outliner_active_text': '7A0F45', 'outliner_selected_text': 'A84A12',
        'viewport_top': 'D2BFE6', 'viewport_bottom': 'F6D6CC',
        'success': '2E7D4A', 'error': 'C9392A',
    },
    'tokens': {
        'keyword': 'BD1766', 'type': '434BB5', 'function': 'B5561A', 'tag': '7235AD', 'variable': '35203F',
        'operator': 'A62A66', 'string': '845A00', 'constant': 'C9392A', 'comment': '87718F',
    },
}

THEMES = [BAY, BAY_LIGHT, SUNSET, SUNSET_LIGHT]

# Colors kept as they are: they tell bones, collections, strips, node categories, curve handle types
# and animation states apart.
KEPT = ('bone_color_sets', 'collection_color', 'strip_color', 'wcol_state', 'ThemeCommonCurves',
        'sequence_editor', 'nla_editor', 'clip_editor', 'dopesheet_editor', 'ThemeCommonAnim')
# Node category colors (converter_node, color_node...) are kept, the rest of the node editor follows.
KEPT_NODE_ATTRS = re.compile(r'_node$|^node_backdrop$')

# Where the blue accent of Blender is the interface accent, and can take the palette accent.
ACCENT_AREAS = ('user_interface', 'regions', 'properties', 'preferences', 'file_browser', 'outliner',
                'text_editor', 'console', 'space')

# Text editor and console, from the palette: attribute -> ui or token role.
TEXT_EDITOR = {
    'line_numbers': 'line_number', 'line_numbers_background': 'editor_margin',
    'selected_text': 'editor_selection', 'cursor': 'caret',
    'syntax_builtin': 'keyword', 'syntax_symbols': 'operator', 'syntax_special': 'function',
    'syntax_preprocessor': 'tag', 'syntax_reserved': 'type', 'syntax_comment': 'comment',
    'syntax_string': 'string', 'syntax_numbers': 'constant',
}
CONSOLE = {
    'line_output': 'function', 'line_input': 'text', 'line_info': 'success', 'line_error': 'error',
    'cursor': 'caret',
}


def hls(rgb):
    return colorsys.rgb_to_hls(*(int(rgb[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def to_rgb(h, l, s):
    return ''.join(f'{round(c * 255):02x}' for c in colorsys.hls_to_rgb(h % 1, l, s))


def chroma(rgb):
    channels = [int(rgb[i:i + 2], 16) for i in (0, 2, 4)]
    return max(channels) - min(channels)


def ramp(theme, lightness):
    """The color of the palette ramp at this lightness, interpolated between its stops."""
    stops = theme['ramp']
    for (l1, c1), (l2, c2) in zip(stops, stops[1:]):
        if l2 <= lightness <= l1:
            t = (lightness - l2) / (l1 - l2)
            return ''.join(f'{round(int(c2[i:i + 2], 16) + (int(c1[i:i + 2], 16) - int(c2[i:i + 2], 16)) * t):02x}'
                           for i in (0, 2, 4))
    return stops[0][1] if lightness > stops[0][0] else stops[-1][1]


def accent(theme, rgb, alpha):
    """A blue of the base, moved to the accent hue. Teal and magenta look lighter than Blender's blue at
    the same lightness: the light themes darken them so that the white text on them stays readable."""
    h, l, s = hls(rgb)
    if theme['base'] == 'light':
        l *= 0.66
    return '#' + to_rgb(hls(theme['accent'])[0], l, min(1, s * 1.15)) + alpha


def recolor(theme, path, attr, value):
    """The Miami color of one attribute of the base, or None to keep it."""
    rgb, alpha = value[1:7].lower(), value[7:]
    if attr == 'playhead':  # in the animation colors, but it is the interface accent
        return accent(theme, rgb, alpha)
    if any(part in path for part in KEPT):
        return None
    if path.endswith('ThemeNodeEditor') and KEPT_NODE_ATTRS.search(attr) and chroma(rgb) >= 12:
        return None
    h, l, s = hls(rgb)
    hue = h * 360

    if chroma(rgb) < 12:
        # The dark themes keep pure black (wires, shadows) and pure white (highlights).
        if theme['base'] == 'dark' and rgb in ('000000', 'ffffff'):
            return None
        return '#' + ramp(theme, l).lower() + alpha

    # The blue accent of Blender: selection, cursor, playhead, links.
    if 195 <= hue <= 230 and s > 0.3 and any(area in path for area in ACCENT_AREAS):
        return accent(theme, rgb, alpha)

    # The orange of selected and active items.
    if 15 <= hue <= 45 and s > 0.6 and re.search(r'select|active', attr):
        return '#' + to_rgb(hls(theme['selection'])[0], l, s) + alpha
    return None


def set_explicit(theme_el, theme):
    ui, tokens = theme['ui'], theme['tokens']
    colors = dict(ui, **tokens)

    text = theme_el.find('text_editor/ThemeTextEditor')
    for attr, role in TEXT_EDITOR.items():
        text.set(attr, '#' + colors[role].lower())
    space = text.find('space/ThemeSpaceGeneric')
    space.set('back', '#' + ui['editor'].lower())
    space.set('text', '#' + ui['text'].lower())

    console = theme_el.find('console/ThemeConsole')
    for attr, role in CONSOLE.items():
        console.set(attr, '#' + colors[role].lower())
    console.set('select', '#' + ui['editor_selection'].lower() + 'aa')
    space = console.find('space/ThemeSpaceGeneric')
    space.set('back', '#' + ui['editor'].lower())
    space.set('text', '#' + ui['text'].lower())

    gradient = theme_el.find('view_3d/ThemeView3D/space/ThemeSpaceGradient/gradients/ThemeGradientColors')
    gradient.set('background_type', 'LINEAR')
    gradient.set('high_gradient', '#' + ui['viewport_top'].lower())
    gradient.set('gradient', '#' + ui['viewport_bottom'].lower())

    # The outliner rows of selected items: the editor selection, so that the selected and active object
    # names (in the selection hue) stay readable on them.
    outliner = theme_el.find('outliner/ThemeOutliner')
    outliner.set('selected_highlight', '#' + ui['editor_selection'].lower())
    outliner.set('active', '#' + ui['outliner_active'].lower())
    if 'outliner_active_text' in ui:
        # Blender Light draws white names on dark rows; the pastel rows need dark names.
        outliner.set('active_object', '#' + ui['outliner_active_text'].lower())
        outliner.set('selected_object', '#' + ui['outliner_selected_text'].lower())
        outliner.find('space/ThemeSpaceGeneric').set('text_hi', '#' + ui['outliner_active_text'].lower())


def generate(theme):
    tree = ET.parse(ROOT / 'tools' / f"base-{theme['base']}.xml")

    def walk(element, path):
        for attr, value in element.attrib.items():
            if value.startswith('#') and len(value) in (7, 9):
                new = recolor(theme, path, attr, value)
                if new:
                    element.set(attr, new)
        for child in element:
            walk(child, f'{path}/{child.tag}')

    root = tree.getroot()
    walk(root, root.tag)
    set_explicit(root.find('Theme'), theme)

    folder = ROOT / 'extensions' / theme['id']
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob('*.xml'):
        old.unlink()
    ET.indent(tree, space='  ')
    tree.write(folder / theme['file'], encoding='utf-8', xml_declaration=False)
    (folder / 'blender_manifest.toml').write_text(manifest(theme), encoding='utf-8')
    print(f"extensions/{theme['id']} generated")


def manifest(theme):
    assert len(theme['tagline']) <= 64 and theme['tagline'][-1].isalnum(), theme['tagline']
    tags = ['Dark' if theme['base'] == 'dark' else 'Light', 'Colorful']
    return f'''schema_version = "1.0.0"

id = "{theme['id']}"
version = "{VERSION}"
name = "{theme['name']}"
tagline = "{theme['tagline']}"
maintainer = "stillgbx"
type = "theme"
website = "https://github.com/stillgbx/miami26-blender"
tags = [{", ".join(f'"{t}"' for t in tags)}]

blender_version_min = "4.2.0"

license = ["SPDX:GPL-3.0-or-later"]
copyright = ["2026 stillgbx"]
'''


def main():
    for theme in THEMES:
        generate(theme)


if __name__ == '__main__':
    main()
