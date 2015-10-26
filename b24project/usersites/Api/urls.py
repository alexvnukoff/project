from django.conf.urls import patterns, url
from usersites.Api.views import SiteSettings

urlpatterns = patterns('',
                       url(r'^settings.json$', SiteSettings.as_view(), name='main'),
                       url(r'^actions.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^categories.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^gallery.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^news.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^offers.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^products.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^products.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^menu.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^structure.json$', NewsList.as_view(), name="paginator"),
                       )
