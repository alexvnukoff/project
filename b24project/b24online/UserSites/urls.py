# -*- encoding: utf-8 -*-
from django.conf.urls import url
from b24online.UserSites.views import (
    form_dispatch,
    UserTemplateView,
    TemplateUpdate,
    LandingPageView,
    DomainNameView

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


]