from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
import appl.views
import centerpokupok.views
import centerpokupok.News.urls
import centerpokupok.Product.urls
import centerpokupok.Reviews.urls
import centerpokupok.Coupons.urls

from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.views.home, name="main"),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', centerpokupok.views.about),
    url(r'^news/', include("centerpokupok.News.urls", namespace="news")),
    url(r'^products/', include("centerpokupok.Product.urls", namespace="products")),
    url(r'^reviews/', include("centerpokupok.Reviews.urls", namespace="reviews")),
    url(r'^coupons/', include("centerpokupok.Coupons.urls", namespace="coupons")),
    url(r'^profile/', include("centerpokupok.Cabinet.urls", namespace="profile")),
    url(r'^categories/', include("centerpokupok.Categories.urls", namespace="categories")),
    url(r'^company/(?P<company>[0-9]+)/', include("centerpokupok.company.urls", namespace="companies")),
    url(r'^country/(?P<country>[0-9]+)/$', centerpokupok.views.home, name="home_country"),


    url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^registration/', centerpokupok.views.registration, {'form': RegistrationForm(), 'auth_form': AuthenticationForm()}, name="register"),
    url(r'^logout/', centerpokupok.views.user_logout,  name="logout"),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)
