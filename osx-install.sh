#!/bin/bash
set -e

iconutil -c icns nbmanager.iconset

python3 setup.py install
python3 setup.py py2app

INSTALL_PATH="$HOME/Applications/nbmanager.app"
if [ -e $INSTALL_PATH ]; then
    rm -rf $INSTALL_PATH
fi
ln -s "$(pwd)/dist/nbmanager.app" $INSTALL_PATH

