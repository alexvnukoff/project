from django.conf.urls import url

from b24online.Wall.views import get_wall_list

urlpatterns = [url(r'^$', get_wall_list, name='main')]
