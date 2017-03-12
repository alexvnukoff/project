from django.conf.urls import url
from django.views.generic import TemplateView

from usersites.OrganizationPages.views import (Contacts, PageDetail,
        Structure, About, Gallery, CompanyView)

urlpatterns = [
    url(r'^about/$', About.as_view(), name='about'),
    url(r'^structure/$', Structure.as_view(), name='structure'),
    url(r'^contacts/$', Contacts.as_view(), name='contacts'),
    url(r'^gallery/$', Gallery.as_view(), name='gallery'),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', PageDetail.as_view(), name='detail'),
    url(r'^company/(?P<pk>[0-9]+)/detail/$', CompanyView.as_view(), name='company'),
]
