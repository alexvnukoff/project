# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from paypal.standard.ipn.views import ipn
import usersites.Api.urls
import usersites.B2BProducts.urls
import usersites.B2CProducts.urls
import usersites.Messages.urls
import usersites.News.urls
import usersites.OrganizationPages.urls
import usersites.Proposals.urls
import usersites.Questionnaires.urls
import usersites.Video.urls
import usersites.Exhibitions.urls
import usersites.Category.urls
import usersites.BusinessIndex.urls
import usersites.views
from appl import func
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^$', usersites.views.WallView.as_view(), name='main'),
    url(r'^news/', include(usersites.News.urls, namespace='news')),
    url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
    url(r'^b2b-products/', include(usersites.B2BProducts.urls, namespace='b2b_products')),
    url(r'^b2c-products/', include(usersites.B2CProducts.urls, namespace='b2c_products')),
    url(r'^pages/', include(usersites.OrganizationPages.urls, namespace='pages')),
    url(r'^video/', include(usersites.Video.urls, namespace='video')),
    url(r'^exhibitions/', include(usersites.Exhibitions.urls, namespace='exhibitions')),
    url(r'^sendmessage/$', usersites.views.sendmessage.as_view(), name='sendmessage'),
    url(r'^message_sent/$', usersites.views.MessageSent.as_view(), name='message_sent'),
    url(r'^business_index/', include(usersites.BusinessIndex.urls, namespace='business_index')),

    # Additionals
    url(r'^api/', include(usersites.Api.urls)),
    url(r'^profile/$', usersites.views.ProfileUpdate.as_view(), name='my_profile'),
    url(r'^profile/change_password/$', usersites.views.ChangePassword.as_view(), name='change_password'),
    url(r'^profile/change_password/done/$', usersites.views.ChangePasswordDone.as_view(), name='change_password_done'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^ipn/', ipn, {'item_check_callable': func.verify_ipn_request}, name='paypal-ipn'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^denied/$', TemplateView.as_view(template_name="usersites/denied.html"), name='denied'),
    # url(r'^new/$', TemplateView.as_view(template_name="usersites_angular/index.html")),
    #url(r'^$', render_page, kwargs={'template': 'News/contentPage.html', 'title': _("News")}, name='main'),
    #url(r'^page(?P<page>[0-9]+)?/$', render_page, kwargs={'template': 'News/contentPage.html', 'title': _("News")}, name="paginator"),
    #url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', NewsDetail.as_view(), name='detail'),
    url(r'^questionnaires/', include(usersites.Questionnaires.urls, namespace='questionnaires')),
    url(r'^messages/', include(usersites.Messages.urls, namespace='messages')),
    url(r'^landing/$', usersites.views.LandingView.as_view(), name='landing'),
]

if settings.DEBUG:
    import debug_toolbar
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()
