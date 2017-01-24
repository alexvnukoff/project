from django.conf.urls import url
from django.utils.translation import ugettext as _

from usersites.Exhibitions.views import ExhibitionDetail
from usersites.views import render_page

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'Exhibitions/contentPage.html', 'title': _("Exhibitions")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'Exhibitions/contentPage.html', 'title': _("Exhibitions")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', ExhibitionDetail.as_view(), name='detail'),
]
