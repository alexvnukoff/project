import tornado
from django.core.management.base import BaseCommand
from sockjs.tornado import SockJSRouter
from appl.realtime import Connection
import signal
import time

class Command(BaseCommand):

    def sig_handler(self, sig, frame):
        """Catch signal and init callback"""
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def handle(self, *args, **options):
        router = SockJSRouter(Connection, '/echo')
        app = tornado.web.Application(router.urls)
        app.listen(9998)

        # Init signals handler
        signal.signal(signal.SIGTERM, self.sig_handler)

        # This will also catch KeyboardInterrupt exception
        signal.signal(signal.SIGINT, self.sig_handler)

        tornado.ioloop.IOLoop.instance().start()

    def shutdown(self):

        #Connection.close()
        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.add_timeout(time.time() + 2, io_loop.stop)

