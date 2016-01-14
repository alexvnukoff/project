from django.conf.urls import url

import b24online.Messages.views

urlpatterns = [
    url(r'^$', b24online.Messages.views.view_messages, name='main'),
    url(r'^(?P<recipient_id>[0-9]+)/$', b24online.Messages.views.view_messages, name="message_item"),
    url(r'^add/$', b24online.Messages.views.add_message, name="add"),
]
