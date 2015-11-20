from django.conf.urls import patterns, url
from django.contrib import admin
from usersites.B2CProducts.views import B2CProductList, B2CProductDetail, B2CProductBasket

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
                           B2CProductBasket, name='basket'),
                       )
