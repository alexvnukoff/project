from importlib import import_module
import tornado
import tornadoredis
from sockjs.tornado import SockJSConnection
import django
from django.conf import settings
import json

# start of kmike's sources
_engine = import_module(settings.SESSION_ENGINE)


def get_session(session_key):
    return _engine.SessionStore(session_key)


def get_current_company(session):
    return session._session.get('current_company', False)


def get_user(session):
    class Dummy(object):
        pass

    django_request = Dummy()
    django_request.session = session
    return django.contrib.auth.get_user(django_request)


# end of kmike's sources


# конфиг для подключения к redis можно хранить в настройках django
ORDERS_REDIS_HOST = getattr(settings, 'ORDERS_REDIS_HOST', 'localhost')
ORDERS_REDIS_PORT = getattr(settings, 'ORDERS_REDIS_PORT', 6379)
ORDERS_REDIS_PASSWORD = getattr(settings, 'ORDERS_REDIS_PASSWORD', None)
ORDERS_REDIS_DB = getattr(settings, 'ORDERS_REDIS_DB', None)


class Connection(SockJSConnection):
    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.listen_redis()

    @tornado.gen.engine
    def listen_redis(self):
        """
            Вешаем подписчиков на каналы сообщений.
        """
        self.redis_client = tornadoredis.Client(
            host=ORDERS_REDIS_HOST,
            port=ORDERS_REDIS_PORT,
            password=ORDERS_REDIS_PASSWORD,
            selected_db=ORDERS_REDIS_DB
        )
        self.redis_client.connect()

        yield tornado.gen.Task(self.redis_client.subscribe, [
            'notification',
            'private_message',
            'partner'
        ])
        self.redis_client.listen(self.on_redis_queue)  # при получении сообщения
        #  вызываем self.on_redis_queue

    def send(self, msg_type, message):
        """
        Оправка сообщений.
        """
        return super(Connection, self).send(json.dumps({
            'type': msg_type,
            'data': message,
        }))

    def on_open(self, request):
        """
        Определяем сессию django.
        """
        self.django_session = get_session(request.get_cookie('sessionid').value)
        self.user = get_user(self.django_session)
        print(self.user)
        self.current_company = get_current_company(self.django_session)
        print(self.current_company)

    def on_message(self, msg):
        """
        Обязательный метод.
        """
        pass

    def on_redis_queue(self, message):
        """
        Обновление в списке заказов
        """
        print(message)
        if message.kind == 'message':  
            message_body = json.loads(message.body) 
            if message.channel == 'notification' and \
                message_body.get('user', False) == self.user.pk:
                self.send_notification(message, message_body)
            elif message.channel == 'private_message':
                recipient = message_body.get('recipient', False)
                if int(recipient) == self.user.pk:
                    self.send_notification(message, message_body)

    def send_notification(self, message, message_body):
        self.send(message.channel, message_body)

    def on_close(self):
        """
        При закрытии соединения отписываемся от сообщений
        """
        self.redis_client.unsubscribe([
            'notification',
            'private_message',
            'partner'
        ])
        self.redis_client.disconnect()
