from django.conf.urls import url
from b24online.UserSites.views import form_dispatch
from django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^$',
        form_dispatch,
        name='main'),

    # url(r'templates/$',
    #     login_required(UserTemplateView.as_view()),
    #     name='template'),
    #
    # url(r'templates/(?P<pk>[0-9]+)/$',
    #     login_required(TemplateUpdate.as_view()),
    #     name='color'),

]
