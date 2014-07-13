from django.conf.urls import patterns, include, url
from appl.models import Country, Tpp, Branch
import appl.views
import tppcenter.AdminTpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', tppcenter.AdminTpp.views.users, name='main'),
    url(r'^users/$', tppcenter.AdminTpp.views.users, name='users'),
    url(r'^adv/$', tppcenter.AdminTpp.views.adv, name='adv'),
    url(r'^adv/activate/([0-9]+)/$', tppcenter.AdminTpp.views.advActivate),
    url(r'^adv/deactivate/([0-9]+)/$', tppcenter.AdminTpp.views.advDeactivate),
    url(r'^adv/targets/([0-9]+)/$', tppcenter.AdminTpp.views.advTargets),
    url(r'^adv/prices/save/$', tppcenter.AdminTpp.views.adv_save_price, name='adv_save_price'),
    url(r'^adv/prices/load/country/$', tppcenter.AdminTpp.views.adv_price, {'ladModel': Country}, name='adv_load_country'),
    url(r'^adv/prices/load/tpp/$', tppcenter.AdminTpp.views.adv_price, {'ladModel': Tpp}, name='adv_load_tpp'),
    url(r'^adv/prices/load/branch/$', tppcenter.AdminTpp.views.adv_price, {'ladModel': Branch}, name='adv_load_branch'),
    url(r'^adv/prices/$', tppcenter.AdminTpp.views.adv_price, name='adv_price'),
    url(r'^adv/settings/$', tppcenter.AdminTpp.views.adv_settings, name='adv_sett'),
    url(r'^adv/delete-type/([0-9]+)/$', tppcenter.AdminTpp.views.adv_remove_banner_type),
    url(r'^pages/$', tppcenter.AdminTpp.views.pages, name="pages"),
    url(r'^pages/edit/([0-9]+)/$', tppcenter.AdminTpp.views.pages, name="pages_edit"),
    url(r'^pages/delete/([0-9]+)/$', tppcenter.AdminTpp.views.pages_delete, name="pages_delete"),
    url(r'^greetings/$', tppcenter.AdminTpp.views.greetings, name="greetings"),
    url(r'^greetings/edit/([0-9]+)/$', tppcenter.AdminTpp.views.greetings, name="greetings_edit"),
    url(r'^greetings/delete/([0-9]+)/$', tppcenter.AdminTpp.views.greetings_delete, name="greetings_delete"),

)