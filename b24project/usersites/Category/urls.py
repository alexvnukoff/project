# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from usersites.views import render_page
from usersites.Category import views

urlpatterns = [
    url(r'^all/$', views.CategoriesView.as_view(), name='all'),
]
