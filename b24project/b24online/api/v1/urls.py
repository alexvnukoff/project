from django.conf.urls import url

from b24online.api.v1.views import wall, news

urlpatterns = [
    url(r'^wall/$', wall, name='wall'),
    url(r'^news/$', news, name='news')
]
