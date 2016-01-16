from django.conf.urls import url

import b24online.Greetings.views

urlpatterns = [
     url(r'^$', b24online.Greetings.views.GreetingList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', b24online.Greetings.views.GreetingList.as_view(), name="paginator"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.Greetings.views.GreetingDetail.as_view(), name="detail"),
]