#!/usr/bin/python3
from subprocess import call
from pathlib import Path

from PyQt5.uic import compileUi

here = Path(__file__).parent  # type: Path
path_qrc = here / 'qtresources.qrc'
dir_nbmanager = here / 'nbmanager'
dir_themes = here / 'icons'
dir_iconset = here / 'nbmanager.iconset'


template_qrc = '''\
<RCC>
  <qresource>
{}
  </qresource>
</RCC>
'''.format

template_qrc_file = '    <file>{}</file>'.format


template_index = '''\
[Icon Theme]
Name={name}
Inherits=default
Directories={dirs}

{sections}
'''.format

template_section = '''\
[{s}x{s}/{sec}]
Size={s}
Type=Fixed
Context={ctx}\
'''.format

template_scalable = '''\
[{s}/{sec}]
Size=512
Type=Scalable
MinSize=1
MaxSize=1024
Context={ctx}\
'''.format

contexts = dict(
    apps='Applications',
    mimetypes='MimeTypes',
    actions='Actions'
)


def all_sizes(dir_theme):
    def k(n):
        return int(n) if n != 'scalable' else 10000
    return sorted((p.name.split('x')[0] for p in dir_theme.iterdir() if p.is_dir()), key=k)

iconset_sizes = {16, 32, 128, 256, 512}


def sizedirs(dir_theme, sizes=None):
    for s in (sizes or all_sizes(dir_theme)):
        n = '{0}x{0}'.format(s) if s != 'scalable' else s
        yield s, dir_theme / n


def ui():
    for uifn in here.glob('*.ui'):
        pyfn = (dir_nbmanager / ('ui_' + uifn.stem)).with_suffix('.py')
        print(uifn, '→', pyfn)
        with pyfn.open('wt', encoding='utf-8') as pyfile, \
             uifn.open('rt', encoding='utf-8') as uifile:
            compileUi(uifile, pyfile, from_imports=True)


def resource():
    files = []
    for dir_theme in dir_themes.iterdir():
        files.append(template_qrc_file(dir_theme / 'index.theme'))
        for size, size_dir in sizedirs(dir_theme):
            for sec in size_dir.iterdir():
                for icon in sec.iterdir():
                    files.append(template_qrc_file(icon))

    print(path_qrc)
    with path_qrc.open('wt', encoding='utf-8') as qrc:
        qrc.write(template_qrc('\n'.join(files)))

    pyfn = (dir_nbmanager / (path_qrc.stem + '_rc')).with_suffix('.py')
    print(path_qrc, '→', pyfn)
    call('pyrcc5 -o {} {}'.format(pyfn, path_qrc), shell=True)


def icons():
    dirs = []
    sections = []

    for dir_theme in dir_themes.iterdir():
        for size, size_dir in sizedirs(dir_theme):
            for sec in size_dir.iterdir():
                dirs.append(str(sec.relative_to(dir_theme)))
                template = template_scalable if size == 'scalable' else template_section
                sections.append(template(
                    s=size,
                    sec=sec.name,
                    ctx=contexts[sec.name],
                ))

        index_theme = dir_theme / 'index.theme'
        print(index_theme)
        with index_theme.open('wt', encoding='utf-8') as index:
            index.write(template_index(
                name=dir_theme.name.title(),
                dirs=','.join(dirs),
                sections='\n\n'.join(sections),
            ))


def iconset():
    print(dir_iconset / '*')
    dir_iconset.mkdir(exist_ok=True)
    for size, size_dir in sizedirs(dir_themes / 'hicolor', iconset_sizes):
        links = [dir_iconset / 'icon_{s}x{s}.png'.format(s=size)]
        if size // 2 in iconset_sizes:
            links += [dir_iconset / 'icon_{h}x{h}@2x.png'.format(h=size // 2)]

        target = size_dir / 'apps' / 'jupyter-nbmanager.png'
        for link in links:
            if link.is_symlink():
                link.unlink()
            link.symlink_to('..' / target)


if __name__ == '__main__':
    ui()
    resource()
    icons()
    iconset()
