from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Companies.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Companies.views.get_companies_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Companies.views.get_companies_list, name="paginator"),
     url(r'^add/$', tppcenter.Companies.views.addCompany, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.Companies.views.updateCompany, name="update"),






)