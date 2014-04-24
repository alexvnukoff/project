from django.conf.urls import patterns, include, url

import usersites.views
import usersites.News.urls


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.views.home),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/', include(usersites.News.urls, namespace='news')),
)
