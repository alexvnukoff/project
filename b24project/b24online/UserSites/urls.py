from django.conf.urls import url

from b24online.UserSites.views import form_dispatch, TemplateUpdate
from django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^$',
        form_dispatch,
        name='main'),

    url(r'templates/$',
        login_required(TemplateUpdate.as_view()),
        name='template'),

]
