from django.conf.urls import patterns, url
from django.contrib import admin
from django.views.generic import TemplateView
from usersites.B2CProducts.views import B2CProductList, B2CProductDetail, B2CProductBasket, B2CProductSearch, B2CProductByEmail

admin.autodiscover()

urlpatterns = patterns('',

         url(r'^$', B2CProductList.as_view(), name='main'),
         url(r'^page(?P<page>[0-9]+)?/$', B2CProductList.as_view(),
             name="paginator"),
         url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)?/$', B2CProductList.as_view(),
             name="category"),
         url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)?/page(?P<page>[0-9]+)?/$',
             B2CProductList.as_view(),
             name="category_paged"),
         url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$',
             B2CProductDetail.as_view(), name='detail'),
         url(r'^basket\.html$',
             B2CProductBasket.as_view(), name='basket'),

         url(r'^search/$', B2CProductSearch.as_view(), name="search"),
         url(r'^search/page(?P<page>[0-9]+)?/$', B2CProductSearch.as_view(), name="serch_paginator"),
         url(r'^order\.html$', B2CProductByEmail.as_view(), name='order_by_email'),
         url(r'^order_done\.html$', TemplateView.as_view(template_name='usersites/B2CProducts/orderDone.html', \
                                    content_type='text/html'), name='order_done'),

                       )
