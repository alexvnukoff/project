import tornado
from django.core.management.base import NoArgsCommand
from sockjs.tornado import SockJSRouter
from core.tests import Connection


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        router = SockJSRouter(Connection, '/orders')  # sockjs не захотел работать с корнем :(
        app = tornado.web.Application(router.urls)
        app.listen(8989)
        tornado.ioloop.IOLoop.instance().start()
