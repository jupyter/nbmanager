import os
import signal
import sys
import time
from collections.abc import Iterable
from typing import Self, TypedDict
from urllib.parse import urljoin

import requests
from jupyter_server import serverapp
from psutil import pid_exists


class NbSession(TypedDict):
    id: str


class NbServerInfo(TypedDict):
    base_url: str  # '/'
    hostname: str
    password: bool
    pid: int
    port: int
    root_dir: str
    secure: bool
    sock: str  # ''
    token: str  # md5 hash
    url: str
    version: str  # '2.15.0'


class NbServer:
    pid: int
    port: int
    url: str
    root_dir: str
    token: str
    last_sessions: list[NbSession]

    def __init__(self, info: NbServerInfo) -> None:
        self.pid = info["pid"]
        self.port = info["port"]
        self.url = info["url"]
        self.root_dir = info["root_dir"]
        self.token = info.get("token", "")
        self.last_sessions = []

    @classmethod
    def findall(cls) -> list[Self]:
        return [cls(info) for info in serverapp.list_running_servers()]

    @classmethod
    def find_new_and_stopped(
        cls, last_servers: Iterable[Self]
    ) -> tuple[list[Self], list[Self], list[Self]]:
        last_by_pid = {s.pid: s for s in last_servers}
        new_servers, kept_servers = [], []
        for server in cls.findall():
            if server.pid in last_by_pid:
                kept_servers.append(last_by_pid.pop(server.pid))
            else:
                new_servers.append(server)

        return list(last_by_pid.values()), new_servers, kept_servers

    def check_alive(self):
        if not pid_exists(self.pid):
            return False

        try:
            requests.head(self.url)
            return True
        except requests.ConnectionError:
            return False

    def sessions(self) -> list[NbSession]:
        params = {}
        if self.token:
            params["token"] = self.token

        try:
            r = requests.get(urljoin(self.url, "api/sessions"), params=params)
        except requests.ConnectionError:
            self.last_sessions = []
        else:
            r.raise_for_status()
            self.last_sessions = r.json()
        return self.last_sessions

    def sessions_new_and_stopped(
        self,
    ) -> tuple[list[NbSession], list[NbSession], list[NbSession]]:
        last_by_sid = {s["id"]: s for s in self.last_sessions}
        new_sessions, kept_sessions = [], []
        for curr_sess in self.sessions():
            sid = curr_sess["id"]
            if sid in last_by_sid:
                del last_by_sid[sid]
                kept_sessions.append(curr_sess)
            else:
                new_sessions.append(curr_sess)

        return list(last_by_sid.values()), new_sessions, kept_sessions

    def shutdown(self, wait: bool = True) -> None:
        os.kill(self.pid, signal.SIGTERM)

        if wait:
            self.wait()

    def wait(self, interval: float = 0.01) -> None:
        # os.waitpid() only works with child processes, so we need a busy loop
        pid = self.pid
        while pid_exists(pid):
            time.sleep(interval)

    def stop_session(self, sid: str) -> None:
        r = requests.delete(urljoin(self.url, f"api/sessions/{sid}"))
        r.raise_for_status()


def launch_server(directory: os.PathLike, **kwargs):
    import subprocess

    cmd = [sys.executable, "-m", "jupyterlab", directory, "--no-browser"]
    if sys.platform == "darwin" and not sys.stdin.isatty():
        script = f'tell application "Terminal" to do script "{" ".join(cmd)}; exit"'
        subprocess.Popen(["osascript", "-e", script])
    else:
        subprocess.Popen(cmd)
