from __future__ import annotations

import importlib.resources
import os.path
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from qtico import install_icon_theme
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.uic import loadUi

from . import api

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import ClassVar, Self

    from qtpy.QtGui import _QAction as QAction


class Icon(Enum):
    NbManager = "jupyter-nbmanager"
    Server = "go-home"
    Session = "application-x-ipynb+json"
    Link = "go-jump"
    Shutdown = "process-stop"

    @property
    def icon(self):
        return QtGui.QIcon.fromTheme(self.value)


class ActionItem(QtGui.QStandardItem):
    def __init__(self, action: QAction) -> None:
        super().__init__()
        self.action = action
        self.setEditable(False)
        self.setSelectable(False)


class ServerItem(QtGui.QStandardItem):
    server: api.Server

    def __init__(self, server, icon=None) -> None:
        super().__init__()
        self.server = server
        self.setEditable(False)
        self.setIcon(icon or Icon.Server.icon)


class SessionItem(ServerItem):
    def __init__(self, session: api.JupyterSession, server: api.Server) -> None:
        super().__init__(server, Icon.Session.icon)
        self.session = session


class ActionRow(QtWidgets.QWidget):
    def __init__(self, action: QAction) -> None:
        super().__init__()
        button = QtWidgets.QPushButton(action.icon(), action.text())
        button.clicked.connect(action.trigger)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(button)
        # layout.addWidget(label)


class ItemRow(QtWidgets.QWidget):
    def __init__(
        self,
        item: ServerItem | SessionItem,
        shutdown_callback: Callable[[], None],
    ):
        super().__init__()
        self.item = item
        self.shutdown_callback = shutdown_callback

        label = QtWidgets.QLabel(self.label)
        label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        link_button = QtWidgets.QPushButton(Icon.Link.icon, "")
        link_button.clicked.connect(self.open_browser)
        shutdown_button = QtWidgets.QPushButton(Icon.Shutdown.icon, "")
        shutdown_button.clicked.connect(self.shutdown)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(link_button)
        layout.addWidget(shutdown_button)

    @property
    def label(self) -> str: ...

    def open_browser(self) -> None: ...

    def shutdown(self) -> None: ...


class ServerRow(ItemRow):
    @property
    def label(self) -> str:
        return self.item.server.root_dir

    def open_browser(self) -> None:
        webbrowser.open(f"{self.item.server.url}?token={self.item.server.token}")

    def shutdown(self) -> None:
        self.item.server.shutdown(wait=False)
        swt = ServerWaiterThread(self.item.server)
        swt.finished.connect(self.shutdown_callback)
        swt.start()


class SessionRow(ItemRow):
    @property
    def label(self) -> str:
        return self.item.session["notebook"]["path"]

    def open_browser(self) -> None:
        webbrowser.open(
            f"{self.item.server.url}lab/tree/{self.label}?token={self.item.server.token}"
        )

    def shutdown(self) -> None:
        sid = self.item.session["id"]
        self.item.server.stop_session(sid)
        self.shutdown_callback()


class ServerWaiterThread(QtCore.QThread):
    # Keep a global reference so threads aren't GCed too soon
    registry: ClassVar[set[Self]] = set()

    finished: ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, server: api.Server, parent: QtCore.QObject = None) -> None:
        super().__init__(parent)
        self.server = server
        self.registry.add(self)
        self.finished.connect(lambda: self.registry.remove(self))

    def run(self) -> None:
        self.server.wait()
        self.finished.emit()


class Ui(Protocol):
    tree: QtWidgets.QTreeView
    start_dir_lineedit: QtWidgets.QLineEdit
    choose_dir_button: QtWidgets.QPushButton
    launch_button: QtWidgets.QPushButton

    actionRefresh: QAction


