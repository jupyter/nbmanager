import os
import signal
import time
from urllib.parse import urljoin

from IPython.html.notebookapp import list_running_servers
from IPython.utils.process import check_pid
import requests

class NbServer:
    pid = port = url = notebook_dir = None
    def __init__(self, info):
        self.pid = info['pid']
        self.port = info['port']
        self.url = info['url']
        self.notebook_dir = info['notebook_dir']

        self.last_sessions = []

    @classmethod
    def findall(cls, profile='default'):
        return [cls(info) for info in list_running_servers(profile=profile)]

    @classmethod
    def find_new_and_stopped(cls, last_servers, profile='default'):
        last_by_pid = {s.pid: s for s in last_servers}
        new_servers, kept_servers = [], []
        for server in cls.findall(profile=profile):
            if server.pid in last_by_pid:
                kept_servers.append(last_by_pid.pop(server.pid))
            else:
                new_servers.append(server)

        return list(last_by_pid.values()), new_servers, kept_servers

    def check_alive(self):
        if not check_pid(self.pid):
            return False

        try:
            requests.head(self.url)
            return True
        except requests.ConnectionError:
            return False

    def sessions(self):
        try:
            r = requests.get(urljoin(self.url, 'api/sessions'))
        except requests.ConnectionError:
            self.last_sessions = []
        else:
            r.raise_for_status()
            self.last_sessions = r.json()
        return self.last_sessions

    def sessions_new_and_stopped(self):
        last_by_sid = {s['id']: s for s in self.last_sessions}
        new_sessions, kept_sessions = [], []
        for curr_sess in self.sessions():
            sid = curr_sess['id']
            if sid in last_by_sid:
                del last_by_sid[sid]
                kept_sessions.append(curr_sess)
            else:
                new_sessions.append(curr_sess)

        return list(last_by_sid.values()), new_sessions, kept_sessions

    def shutdown(self, wait=True):
        os.kill(self.pid, signal.SIGTERM)

        if wait:
            self.wait()
    
    def wait(self, interval=0.01):
        # os.waitpid() only works with child processes, so we need a busy loop
        pid = self.pid
        while check_pid(pid):
            time.sleep(0.01)

    def stop_session(self, sid):
        r = requests.delete(urljoin(self.url, 'api/sessions/%s' % sid))
        r.raise_for_status()