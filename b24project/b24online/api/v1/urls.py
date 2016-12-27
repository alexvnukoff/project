from django.conf.urls import url

from b24online.Video.views import VideoList
from b24online.api.v1.views import CompanyList, ResumeList, VacancyList, ChamberList, \
    ExhibitionList, ProposalList, ProjectList, CouponList, B2CProductList, B2BProductList, NewsList, Wall

urlpatterns = [
    url(r'^wall/$', Wall.as_view(), name='wall'),
    url(r'^news/$', NewsList.as_view(), name='news'),
    url(r'^b2b-products/$', B2BProductList.as_view(), name='b2b_products'),
    url(r'^b2c-products/$', B2CProductList.as_view(), name='b2c_products'),
    url(r'^coupons/$', CouponList.as_view(), name='coupons'),
    url(r'^projects/$', ProjectList.as_view(), name='projects'),
    url(r'^proposals/$', ProposalList.as_view(), name='proposals'),
    url(r'^exhibitions/$', ExhibitionList.as_view(), name='exhibitions'),
    url(r'^companies/$', CompanyList.as_view(), name='companies'),
    url(r'^chambers/$', ChamberList.as_view(), name='chambers'),
    url(r'^videos/$', VideoList.as_view(), name='videos'),
    url(r'^vacancies/$', VacancyList.as_view(), name='vacancies'),
    url(r'^resumes/$', ResumeList.as_view(), name='resumes'),
]
