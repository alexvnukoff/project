from django.conf.urls import patterns, url
from usersites.Api.views import SiteSettings, SiteBarMenu, actions

urlpatterns = patterns('',
                       url(r'^settings.json$', SiteSettings.as_view()),
                       url(r'^actions.json$', actions),
                       url(r'^siteBarMenu.json$', SiteBarMenu.as_view()),
                       # url(r'^gallery.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^news.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^offers.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^products.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^products.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^menu.json$', NewsList.as_view(), name="paginator"),
                       # url(r'^structure.json$', NewsList.as_view(), name="paginator"),
                       )
