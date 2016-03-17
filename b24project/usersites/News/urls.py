from django.conf.urls import url
from django.utils.translation import ugettext as _

from usersites.News.views import NewsDetail
from usersites.views import render_page

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'News/contentPage.html', 'title': _("News")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'News/contentPage.html', 'title': _("News")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', NewsDetail.as_view(), name='detail'),
]
