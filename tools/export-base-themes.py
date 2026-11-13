"""Export the built-in Blender themes, the bases of the Miami '26 themes, to tools/base-dark.xml and
tools/base-light.xml. Run with the Blender version to target, in the background with factory settings
(the user preferences are not touched):

    blender --background --factory-startup --python tools/export-base-themes.py

base-dark.xml is the default theme, built into Blender (its Blender_Dark.xml preset is empty).
base-light.xml is the Blender_Light.xml preset, applied then exported, so that it lists every field.
"""
import os

import bpy

try:  # Blender 5.x
    import _rna_xml as rna_xml
except ImportError:  # Blender 4.x
    import rna_xml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The same map as the "Add Theme Preset" operator (scripts/startup/bl_operators/presets.py).
PRESET_XML_MAP = bpy.types.USERPREF_MT_interface_theme_presets.preset_xml_map
SECURE_TYPES = getattr(bpy.types.USERPREF_MT_interface_theme_presets, "preset_xml_secure_types", None)


def export(name):
    path = os.path.join(ROOT, "tools", name)
    rna_xml.xml_file_write(bpy.context, path, PRESET_XML_MAP)
    print(f"{path} written")


bpy.ops.preferences.reset_default_theme()
export("base-dark.xml")

light = os.path.join(bpy.utils.preset_paths("interface_theme")[0], "Blender_Light.xml")
rna_xml.xml_file_run(bpy.context, light, PRESET_XML_MAP, secure_types=SECURE_TYPES)
export("base-light.xml")
