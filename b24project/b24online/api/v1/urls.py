from django.conf.urls import url

from b24online.api.v1.views import wall, news, projects, proposals, exhibitions, companies, chambers, \
    b2c_products, b2b_products, coupons, videos, vacancies, resumes

urlpatterns = [
    url(r'^wall/$', wall, name='wall'),
    url(r'^news/$', news, name='news'),
    url(r'^b2b-products/$', b2b_products, name='b2b_products'),
    url(r'^b2c-products/$', b2c_products, name='b2c_products'),
    url(r'^coupons/$', coupons, name='coupons'),
    url(r'^projects/$', projects, name='projects'),
    url(r'^proposals/$', proposals, name='proposals'),
    url(r'^exhibitions/$', exhibitions, name='exhibitions'),
    url(r'^companies/$', companies, name='companies'),
    url(r'^chambers/$', chambers, name='chambers'),
    url(r'^videos/$', videos, name='videos'),
    url(r'^vacancies/$', vacancies, name='vacancies'),
    url(r'^resumes/$', resumes, name='resumes'),
]
