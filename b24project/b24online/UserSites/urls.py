from django.conf.urls import url

from b24online.UserSites.views import form_dispatch

urlpatterns = [url(r'^$', form_dispatch, name='main')]
