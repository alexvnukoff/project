from django.conf.urls import url
from django.views.generic import TemplateView
from b24online.Profile.views import ProfileUpdate, ChangePassword

urlpatterns = [
    url(r'^$', ProfileUpdate.as_view(), name='main'),
    url(r'^change_password/$', ChangePassword.as_view(), name='change_password'),
    url(r'^change_password/done/$', TemplateView.as_view(template_name="b24online/Profile/changePassword_done.html"), name='change_password_done'),
]
