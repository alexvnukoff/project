from django.conf.urls import patterns, url
from django.contrib import admin
from usersites.News.views import NewsList, NewsDetail

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', NewsList.as_view(), name='main'),
                       url(r'^page(?P<page>[0-9]+)?/$', NewsList.as_view(), name="paginator"),
                       url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', NewsDetail.as_view(), name='detail'),
                       )
