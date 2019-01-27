from setuptools import setup
import sys


if 'egg_info' not in sys.argv:
    from uic2 import compile_all
    compile_all(True)

if sys.platform == 'darwin':
    extra_options = dict(
        app=['nbmanager'],
        options=dict(py2app=dict(
            argv_emulation=True,
            packages=['nbmanager'],
            alias=True,
            iconfile='nbmanager.icns'
        )),
    )
    extra_setup = ['py2app']
else:
    extra_options = {}
    extra_setup = []


setup(
    name='nbmanager',
    version='0.1',
    description='View and stop running Jupyter notebooks and servers',
    author='Thomas Kluyver',
    author_email='thomas@kluyver.me.uk',
    maintainer='Philipp A.',
    maintainer_email='flying-sheep@web.de',
    url='https://github.com/jupyter/nbmanager',
    packages=['nbmanager'],
    classifiers=[
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Framework :: Jupyter',
      'License :: OSI Approved :: BSD License',
    ],
    install_requires=['PyQt5', 'jupyterlab', 'requests', 'qtico'],
    setup_requires=['qtico'] + extra_setup,
    **extra_options,
)
