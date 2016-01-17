from django.conf.urls import url

from b24online.Messages.views import view_messages, add_message

urlpatterns = [
    url(r'^$', view_messages, name='main'),
    url(r'^(?P<recipient_id>[0-9]+)/$', view_messages, name="message_item"),
    url(r'^add/$', add_message, name="add"),
]
