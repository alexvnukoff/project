from django.conf.urls import url
from django.views.generic import TemplateView
from b24online.Profile.views import ChangePassword, ProfileView, ProfilePromote, PromoteDel

urlpatterns = [
    url(r'^$', ProfileView.as_view(), name='main'),
    url(r'^change_password/$', ChangePassword.as_view(), name='change_password'),
    url(r'^change_password/done/$',
        TemplateView.as_view(template_name="b24online/Profile/changePassword_done.html"),
            name='change_password_done'),
    url(r'^promote/(?P<type>(b2bproduct|b2cproduct|businessproposal|news))/(?P<item_id>[0-9]+)$',
        ProfilePromote, name="promote"),
    url(r'^promote/del/(?P<type>(b2bproduct|b2cproduct|businessproposal|news))/$',
        PromoteDel, name="promote_del"),
]
