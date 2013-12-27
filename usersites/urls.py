from django.conf.urls import patterns, include, url
import appl.views
import usersites.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.views.home),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/$', appl.views.set_news_list),
)
