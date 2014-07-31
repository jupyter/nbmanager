#!/usr/bin/python3
from glob import glob
from subprocess import call
import os

from PyQt4.uic import compileUi

def ui():
    for uifile in glob("*.ui"):
        pyfile = os.path.join('nbmanager', 'ui_' + uifile[:-3] + ".py")
        #if outdated(pyfile, uifile):
        print(uifile)
        pyfile = open(pyfile, "wt", encoding="utf-8")
        uifile = open(uifile, "rt", encoding="utf-8")
        compileUi(uifile, pyfile, from_imports=True)
        
def resource():
    for resfile in glob("*.qrc"):
        pyfile = os.path.join('nbmanager', resfile[:-4] + "_rc.py")
        #if outdated(pyfile, resfile):
        print(resfile)
        call("pyrcc4 -py3 -o {} {}".format(pyfile, resfile), shell=True)

if __name__ == "__main__":
    ui()
    resource()
