from django.conf.urls import url
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from usersites.views import render_page
from usersites.B2CProducts.views import (B2CProductDetail, B2CProductBasket,
                                         B2CProductByEmail, B2CProductJsonData,
                                         B2C_orderDone)

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'B2CProducts/contentPage.html', 'title': _("B2C Products")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2CProducts/contentPage.html', 'title': _("B2C Products")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<category>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2CProducts/contentPage.html', 'title': _("B2C Products")}, name="category"),
    url(r'^p/(?P<slug>[a-zA-z0-9-]+)/$', render_page,
        kwargs={'template': 'B2CProducts/contentPage.html', 'title': _("B2C Products")}, name="category_paged"),
    url(r'^search/$', render_page,
        kwargs={'template': 'B2CProducts/searchPage.html', 'title': _("B2C Products")}, name="search"),
    url(r'^search/page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2CProducts/searchPage.html', 'title': _("B2C Products")}, name="search_paginator"),

    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', B2CProductDetail.as_view(), name='detail'),
    url(r'^basket\.html$', B2CProductBasket.as_view(), name='basket'),
    url(r'^order\.html$', B2CProductByEmail.as_view(), name='order_by_email'),
    url(r'^json/$', B2CProductJsonData.as_view(), name='b2c_product_json'),
    url(r'^order_done\.html$', B2C_orderDone.as_view(), name='order_done'),
]
