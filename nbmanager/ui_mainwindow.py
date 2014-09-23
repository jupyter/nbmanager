# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Tue Sep 23 13:15:45 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(382, 488)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.treeView = QtGui.QTreeView(self.centralwidget)
        self.treeView.setIconSize(QtCore.QSize(16, 16))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.treeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.treeView)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.start_dir_lineedit = QtGui.QLineEdit(self.groupBox)
        self.start_dir_lineedit.setObjectName(_fromUtf8("start_dir_lineedit"))
        self.verticalLayout_2.addWidget(self.start_dir_lineedit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.choose_dir_button = QtGui.QPushButton(self.groupBox)
        self.choose_dir_button.setObjectName(_fromUtf8("choose_dir_button"))
        self.horizontalLayout.addWidget(self.choose_dir_button)
        self.launch_button = QtGui.QPushButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/right.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.launch_button.setIcon(icon)
        self.launch_button.setObjectName(_fromUtf8("launch_button"))
        self.horizontalLayout.addWidget(self.launch_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 382, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionShutdown = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/stop.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShutdown.setIcon(icon1)
        self.actionShutdown.setObjectName(_fromUtf8("actionShutdown"))
        self.actionRefresh = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/reload.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon2)
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.toolBar.addAction(self.actionShutdown)
        self.toolBar.addAction(self.actionRefresh)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "IPython nbmanager", None))
        self.groupBox.setTitle(_translate("MainWindow", "Launch a server", None))
        self.choose_dir_button.setText(_translate("MainWindow", "Choose directory", None))
        self.launch_button.setText(_translate("MainWindow", "Launch", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionShutdown.setText(_translate("MainWindow", "Shutdown", None))
        self.actionShutdown.setToolTip(_translate("MainWindow", "<html><head/><body><p>Shut down the selected notebook server or session</p></body></html>", None))
        self.actionRefresh.setText(_translate("MainWindow", "Refresh", None))
        self.actionRefresh.setToolTip(_translate("MainWindow", "Refresh the list of processes", None))

from . import qtresources_rc
