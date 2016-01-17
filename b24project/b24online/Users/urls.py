from django.conf.urls import url

from b24online.Users.views import UserList

urlpatterns = [
    url(r'^$', UserList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', UserList.as_view(), name="paginator"),
]
