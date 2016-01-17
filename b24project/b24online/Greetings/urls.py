from django.conf.urls import url

from b24online.Greetings.views import GreetingDetail, GreetingList

urlpatterns = [
     url(r'^$', GreetingList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', GreetingList.as_view(), name="paginator"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', GreetingDetail.as_view(), name="detail"),
]