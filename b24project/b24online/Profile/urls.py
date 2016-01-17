from django.conf.urls import url

from b24online.Profile.views import ProfileUpdate

urlpatterns = [url(r'^$', ProfileUpdate.as_view(), name='main')]
