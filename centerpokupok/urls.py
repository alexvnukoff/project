from django.conf.urls import patterns, include, url
import appl.views
import centerpokupok.views
import centerpokupok.News.urls
import centerpokupok.Product.urls
import centerpokupok.Reviews.urls
import centerpokupok.Coupons.urls
import centerpokupok.Categories.urls
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.views.home),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', centerpokupok.views.about),
    url(r'^news/', include("centerpokupok.News.urls", namespace="news")),
    url(r'^products/', include("centerpokupok.Product.urls", namespace="products")),
    url(r'^reviews/', include("centerpokupok.Reviews.urls", namespace="reviews")),
    url(r'^coupons/', include("centerpokupok.Coupons.urls", namespace="coupons")),
    url(r'^categories/', include("centerpokupok.Categories.urls", namespace="categories")),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)
