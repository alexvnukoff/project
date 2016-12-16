from django.conf.urls import url

from b24online.api.v1.views import wall, news, products, projects, proposals, exhibitions

urlpatterns = [
    url(r'^wall/$', wall, name='wall'),
    url(r'^news/$', news, name='news'),
    url(r'^b2b-products/$', products, name='b2b_products'),
    url(r'^projects/$', projects, name='projects'),
    url(r'^proposals/$', proposals, name='proposals'),
    url(r'^exhibitions/$', exhibitions, name='exhibitions')
]
