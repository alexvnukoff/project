from django.conf.urls import url

import b24online.Profile.views

urlpatterns = [url(r'^$', b24online.Profile.views.ProfileUpdate.as_view(), name='main')]
