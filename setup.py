from distutils.core import setup

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
     )