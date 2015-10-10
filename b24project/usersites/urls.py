from django.conf import settings
from django.conf.urls import patterns, include, url
from paypal.standard.ipn.views import ipn
from appl import func

import usersites.views
import usersites.OrganizationPages.urls
import usersites.News.urls
import usersites.Proposals.urls
import usersites.B2BProducts.urls
import usersites.B2CProducts.urls

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', usersites.views.wall, name='main'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^news/', include(usersites.News.urls, namespace='news')),
                       url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
                       url(r'^b2b-products/', include(usersites.B2BProducts.urls, namespace='b2b_products')),
                       url(r'^b2c-products/', include(usersites.B2CProducts.urls, namespace='b2c_products')),
                       url(r'^pages/', include(usersites.OrganizationPages.urls, namespace='pages')),
                       url(r'^ipn/', ipn, {'item_check_callable': func.verify_ipn_request}, name='paypal-ipn'),
                       )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
