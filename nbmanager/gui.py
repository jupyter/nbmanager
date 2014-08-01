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

        self.ui.treeView.clicked.connect(self.select_process)

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