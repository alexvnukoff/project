from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from loginas.views import user_login
#from tppcenter.sitemaps import all_sitemaps as sitemaps

import tppcenter.views
import tppcenter.News.urls
import tppcenter.Product.urls
import tppcenter.Companies.urls
import tppcenter.Innov.urls
import tppcenter.Tpp.urls
import tppcenter.BusinessProposal.urls
import tppcenter.Exhibitions.urls
import tppcenter.Tenders.urls
import tppcenter.TppTV.urls
import tppcenter.Profile.urls
import tppcenter.Messages
import tppcenter.Messages.urls
import tppcenter.Wall.urls
import tppcenter.AdvBanner
import tppcenter.AdvBanner.urls
import tppcenter.AdvTop
import tppcenter.AdvTop.urls
import tppcenter.Project
import tppcenter.Project.urls
import tppcenter.Analytic
import tppcenter.Analytic.urls
import tppcenter.Greetings
import tppcenter.Greetings.urls
import tppcenter.Resume.urls
import tppcenter.Vacancy.urls
import tppcenter.Users.urls
import tppcenter.Payments.urls


import tppcenter.UserSites.urls

import tppcenter.AdminTpp
import tppcenter.AdminTpp.urls

import tppcenter.Adv
import tppcenter.Adv.urls

from tppcenter.News.views import NewsFeed


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', tppcenter.views.home, name="main"),
    url(r"^login/user/(?P<user_id>.+)/$", user_login, name="loginas-user-login"),
    #url(r'^addcon/', tppcenter.views.buildCountries),
    #url(r'^addTemp/', tppcenter.views.builTemplate),
    url(r'^news/', include(tppcenter.News.urls, namespace='news')),
    url(r'^products/', include(tppcenter.Product.urls, namespace='products')),
    url(r'^innovation/', include(tppcenter.Innov.urls, namespace='innov')),
    url(r'^companies/', include(tppcenter.Companies.urls, namespace='companies')),
    url(r'^tpp/', include(tppcenter.Tpp.urls, namespace='tpp')),
    url(r'^proposal/', include(tppcenter.BusinessProposal.urls, namespace='proposal')),
    url(r'^exhibitions/', include(tppcenter.Exhibitions.urls, namespace='exhibitions')),
    url(r'^tenders/', include(tppcenter.Tenders.urls, namespace='tenders')),
    url(r'^vacancy/', include(tppcenter.Vacancy.urls, namespace='vacancy')),
    url(r'^tv/', include(tppcenter.TppTV.urls, namespace='tv')),
    url(r'^profile/', include(tppcenter.Profile.urls, namespace='profile')),
    url(r'^wall/', include(tppcenter.Wall.urls, namespace='wall')),
    url(r'^greetings/', include(tppcenter.Greetings.urls, namespace='greetings')),
    url(r'^analytic/', include(tppcenter.Analytic.urls, namespace='analytic')),
    url(r'^resume/', include(tppcenter.Resume.urls, namespace='resume')),
    url(r'^site/', include(tppcenter.UserSites.urls, namespace='site')),
    url(r'^users/', include(tppcenter.Users.urls, namespace='users')),
    url(r'^payments/', include(tppcenter.Payments.urls, namespace='payments')),
    url(r'^upload/yandex_news_rss.xml$', NewsFeed()),


    url(r'^admin-tpp/', include(tppcenter.AdminTpp.urls, namespace='AdminTpp')),


    url(r'^register/exhibition/$', tppcenter.views.register_to_exhibition),

    url(r'^denied/', tppcenter.views.perm_denied, name='denied'),

    url(r'^messages/', include(tppcenter.Messages.urls, namespace='messages')),
    url(r'^advbanner/', include(tppcenter.AdvBanner.urls, namespace='adv_banners')),
    url(r'^advtop/', include(tppcenter.AdvTop.urls, namespace='adv_top')),
    url(r'^adv/', include(tppcenter.Adv.urls, namespace='Adv')),




    # url(r'^blog/', include('blog.urls')),
    url(r'^login/', tppcenter.views.user_login, name='login'),
    url(r'^logout/', tppcenter.views.user_logout, name='logout'),
    url(r'^registration/', tppcenter.views.registration, name='register'),

    url(r'^project/', include(tppcenter.Project.urls, namespace='project')),


    #url(r'^test/', tppcenter.views.test),
    #url(r'^test2/', tppcenter.views.test2),
    url(r'^ping/', tppcenter.views.ping),
    url(r'^admin/tpp/', include(admin.site.urls)),

    #url(r'^adv/paypal/', include('paypal.standard.ipn.urls')),



    #url(r'^items/$', tppcenter.views.set_items_list),
    #url(r'^items/([a-zA-Z]+)/$', tppcenter.views.set_item_list),
    #url(r'^items/([a-zA-Z]+)/create/$', tppcenter.views.get_item_form),
    #url(r'^items/([a-zA-Z]+)/update/([0-9]+)/$', tppcenter.views.update_item),
    #url(r'^items/([a-zA-Z]+)/showlist/([0-9]+)/$', tppcenter.views.showlist),



    url(r'^notification/get/$', tppcenter.views.get_notification_list),
    url(r'^addPage/get/$', tppcenter.views.get_additional_page),
    # url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    # url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),
    # url(r'^accounts/password/reset/$', auth_views.password_reset, name='password_reset'),
    # url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    # url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^accounts/', include('registration.backends.default.urls')),





    url(r'^adv/tops/', tppcenter.views.get_live_top),
    url(r'^adv/bann/', tppcenter.views.get_live_banner),
    url(r'^filter/', tppcenter.views.json_filter),
    url(r'^company-manage/', tppcenter.views.my_companies),
    url(r'^set/(?P<item_id>[0-9]+)/$', tppcenter.views.set_current, name="setCurrent"),



)

import debug_toolbar
urlpatterns += patterns('',
    url(r'^__debug__/', include(debug_toolbar.urls)),
)
#urlpatterns += patterns('',
#        (r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
#        (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
#)

