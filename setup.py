from setuptools import setup
import sys

from uic2 import compile_ui

compile_ui()

if sys.platform == 'darwin':
    extra_options = dict(
        app=['nbmanager.py'],
        options={'py2app': {
            'argv_emulation': True,
            'packages': ['nbmanager'],
            'alias': True,
            'iconfile': 'nbmanager.icns'
        }},
        setup_requires=['py2app']
    )
else:
    extra_options = {}


setup(name='nbmanager',
      version='0.1',
      description="View and stop running IPython notebooks and servers",
      author='Thomas Kluyver',
      author_email="thomas@kluyver.me.uk",
      url="https://github.com/takluyver/nbmanager",
      packages=['nbmanager'],
      classifiers=[
          "Framework :: IPython",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 3",
      ],
      install_requires=['PyQt5', 'notebook', 'requests'],
      **extra_options)
