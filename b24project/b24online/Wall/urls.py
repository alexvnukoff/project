from django.conf.urls import url

import b24online.Wall.views

urlpatterns = [url(r'^$', b24online.Wall.views.get_wall_list, name='main')]
