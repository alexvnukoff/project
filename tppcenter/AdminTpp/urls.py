from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.AdminTpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', tppcenter.AdminTpp.views.dashboard, name='main'),
    url(r'^users/$', tppcenter.AdminTpp.views.users, name='users'),
    url(r'^adv/$', tppcenter.AdminTpp.views.adv, name='adv'),
    url(r'^adv/activate/([0-9]+)/$', tppcenter.AdminTpp.views.advActivate),
    url(r'^adv/deactivate/([0-9]+)/$', tppcenter.AdminTpp.views.advDeactivate),
    url(r'^adv/targets/([0-9]+)/$', tppcenter.AdminTpp.views.advTargets),
)