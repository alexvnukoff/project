from django.conf.urls import url

import b24online.UserSites.views

urlpatterns = [url(r'^$', b24online.UserSites.views.form_dispatch, name='main')]
