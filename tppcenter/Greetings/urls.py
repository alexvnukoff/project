from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Greetings.views
import tppcenter.views


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Greetings.views.GreetingList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Greetings.views.GreetingList.as_view(), name="paginator"),
     url(r'^(?P<slug>[0-9a-zA-z-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.Greetings.views.GreetingDetail.as_view(), name="detail"),

)