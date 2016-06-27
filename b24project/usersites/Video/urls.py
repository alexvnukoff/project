from django.conf.urls import url
from django.utils.translation import ugettext as _

from usersites.Video.views import VideoDetail
from usersites.views import render_page

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'Video/contentPage.html', 'title': _("Video")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'Video/contentPage.html', 'title': _("Video")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', VideoDetail.as_view(), name='detail'),
]
