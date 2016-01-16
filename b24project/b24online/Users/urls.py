from django.conf.urls import url

import b24online.Users.views

urlpatterns = [
    url(r'^$', b24online.Users.views.UserList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', b24online.Users.views.UserList.as_view(), name="paginator"),
]
