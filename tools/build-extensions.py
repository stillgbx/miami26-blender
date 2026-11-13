"""Package each theme of extensions/ as an extension zip in dist/, ready to install or upload:

    python tools/build-extensions.py

This is what "blender --command extension build" does for a theme (the manifest and the XML file at
the root of the zip), without needing Blender. To check a zip with Blender:

    blender --command extension validate dist/<id>-<version>.zip
"""
import pathlib
import re
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'


def main():
    DIST.mkdir(exist_ok=True)
    for folder in sorted((ROOT / 'extensions').iterdir()):
        manifest = (folder / 'blender_manifest.toml').read_text(encoding='utf-8')
        ext_id = re.search(r'^id = "([^"]+)"', manifest, re.M).group(1)
        version = re.search(r'^version = "([^"]+)"', manifest, re.M).group(1)
        themes = list(folder.glob('*.xml'))
        assert len(themes) == 1, f'{folder.name}: a theme extension holds exactly one XML file'

        target = DIST / f'{ext_id}-{version}.zip'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(folder / 'blender_manifest.toml', 'blender_manifest.toml')
            archive.write(themes[0], themes[0].name)
        print(f'{target.relative_to(ROOT)} built')


if __name__ == '__main__':
    main()
