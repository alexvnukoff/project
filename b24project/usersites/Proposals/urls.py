from django.conf.urls import url
from django.utils.translation import ugettext as _

from usersites.Proposals.views import BusinessProposalDetail
from usersites.views import render_page

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'Proposals/contentPage.html', 'title': _("Business proposals")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'Proposals/contentPage.html', 'title': _("Business proposals")}, name="paginator"),
    url(r'^(?P<slug>[0-9a-zA-z-]+)-(?P<pk>[0-9]+)\.html$', BusinessProposalDetail.as_view(), name='detail'),
]
