#!/usr/bin/python3
from __future__ import annotations

from logging import INFO, basicConfig, getLogger
from pathlib import Path

from qtico import write_iconset, write_resources, write_theme_indices

logger = getLogger("uic2" if __name__ == "__main__" else __name__)

here = Path(__file__).parent  # type: Path
dir_themes = here / "icons"
dir_iconset = here / "nbmanager.iconset"
path_qrc = here / "qtresources.qrc"
path_rcpy = here / "src/nbmanager/qtresources_rc.py"


def compile_all(verbose: bool = False):
    if verbose:
        basicConfig(level=INFO)
    write_theme_indices(dir_themes)
    write_resources(path_qrc, path_rcpy)
    write_iconset("jupyter-nbmanager", dir_themes, dir_iconset)


if __name__ == "__main__":
    compile_all(True)
