# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(382, 488)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setIconSize(QtCore.QSize(16, 16))
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.treeView)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.start_dir_lineedit = QtWidgets.QLineEdit(self.groupBox)
        self.start_dir_lineedit.setObjectName("start_dir_lineedit")
        self.verticalLayout_2.addWidget(self.start_dir_lineedit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.choose_dir_button = QtWidgets.QPushButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("document-open-folder")
        self.choose_dir_button.setIcon(icon)
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.horizontalLayout.addWidget(self.choose_dir_button)
        self.launch_button = QtWidgets.QPushButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("system-run")
        self.launch_button.setIcon(icon)
        self.launch_button.setObjectName("launch_button")
        self.horizontalLayout.addWidget(self.launch_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 382, 27))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionShutdown = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("process-stop")
        self.actionShutdown.setIcon(icon)
        self.actionShutdown.setObjectName("actionShutdown")
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.actionRefresh.setIcon(icon)
        self.actionRefresh.setObjectName("actionRefresh")
        self.toolBar.addAction(self.actionShutdown)
        self.toolBar.addAction(self.actionRefresh)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IPython nbmanager"))
        self.groupBox.setTitle(_translate("MainWindow", "Launch a server"))
        self.choose_dir_button.setText(_translate("MainWindow", "Choose directory"))
        self.launch_button.setText(_translate("MainWindow", "Launch"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionShutdown.setText(_translate("MainWindow", "Shutdown"))
        self.actionShutdown.setToolTip(_translate("MainWindow", "<html><head/><body><p>Shut down the selected notebook server or session</p></body></html>"))
        self.actionRefresh.setText(_translate("MainWindow", "Refresh"))
        self.actionRefresh.setToolTip(_translate("MainWindow", "Refresh the list of processes"))

from . import qtresources_rc
