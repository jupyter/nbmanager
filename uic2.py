#!/usr/bin/python3
from pathlib import Path
from logging import basicConfig, getLogger, INFO

from PyQt5.uic import compileUi
from qtico import write_theme_indices, write_resources, write_iconset


logger = getLogger('uic2' if __name__ == '__main__' else __name__)

here = Path(__file__).parent  # type: Path
dir_nbmanager = here / 'nbmanager'
dir_themes = here / 'icons'
dir_iconset = here / 'nbmanager.iconset'
path_qrc = here / 'qtresources.qrc'
path_rcpy = dir_nbmanager / 'qtresources_rc.py'


def compile_ui(dir_ui: Path, dir_module: Path):
    for uifn in dir_ui.glob('*.ui'):
        pyfn = (dir_module / ('ui_' + uifn.stem)).with_suffix('.py')
        logger.info('Creating ui_*.py file: %s from %s', pyfn, uifn)
        with pyfn.open('wt', encoding='utf-8') as pyfile, \
             uifn.open('rt', encoding='utf-8') as uifile:
            compileUi(uifile, pyfile, from_imports=True)


def compile_all(verbose: bool=False):
    if verbose:
        basicConfig(level=INFO)
    compile_ui(here, dir_nbmanager)
    write_theme_indices(dir_themes)
    write_resources(path_qrc, path_rcpy)
    write_iconset('jupyter-nbmanager', dir_themes, dir_iconset)


if __name__ == '__main__':
    compile_all(True)
