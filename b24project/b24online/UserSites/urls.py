# -*- encoding: utf-8 -*-
from django.conf.urls import url
from b24online.UserSites.views import (
    form_dispatch, UserTemplateView, TemplateUpdate, LandingPageView,
    DomainNameView, LanguagesView, ProductDeliveryView, SiteSloganView,
    FooterTextView, SiteLogoView, SliderImagesView, BannersView,
    SocialLinksView, GAnalyticsView, FacebookPixelView
    )

from django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^$', form_dispatch, name='main'),

    url(r'templates/$',
        login_required(UserTemplateView.as_view()),
        name='template'),

    url(r'templates/(?P<pk>[0-9]+)/$',
        login_required(TemplateUpdate.as_view()),
        name='color'),

    url(r'landing_page/$',
        login_required(LandingPageView.as_view()),
        name='landing_page'),

    url(r'domain_name/$',
        login_required(DomainNameView.as_view()),
        name='domain_name'),

    url(r'site_languages/$',
        login_required(LanguagesView.as_view()),
        name='site_languages'),

    url(r'product_delivery/$',
        login_required(ProductDeliveryView.as_view()),
        name='product_delivery'),

    url(r'site_slogan/$',
        login_required(SiteSloganView.as_view()),
        name='site_slogan'),

    url(r'footer_text/$',
        login_required(FooterTextView.as_view()),
        name='footer_text'),

    url(r'site_logo/$',
        login_required(SiteLogoView.as_view()),
        name='site_logo'),

    url(r'slider_images/$',
        login_required(SliderImagesView.as_view()),
        name='slider_images'),

    url(r'banners/$',
        login_required(BannersView.as_view()),
        name='banners'),

    url(r'social_links/$',
        login_required(SocialLinksView.as_view()),
        name='social_links'),

    url(r'google_analytics/$',
        login_required(GAnalyticsView.as_view()),
        name='google_analytics'),

    url(r'facebook_pixel/$',
        login_required(FacebookPixelView.as_view()),
        name='facebook_pixel'),
]