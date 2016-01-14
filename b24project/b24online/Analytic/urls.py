from django.conf.urls import url

import b24online.Analytic.views

urlpatterns = [
    url(r'^$', b24online.Analytic.views.main, name='main'),
    url(r'^get/$', b24online.Analytic.views.get_analytic, name='get_analytic'),
]
