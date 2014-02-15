from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
import appl.views
from legacy_data import views as leg_v

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'tpp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/$', appl.views.set_news_list),

    url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', appl.views.cabinet),

    url(r'^legacy/user/csvdb$', leg_v.users_reload_CSV_DB),
    url(r'^legacy/user/dbdb$', leg_v.users_reload_DB_DB),
    url(r'^legacy/user/email$', leg_v.users_reload_email_sent),
    url(r'^legacy/company/csvdb$', leg_v.company_reload_CSV_DB),
)
