"""Generate the four Miami '26 Blender themes, each as its own extension (a theme extension holds a
single XML file):

    python tools/generate-themes.py

Two palettes, each in a dark and a light version, the same as the Visual Studio and VS Code themes
(github.com/stillgbx/miami26-vs, github.com/stillgbx/miami26-vscode):
* Bay: a day on the bay. Sky blue, turquoise water, lavender palm trees, peach facades, warm sand.
* Sunset: dusk on the ocean front. Magenta, peach, pale gold, periwinkle and lavender sky, plum palm trees.

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
VERSION = '1.1.1'

BAY = {
    'id': 'miami26_bay',
    'name': "Miami '26 Bay",
    'file': 'Miami_26_Bay.xml',
    'base': 'dark',
    'tagline': 'Sky blue, turquoise water and lavender palm trees of a Miami bay',
    # The greys of the base by lightness: the bay at nightfall. Deep water backgrounds, lilac blue
    # widgets like the evening sky, up to the light text.
    'ramp': [(1.00, 'FFFFFF'), (0.93, 'EAF4F2'), (0.90, 'E2EEF2'), (0.76, 'B5C6DA'), (0.60, '7F95B8'),
             (0.45, '46607A'), (0.33, '2E3F63'), (0.24, '233056'), (0.188, '1C2747'), (0.157, '162538'),
             (0.114, '102230'), (0.094, '0D1A2A'), (0.086, '0B1626'), (0.03, '050B14'), (0.00, '000000')],
    'accent': '5FD6C6',      # the hue of the selection, cursor and playhead: turquoise water
    'selection': 'F5B095',   # the hue of selected and active objects: peach facades
    'ui': {
        'editor': '102230', 'editor_margin': '0D1C29', 'text': 'EAF4F2', 'line_number': '5F7C9A',
        'editor_selection': '5A4048', 'outliner_active': '6B4C55', 'caret': '7FD8C8',
        'viewport_top': '2B3762', 'viewport_bottom': '10303A',
        'success': '7EDC9E', 'error': 'FF6B8B',
    },
    'tokens': {
        'keyword': '7FD8C8', 'type': 'A9A6F0', 'function': '8EC6EC', 'tag': 'F5B49C', 'variable': 'E2EEF2',
        'operator': '9FE3D6', 'string': 'F3DDB0', 'constant': 'F2A0B4', 'comment': '64799C',
    },
}

BAY_LIGHT = {
    'id': 'miami26_bay_light',
    'name': "Miami '26 Bay Light",
    'file': 'Miami_26_Bay_Light.xml',
    'base': 'light',
    'tagline': 'The sky, water and sand of a Miami bay, in light',
    # Blender Light draws its backgrounds with mid greys: they become sky blues and mint water, its
    # lightest fields the sand, its text a deep blue.
    'ramp': [(1.00, 'FFFBF3'), (0.90, 'FBF3E6'), (0.80, 'E2F2EC'), (0.70, 'D3EEE8'), (0.60, 'B4D8E6'),
             (0.45, '93B8DC'), (0.39, '80A6CC'), (0.30, '45627E'), (0.19, '233A52'), (0.10, '1B3245'),
             (0.00, '0E2233')],
    'accent': '128079',
    'selection': 'C2386C',   # pink facades
    'ui': {
        'editor': 'FBF3E6', 'editor_margin': 'F2E6D3', 'text': '1B3245', 'line_number': '7A93AE',
        'editor_selection': 'F7CDBB', 'outliner_active': 'F2BBA6', 'caret': '128079',
        # Light themes: the outliner names of active and selected items, dark on the pastel rows.
        'outliner_active_text': '0B5853', 'outliner_selected_text': 'A3245A',
        'viewport_top': 'A6CBE8', 'viewport_bottom': 'CFEDE6',
        'success': '2A7F47', 'error': 'C62D58',
    },
    'tokens': {
        'keyword': '0E7A74', 'type': '5853B5', 'function': '23689E', 'tag': '9C3F8A', 'variable': '1F3A50',
        'operator': '2A7579', 'string': 'B04F2A', 'constant': 'C2386C', 'comment': '7380AA',
    },
}

SUNSET = {
    'id': 'miami26_sunset',
    'name': "Miami '26 Sunset",
    'file': 'Miami_26_Sunset.xml',
    'base': 'dark',
    'tagline': 'Magenta, peach and plum palm trees under a Miami dusk sky',
    # Plum palm trees for the backgrounds, the night sky for the widgets.
    'ramp': [(1.00, 'FFFFFF'), (0.93, 'F8EEF4'), (0.90, 'F2E6F0'), (0.76, 'D0BEDE'), (0.60, 'A08AC0'),
             (0.45, '64508A'), (0.33, '45336A'), (0.24, '3A2A58'), (0.188, '2E1F45'), (0.157, '2A1A3E'),
             (0.114, '231833'), (0.094, '1C1230'), (0.086, '160E24'), (0.03, '0A0612'), (0.00, '000000')],
    'accent': 'FF5FAA',
    'selection': 'FFB27A',   # the peach horizon, close to the Blender orange
    'ui': {
        'editor': '231833', 'editor_margin': '1E142D', 'text': 'F8EEF4', 'line_number': '7E6A9C',
        'editor_selection': '5A2F62', 'outliner_active': '6E3A78', 'caret': 'FF5FAA',
        'viewport_top': '2C2860', 'viewport_bottom': '5E2E52',
        'success': '7EE0A8', 'error': 'FF5C6C',
    },
    'tokens': {
        'keyword': 'FF5FAA', 'type': 'A9B4F5', 'function': 'FFB27A', 'tag': 'D6A2F2', 'variable': 'F6E2EE',
        'operator': 'FF9CC8', 'string': 'F6E2A2', 'constant': 'FF8A7A', 'comment': '8C72A8',
    },
}

SUNSET_LIGHT = {
    'id': 'miami26_sunset_light',
    'name': "Miami '26 Sunset Light",
    'file': 'Miami_26_Sunset_Light.xml',
    'base': 'light',
    'tagline': 'The sky of a Miami dusk, from lavender to peach, in light',
    # The sky at dusk by lightness: peach fields, pink and lavender backgrounds, a periwinkle frame.
    'ramp': [(1.00, 'FFF6EE'), (0.90, 'FDEBDB'), (0.80, 'F8D8E1'), (0.70, 'EECBE3'), (0.60, 'C9B9EA'),
             (0.45, 'AFA6E0'), (0.39, '9C96D6'), (0.30, '6C5277'), (0.19, '3A2350'), (0.10, '2E1A3D'),
             (0.00, '1E0F2A')],
    'accent': 'C8287A',
    'selection': 'C2601F',
    'ui': {
        'editor': 'FDEBDB', 'editor_margin': 'F9DDD3', 'text': '2E1A3D', 'line_number': '9A82A6',
        'editor_selection': 'F6C4D8', 'outliner_active': 'EEB0CB', 'caret': 'C8287A',
        'outliner_active_text': '7A0F45', 'outliner_selected_text': 'A84A12',
        'viewport_top': 'C3B6EA', 'viewport_bottom': 'F9CDB0',
        'success': '2E7D4A', 'error': 'C42B3A',
    },
    'tokens': {
        'keyword': 'BE1F70', 'type': '4A56B8', 'function': 'A64F18', 'tag': '7A3D8C', 'variable': '35203F',
        'operator': 'A3306E', 'string': '7F5E00', 'constant': 'B83A28', 'comment': '8E7299',
    },
}

THEMES = [BAY, BAY_LIGHT, SUNSET, SUNSET_LIGHT]

# Colors kept as they are: they tell bones, collections, strips, node categories, curve handle types
# and animation states apart.
KEPT = ('bone_color_sets', 'collection_color', 'strip_color', 'wcol_state', 'ThemeCommonCurves',
        'ThemeCommonAnim')
# Editors whose colors are kept (strips, keyframes, markers...), except their greys of background, text
# and grid: the timeline is a dope sheet, and its grey rows would stand out in a Miami theme.
KEPT_EDITORS = ('sequence_editor', 'nla_editor', 'clip_editor', 'dopesheet_editor')
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
    if any(part in path for part in KEPT_EDITORS) and not (
            chroma(rgb) < 12 and ('/space/' in path or attr == 'grid')):
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

    # Blender 5.3 dropped header_text: the top bar and status bar draw their text with 'text', white in
    # Blender Light. On the pastel bars of the light themes it must be the dark palette text.
    if theme['base'] == 'light':
        for bar in ('topbar/ThemeTopBar', 'statusbar/ThemeStatusBar'):
            space = theme_el.find(f'{bar}/space/ThemeSpaceGeneric')
            space.set('text', '#' + ui['text'].lower())
            space.set('text_hi', '#' + ui['text'].lower())

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
