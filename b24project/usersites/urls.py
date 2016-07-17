from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from paypal.standard.ipn.views import ipn

import usersites.Api.urls
import usersites.B2BProducts.urls
import usersites.B2CProducts.urls
import usersites.Messages.urls
import usersites.News.urls
import usersites.OrganizationPages.urls
import usersites.Proposals.urls
import usersites.Questionnaires.urls
import usersites.Video.urls

import usersites.views

from appl import func

urlpatterns = [
    url(r'^$', usersites.views.wall, name='main'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^profile/$', usersites.views.ProfileUpdate.as_view(), name='my_profile'),
    url(r'^new/$', TemplateView.as_view(template_name="usersites_angular/index.html")),
    url(r'^api/', include(usersites.Api.urls, namespace='api')),
    url(r'^news/', include(usersites.News.urls, namespace='news')),
    url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
    url(r'^b2b-products/', include(usersites.B2BProducts.urls, namespace='b2b_products')),
    url(r'^b2c-products/', include(usersites.B2CProducts.urls, namespace='b2c_products')),
    url(r'^pages/', include(usersites.OrganizationPages.urls, namespace='pages')),
    url(r'^ipn/', ipn, {'item_check_callable': func.verify_ipn_request}, name='paypal-ipn'),
    url(r'^questionnaires/',
        include(usersites.Questionnaires.urls, namespace='questionnaires')),
    url(r'^denied/$',
        TemplateView.as_view(template_name="usersites/denied.html"),
        name='denied'),
    url(r'^video/', include(usersites.Video.urls, namespace='video')),
    url(r'^messages/', include(usersites.Messages.urls, namespace='messages')),
    url(r'^sendmessage/$', usersites.views.sendmessage.as_view(), name='sendmessage'),
]

if settings.DEBUG:
    import debug_toolbar
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()
