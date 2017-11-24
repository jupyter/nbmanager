import os.path
import sys
import webbrowser
from enum import Enum
from typing import Callable, Union

from PyQt5 import QtCore, QtGui, QtWidgets

from .ui_mainwindow import Ui_MainWindow
from .widgets import EditableLabel
from . import api


class Icon(Enum):
    NbManager = 'jupyter-nbmanager'
    Server = 'go-home'
    Session = 'application-x-ipynb+json'
    Link = 'link'
    Shutdown = 'process-stop'

    @property
    def icon(self):
        return QtGui.QIcon.fromTheme(self.value)


class ActionItem(QtGui.QStandardItem):
    def __init__(self, action: QtWidgets.QAction):
        super().__init__()
        self.action = action
        self.setSelectable(False)


class ServerItem(QtGui.QStandardItem):
    def __init__(self, server: api.NbServer, icon: QtGui.QIcon=None):
        super().__init__()
        self.server = server
        self.setIcon(icon or Icon.Server.icon)


class SessionItem(ServerItem):
    def __init__(self, session: dict, server: api.NbServer):
        super().__init__(server, Icon.Session.icon)
        self.session = session


class ActionRow(QtWidgets.QWidget):
    def __init__(self, action: QtWidgets.QAction):
        super().__init__()
        button = QtWidgets.QPushButton(action.icon(), action.text())
        button.clicked.connect(action.trigger)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(button)
        # layout.addWidget(label)


class ItemRow(QtWidgets.QWidget):
    def __init__(self, item: Union[ServerItem, SessionItem], shutdown_callback: Callable):
        super().__init__()
        self.item = item
        self.shutdown_callback = shutdown_callback

        self.edit_label = EditableLabel(self.label)
        self.edit_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        link_button = QtWidgets.QPushButton(Icon.Link.icon, '')
        link_button.clicked.connect(self.open_browser)
        shutdown_button = QtWidgets.QPushButton(Icon.Shutdown.icon, '')
        shutdown_button.clicked.connect(self.shutdown)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.edit_label)
        layout.addWidget(link_button)
        layout.addWidget(shutdown_button)

    @property
    def editable(self):
        return self.edit_label.editable

    @editable.setter
    def editable(self, value: bool):
        self.edit_label.editable = value

    @property
    def label(self): raise NotImplemented

    def open_browser(self): raise NotImplemented

    def shutdown(self): raise NotImplemented


class ServerRow(ItemRow):
    def __init__(self, item: ServerItem, shutdown_callback: Callable):
        super().__init__(item, shutdown_callback)
        self.editable = False

    @property
    def label(self):
        return self.item.server.notebook_dir

    def open_browser(self):
        webbrowser.open('{}?token={}'.format(self.item.server.url, self.item.server.token))

    def shutdown(self):
        self.item.server.shutdown(wait=False)
        swt = ServerWaiterThread(self.item.server)
        swt.finished.connect(self.shutdown_callback)
        swt.start()


class SessionRow(ItemRow):
    def __init__(self, item: SessionItem, shutdown_callback: Callable):
        super().__init__(item, shutdown_callback)
        self.edit_label.editingFinished.connect(self.rename)

    @property
    def label(self):
        return self.item.session['notebook']['path']

    def open_browser(self):
        print(self.item.session)
        webbrowser.open('{}notebooks/{}?token={}'.format(self.item.server.url, self.label, self.item.server.token))

    def shutdown(self):
        sid = self.item.session['id']
        self.item.server.stop_session(sid)
        self.shutdown_callback()

    def rename(self, name):
        print(self.item.session['id'], '→', name)
        self.item.server.rename_session(self.item.session['id'])


class ServerWaiterThread(QtCore.QThread):
    registry = set()  # Keep a global reference so threads aren't GCed too soon

    finished = QtCore.pyqtSignal()

    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self.registry.add(self)
        self.finished.connect(lambda: self.registry.remove(self))

    def run(self):
        self.server.wait()
        self.finished.emit()


class Main(QtWidgets.QMainWindow):
    _path_valid = True

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(Icon.NbManager.icon)

        self.servers_by_pid = {}
        self.sessions_by_sid = {}
        self.current_servers = []

        self.processes_model = QtGui.QStandardItemModel()
        self.ui.tree.setModel(self.processes_model)
        self.processes_root = self.init_root()
        self.populate_processes()
        self.auto_refresh = QtCore.QTimer(self)
        self.auto_refresh.timeout.connect(self.refresh_processes)
        self.auto_refresh.start(1000)

        self.ui.actionRefresh.triggered.connect(self.refresh_processes)

        # Launching UI
        self.ui.start_dir_lineedit.setText(os.path.expanduser('~'))
        self.ui.start_dir_lineedit.editingFinished.connect(self.validate_dir)
        self.ui.start_dir_lineedit.textEdited.connect(self.validate_dir_sticky)
        self.ui.choose_dir_button.clicked.connect(self.choose_dir)
        self.ui.launch_button.clicked.connect(self.launch)

    def init_root(self):
        root = ActionItem(self.ui.actionRefresh)
        self.processes_model.invisibleRootItem().appendRow(root)
        self.ui.tree.setIndexWidget(root.index(), ActionRow(root.action))
        self.ui.tree.expand(root.index())
        return root

    def add_server(self, server):
        server_item = ServerItem(server)
        self.servers_by_pid[server.pid] = server_item
        self.processes_root.appendRow(server_item)
        self.ui.tree.setIndexWidget(server_item.index(), ServerRow(server_item, self.refresh_processes))

        for session in server.sessions():
            self.add_session(session, server_item)

        self.ui.tree.expand(server_item.index())

    def add_session(self, session, parent):
        session_item = SessionItem(session, parent.server)
        self.sessions_by_sid[session['id']] = session_item
        parent.appendRow(session_item)
        self.ui.tree.setIndexWidget(session_item.index(), SessionRow(session_item, self.refresh_processes))

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

    # Launching UI
    def choose_dir(self):
        path = self.ui.start_dir_lineedit.text()
        if not os.path.isdir(path):
            path = os.path.expanduser('~')
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Choose directory for new notebook server",
            path, QtWidgets.QFileDialog.ShowDirsOnly)
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


def theme_warning(*msg):
    print('NBManager:', *msg, '– using builtin theme', file=sys.stderr)


def install_theme():
    ignore_varname = 'NBMANAGER_IGNORE_THEME'
    forced = os.environ.get(ignore_varname, '')
    no_theme = not QtGui.QIcon.themeName()
    if forced:
        theme_warning(ignore_varname, 'set')
        paths = QtGui.QIcon.themeSearchPaths()
        builtin = paths.pop(paths.index(':/icons'))
        QtGui.QIcon.setThemeSearchPaths([builtin] + paths)  # this is always available, but we force its use
    elif no_theme:
        theme_warning('no available theme found')

    if forced or no_theme:
        QtGui.QIcon.setThemeName('nbmanager-icons')


def main():
    app = QtWidgets.QApplication(sys.argv)
    install_theme()
    window = Main()
    if sys.stderr is None:
        sys.excepthook = window.excepthook
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
