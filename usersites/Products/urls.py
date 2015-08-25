from django.conf.urls import patterns, url, include
from django.contrib import admin

import usersites.Products.views
import usersites.views



admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.Products.views.get_products_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', usersites.Products.views.get_products_list, name="paginator"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', usersites.Products.views.get_products_list, name='detail'),

)