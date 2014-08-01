import sys

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal
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

class ServerWaiterThread(QtCore.QThread):
    registry = set()  # Keep a global reference so threads aren't GCed too soon

    finished = QtCore.Signal()
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self.registry.add(self)
        self.finished.connect(lambda: self.registry.remove(self))

    def run(self):
        self.server.wait()
        self.finished.emit()

class Main(QtGui.QMainWindow):
    _nb_icon = None
    @property
    def nb_icon(self):
        if self._nb_icon is None:
            self._nb_icon = QtGui.QIcon()
            self._nb_icon.addPixmap(QtGui.QPixmap(":/icons/icons/ipynb_icon_16x16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        return self._nb_icon

    _server_icon = None
    @property
    def server_icon(self):
        if self._server_icon is None:
            self._server_icon = QtGui.QIcon()
            self._server_icon.addPixmap(QtGui.QPixmap(":/icons/icons/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        return self._server_icon

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.servers_by_pid = {}
        self.sessions_by_sid = {}

        self.processes_model = QtGui.QStandardItemModel()
        self.ui.treeView.setModel(self.processes_model)
        self.processes_root = self.processes_model.invisibleRootItem()
        self.populate_processes()

        self.ui.actionShutdown.triggered.connect(self.shutdown)
        self.ui.actionRefresh.triggered.connect(self.refresh_processes)

    def add_server(self, server):
        server_item = ServerItem(server)
        server_item.setIcon(self.server_icon)
        self.servers_by_pid[server.pid] = server_item
        self.processes_root.appendRow(server_item)

        for session in server.sessions():
            self.add_session(session, server_item)

        self.ui.treeView.expand(server_item.index())

    def add_session(self, session, parent):
        session_item = SessionItem(session, parent.server)
        session_item.setIcon(self.nb_icon)
        self.sessions_by_sid[session['id']] = session_item
        parent.appendRow(session_item)

    def populate_processes(self):
        self.current_servers = api.NbServer.findall()
        for server in self.current_servers:
            self.add_server(server)

    def refresh_processes(self):
        stopped, started, kept = api.NbServer.find_new_and_stopped(self.current_servers)
        self.current_servers = kept + started
        for server in stopped:
            row = self.servers_by_pid.pop(server.pid).row()
            self.processes_root.removeRow(row)
            for session in server.last_sessions:
                self.sessions_by_sid.pop(session['id'])

        for server in started:
            self.add_server(server)

        for server in kept:
            closed, opened, kept_sessions = server.sessions_new_and_stopped()
            parent = self.servers_by_pid[server.pid]
            for sess in closed:
                sid = sess['id']
                row = self.sessions_by_sid.pop(sid).row()
                parent.removeRow(row)

            for sess in opened:
                self.add_session(sess, parent)

    def selected_process(self):
        idxs = self.ui.treeView.selectedIndexes()
        if idxs:
            return self.processes_model.itemFromIndex(idxs[0])
        return None

    def shutdown(self):
        selected_proc = self.selected_process()
        if isinstance(selected_proc, ServerItem):
            server = selected_proc.server
            server.shutdown(wait=False)
            swt = ServerWaiterThread(server)
            swt.finished.connect(self.refresh_processes)
            swt.start()
        elif isinstance(selected_proc, SessionItem):
            sid = selected_proc.session['id']
            selected_proc.server.stop_session(sid)
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