from django.conf.urls import patterns, url, include
from django.contrib import admin

import usersites.CompanyStructure.views
import usersites.views
import tppcenter.urls


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.CompanyStructure.views.get_structure_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', usersites.CompanyStructure.views.get_structure_list, name="paginator"),


)