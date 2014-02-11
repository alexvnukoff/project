from django.conf.urls import patterns, include, url
import appl.views

import tppcenter.views
import tppcenter.News.urls


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.views.home),
     url(r'^news/', include(tppcenter.News.urls, namespace='news')),
    # url(r'^blog/', include('blog.urls')),

    url(r'^test/', tppcenter.views.test),
    url(r'^test2/', tppcenter.views.test2),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^items/$', tppcenter.views.set_items_list),
    url(r'^items/([a-zA-Z]+)/$', tppcenter.views.set_item_list),
    url(r'^items/([a-zA-Z]+)/create/$', tppcenter.views.get_item_form),
    url(r'^items/([a-zA-Z]+)/update/([0-9]+)/$', tppcenter.views.update_item),
    url(r'^items/([a-zA-Z]+)/showlist/([0-9]+)/$', tppcenter.views.showlist),

)