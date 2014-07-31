import sys

from PyQt4 import QtGui
from .ui_mainwindow import Ui_MainWindow
from . import api

class ServerItem(QtGui.QStandardItem):
    def __init__(self, server):
        super().__init__(server.notebook_dir)
        self.server = server

class SessionItem(QtGui.QStandardItem):
    def __init__(self, session, server):
        self.session = session
        self.server = server
        if session['notebook']['path']:
            self.path = session['notebook']['path'] + "/" + session['notebook']['name']
        else:
            self.path = session['notebook']['name']
        super().__init__(self.path)

class Main(QtGui.QMainWindow):
    selected_proc = None
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.processes_model = QtGui.QStandardItemModel()
        self.processes_root = self.processes_model.invisibleRootItem()
        self.populate_processes()
        self.ui.treeView.setModel(self.processes_model)
        self.ui.treeView.expandAll()
        
        self.ui.treeView.clicked.connect(self.select_process)
        
        self.ui.actionShutdown.triggered.connect(self.shutdown)
        self.ui.actionRefresh.triggered.connect(self.refresh_processes)
    
    def populate_processes(self):
        for server in api.NbServer.findall():
            server_item = ServerItem(server)
            self.processes_root.appendRow(server_item)
            
            for session in server.sessions():
                server_item.appendRow(SessionItem(session, server))
    
    def refresh_processes(self):
        self.processes_model = QtGui.QStandardItemModel()
        self.processes_root = self.processes_model.invisibleRootItem()
        self.populate_processes()
        self.ui.treeView.setModel(self.processes_model)
        self.ui.treeView.expandAll()

    def select_process(self, index):
        self.selected_proc = self.processes_model.itemFromIndex(index)
    
    def shutdown(self):
        if isinstance(self.selected_proc, ServerItem):
            self.selected_proc.server.shutdown(wait=True)
        elif isinstance(self.selected_proc, SessionItem):
            sid = self.selected_proc.session['id']
            self.selected_proc.server.stop_session(sid)
        
        self.refresh_processes()

def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    if sys.stderr is None:
        sys.excepthook = window.excepthook
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()