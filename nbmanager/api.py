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
    
    @classmethod
    def findall(cls, profile='default'):
        return [cls(info) for info in list_running_servers(profile=profile)]

    def check_alive(self):
        if not check_pid(self.pid):
            return False
        
        try:
            requests.head(self.url)
            return True
        except requests.ConnectionError:
            return False

    def sessions(self):
        r = requests.get(urljoin(self.url, 'api/sessions'))
        r.raise_for_status()
        return r.json()

    def shutdown(self, wait=True):
        os.kill(self.pid, signal.SIGINT)
        # The first interrupt makes it display an 'are you sure?' prompt
        time.sleep(0.01)
        os.kill(self.pid, signal.SIGINT)
        
        if wait:
            while check_pid(self.pid):
                time.sleep(0.01)

    def stop_session(self, sid):
        r = requests.delete(urljoin(self.url, 'api/sessions/%s' % sid))
        r.raise_for_status()