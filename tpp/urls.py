from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
import appl.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'tpp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/$', appl.views.set_news_list),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
)
