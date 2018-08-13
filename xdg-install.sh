#!/bin/bash
set -e

python3 setup.py install --user

# This sets XDG_DATA_HOME if it's not already set
echo "Installing data files to: ${XDG_DATA_HOME:=$HOME/.local/share}"

#export XDG_UTILS_DEBUG_LEVEL=1  #DEBUG

for s in 48 64 128; do
    xdg-icon-resource install --noupdate --size $s --context apps "icons/hicolor/${s}x${s}/apps/jupyter-nbmanager.png" jupyter-nbmanager
done
xdg-icon-resource forceupdate

xdg-desktop-menu install jupyter-nbmanager.desktop
#update-desktop-database "$XDG_DATA_HOME/applications/"

