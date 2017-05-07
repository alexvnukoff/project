from django.conf.urls import url
from django.utils.translation import ugettext as _

from b24online.Project.views import show_page, project

urlpatterns = [
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', show_page, name="detail"),
    url(r'^terms/$', project, {'template': "terms.html", 'section': _('Terms of use')}, name='terms'),
]
