import os.path
import sys

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from .ui_mainwindow import Ui_MainWindow
from . import api


class ServerItem(QStandardItem):
    def __init__(self, server):
        super().__init__(server.notebook_dir)
        self.server = server


class SessionItem(QStandardItem):
    def __init__(self, session, server):
        super().__init__()
        self.session = session
        self.server = server

    def data(self, role=Qt.UserRole+1, *args, **kwargs):
        if role == Qt.DisplayRole:
            return self.session['notebook']['path']
        return super().data(role)


class ServerWaiterThread(QThread):
    registry = set()  # Keep a global reference so threads aren't GCed too soon

    finished = Signal(name='finished')

    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self.registry.add(self)
        self.finished.connect(lambda: self.registry.remove(self))

    def run(self):
        self.server.wait()
        self.finished.emit()


class Main(QMainWindow):
    _path_valid = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon.fromTheme('jupyter-nbmanager'))

        self.servers_by_pid = {}
        self.current_servers = []
        self.sessions_by_sid = {}

        self.processes_model = QStandardItemModel()
        self.ui.treeView.setModel(self.processes_model)
        self.processes_root = self.processes_model.invisibleRootItem()
        self.populate_processes()
        self.autorefresh = QTimer(self)
        self.autorefresh.timeout.connect(self.refresh_processes)
        self.autorefresh.start(1000)

        self.ui.actionShutdown.triggered.connect(self.shutdown)
        self.ui.actionRefresh.triggered.connect(self.refresh_processes)
        
        # Launching UI
        self.ui.start_dir_lineedit.setText(os.path.expanduser('~'))
        self.ui.start_dir_lineedit.editingFinished.connect(self.validate_dir)
        self.ui.start_dir_lineedit.textEdited.connect(self.validate_dir_sticky)
        self.ui.choose_dir_button.clicked.connect(self.choose_dir)
        self.ui.launch_button.clicked.connect(self.launch)

    def add_server(self, server):
        server_item = ServerItem(server)
        server_item.setIcon(QIcon.fromTheme('go-home'))
        self.servers_by_pid[server.pid] = server_item
        self.processes_root.appendRow(server_item)

        for session in server.sessions():
            self.add_session(session, server_item)

        self.ui.treeView.expand(server_item.index())

    def add_session(self, session, parent):
        session_item = SessionItem(session, parent.server)
        session_item.setIcon(QIcon.fromTheme('application-x-ipynb+json'))
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

            for sess in kept_sessions:
                # If the notebook has been renamed since the last poll, update
                # its GUI entry
                sess_item = self.sessions_by_sid[sess['id']]
                if sess_item.session != sess:
                    sess_item.session = sess
                    sess_item.emitDataChanged()

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

    # Launching UI
    def choose_dir(self):
        path = self.ui.start_dir_lineedit.text()
        if not os.path.isdir(path):
            path = os.path.expanduser('~')
        path = QFileDialog.getExistingDirectory(
            self, "Choose directory for new notebook server",
            path, QFileDialog.ShowDirsOnly)
        # Cancelled dialog -> empty string
        if path:
            self.ui.start_dir_lineedit.setText(path)

    def validate_dir(self, path=None):
        if path is None:
            path = self.ui.start_dir_lineedit.text()
        isvalid = os.path.isdir(path)
        self._path_valid = isvalid
        style = "" if isvalid else "QLineEdit{background: red;}"
        self.ui.start_dir_lineedit.setStyleSheet(style)
        self.ui.launch_button.setEnabled(isvalid)

    def validate_dir_sticky(self, path):
        if self._path_valid:
            # Don't mark it as invalid until the user finishes editing
            return
        self.validate_dir(path)
    
    def launch(self):
        path = self.ui.start_dir_lineedit.text()
        api.launch_server(path)


def theme_warning(msg):
    print('NBManager:', msg, '– using builtin theme', file=sys.stderr)


def install_theme():
    forced = os.environ.get('NBMANAGER_IGNORE_THEME', '')
    no_theme = not QIcon.themeName()
    if forced:
        theme_warning('NBCONVERT_IGNORE_THEME set')
        paths = QIcon.themeSearchPaths()
        builtin = paths.pop(paths.index(':/icons'))
        QIcon.setThemeSearchPaths([builtin] + paths)  # this is always available, but we force its use
    elif no_theme:
        theme_warning('no available theme found')

    if forced or no_theme:
        QIcon.setThemeName('nbmanager-icons')


def main():
    app = QApplication(sys.argv)
    install_theme()
    window = Main()
    if sys.stderr is None:
        sys.excepthook = window.excepthook
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
