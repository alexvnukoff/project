from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.UserSites.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.UserSites.views.get_resume_list, name='main'),


     url(r'^add/$', tppcenter.UserSites.views.resumeForm,{'action': 'add'} , name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.UserSites.views.resumeForm,{'action': 'update'}, name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.UserSites.views.resumeForm ,{'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.UserSites.views.get_resume_list, name="detail"),






)