from django.conf.urls import url

from b24online.AdminTpp.views import Dashboard, Users, Adv, AdvTargets, AdvPrice, AdvSettings, StaticPageDelete, \
    StaticPageUpdate, StaticPageCreate, GreetingCreate, GreetingUpdate, GreetingDelete

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^load/(?P<model>[A-z0-9]+)/$', Dashboard.as_view(), name='dashboard_load'),
    url(r'^users/$', Users.as_view(), name='users'),
    url(r'^adv/$', Adv.as_view(), name='adv'),
    url(r'^adv/targets/(?P<pk>[0-9]+)/$', AdvTargets.as_view(), name='adv_targets'),
    url(r'^adv/prices/$', AdvPrice.as_view(), name='adv_price'),
    url(r'^adv/prices/load/(?P<model>[A-z0-9]+)/$', AdvPrice.as_view(), name='price_load'),
    url(r'^adv/settings/$', AdvSettings.as_view(), name='adv_sett'),
    url(r'^pages/$', StaticPageCreate.as_view(), name="pages"),
    url(r'^pages/edit/(?P<pk>[0-9]+)/$', StaticPageUpdate.as_view(), name="pages_edit"),
    url(r'^pages/delete/(?P<pk>[0-9]+)/$', StaticPageDelete.as_view(), name="pages_delete"),
    url(r'^greetings/$', GreetingCreate.as_view(), name="greetings"),
    url(r'^greetings/edit/(?P<pk>[0-9]+)/$', GreetingUpdate.as_view(), name="greetings_edit"),
    url(r'^greetings/delete/(?P<pk>[0-9]+)/$', GreetingDelete.as_view(), name="greetings_delete"),
]
