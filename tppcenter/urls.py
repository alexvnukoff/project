from django.conf.urls import patterns, include, url
import appl.views
from django.contrib.auth import views as auth_views

import tppcenter.views
import tppcenter.News.urls


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', tppcenter.views.home),
    url(r'^news/', include(tppcenter.News.urls, namespace='news')),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/', tppcenter.views.user_login, name='login' ),
    url(r'^logout/', tppcenter.views.user_logout, name='logout' ),
    url(r'^registartion/', tppcenter.views.registration, name='register' ),


    url(r'^test/', tppcenter.views.test),
    url(r'^test2/', tppcenter.views.test2),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^items/$', tppcenter.views.set_items_list),
    url(r'^items/([a-zA-Z]+)/$', tppcenter.views.set_item_list),
    url(r'^items/([a-zA-Z]+)/create/$', tppcenter.views.get_item_form),
    url(r'^items/([a-zA-Z]+)/update/([0-9]+)/$', tppcenter.views.update_item),
    url(r'^items/([a-zA-Z]+)/showlist/([0-9]+)/$', tppcenter.views.showlist),

    url(r'^notification/get/$', tppcenter.views.getNotifList),
    url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^accounts/', include('registration.backends.default.urls')),


)