class Main(QtWidgets.QMainWindow):
    _path_valid: bool = True

    ui: Ui

    servers_by_pid: dict[int, ServerItem]
    sessions_by_sid: dict[str, SessionItem]
    current_servers: list[api.Server]

    processes_model: QtGui.QStandardItemModel
    processes_root: ActionItem
    auto_refresh: QtCore.QTimer

    def __init__(self) -> None:
        super().__init__()
        with importlib.resources.path("nbmanager", "mainwindow.ui") as ui_path:
            self.ui = loadUi(str(ui_path), self)
        # self.ui.setupUi(self)
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
        self.ui.start_dir_lineedit.setText(os.path.expanduser("~"))
        self.ui.start_dir_lineedit.editingFinished.connect(self.validate_dir)
        self.ui.start_dir_lineedit.textEdited.connect(self.validate_dir_sticky)
        self.ui.choose_dir_button.clicked.connect(self.choose_dir)
        self.ui.launch_button.clicked.connect(self.launch)

    def init_root(self) -> ActionItem:
        root = ActionItem(self.ui.actionRefresh)
        self.processes_model.invisibleRootItem().appendRow(root)
        self.ui.tree.setIndexWidget(root.index(), ActionRow(root.action))
        self.ui.tree.expand(root.index())
        return root

    def add_server(self, server: api.Server) -> None:
        server_item = ServerItem(server)
        self.servers_by_pid[server.pid] = server_item
        self.processes_root.appendRow(server_item)
        self.ui.tree.setIndexWidget(
            server_item.index(), ServerRow(server_item, self.refresh_processes)
        )

        for session in server.sessions():
            self.add_session(session, server_item)

        self.ui.tree.expand(server_item.index())

    def add_session(self, session: api.JupyterSession, parent):
        session_item = SessionItem(session, parent.server)
        self.sessions_by_sid[session["id"]] = session_item
        parent.appendRow(session_item)
        self.ui.tree.setIndexWidget(
            session_item.index(), SessionRow(session_item, self.refresh_processes)
        )

    def populate_processes(self):
        self.current_servers = api.Server.findall()
        for server in self.current_servers:
            self.add_server(server)

    def refresh_processes(self):
        stopped, started, kept = api.Server.find_new_and_stopped(self.current_servers)
        self.current_servers = kept + started
        for server in stopped:
            row = self.servers_by_pid.pop(server.pid).row()
            self.processes_root.removeRow(row)
            for session in server.last_sessions:
                self.sessions_by_sid.pop(session["id"])

        for server in started:
            self.add_server(server)

        for server in kept:
            closed, opened, kept_sessions = server.sessions_new_and_stopped()
            parent = self.servers_by_pid[server.pid]
            for sess in closed:
                sid = sess["id"]
                row = self.sessions_by_sid.pop(sid).row()
                parent.removeRow(row)

            for sess in opened:
                self.add_session(sess, parent)

            for sess in kept_sessions:
                # If the notebook has been renamed since the last poll, update
                # its GUI entry
                sess_item = self.sessions_by_sid[sess["id"]]
                if sess_item.session != sess:
                    sess_item.session = sess
                    sess_item.emitDataChanged()

    # Launching UI
    def choose_dir(self):
        path = self.ui.start_dir_lineedit.text()
        if not os.path.isdir(path):
            path = os.path.expanduser("~")
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Choose directory for new notebook server",
            path,
            QtWidgets.QFileDialog.Option.ShowDirsOnly,
        )
        # Cancelled dialog -> empty string
        if path:
            self.ui.start_dir_lineedit.setText(path)

    def validate_dir(self, path: os.PathLike | None = None):
        if path is None:
            path = self.ui.start_dir_lineedit.text()
        isvalid = Path(path).is_dir()
        self._path_valid = isvalid
        style = "" if isvalid else "QLineEdit{background: red;}"
        self.ui.start_dir_lineedit.setStyleSheet(style)
        self.ui.launch_button.setEnabled(isvalid)

    def validate_dir_sticky(self, path: os.PathLike | None = None):
        if self._path_valid:
            # Don't mark it as invalid until the user finishes editing
            return
        self.validate_dir(path)

    def launch(self) -> None:
        path = self.ui.start_dir_lineedit.text()
        api.launch_server(path)


def main():
    app = QtWidgets.QApplication(sys.argv)
    install_icon_theme("nbmanager-icons", ignore_varnames=["NBMANAGER_IGNORE_THEME"])
    window = Main()
    if sys.stderr is None:
        sys.excepthook = window.excepthook
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
