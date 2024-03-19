import gevent
from gevent import monkey
monkey.patch_all()

import signal

from app import app
from gunicorn.app.base import BaseApplication

class CustomApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(CustomApp, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def when_ready(self):
        print('server ready')

    def run(self):
        def handle_stop_signal(sig, frame):
            gevent.killall()
            super().stop()
        signal.signal(signal.SIGINT, handle_stop_signal)
        super().run()

if __name__ == '__main__':
    options = {
        'bind': '0.0.0.0:5000',
        'workers': 2,
        'worker_class': 'gevent',
        "loglevel": "debug",
        'when_ready': CustomApp.when_ready
    }
    CustomApp(app, options).run()
