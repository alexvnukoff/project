from django.conf.urls import patterns, include, url

import usersites.views
import usersites.News.urls
import usersites.Proposals.urls
import usersites.Products.urls
import usersites.Contact.urls
import usersites.CompanyStructure.urls



from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.views.get_wall),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/', include(usersites.News.urls, namespace='news')),
    url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
    url(r'^products/', include(usersites.Products.urls, namespace='products')),
    url(r'^contact/', include(usersites.Contact.urls, namespace='contact')),
    url(r'^structure/', include(usersites.CompanyStructure.urls, namespace='structure')),
    url(r'^page-(?P<page_id>[0-9]+)/$', usersites.views.get_wall, name='additionalPage'),
)
