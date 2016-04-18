# -*- encoding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from usersites.views import UsersitesRegistrationView

urlpatterns = [
    url(r'^register/$', UsersitesRegistrationView.as_view(), 
        name='registration_register'),   
    url(r'', include('registration.auth_urls')),
]
