from django.conf.urls import url, include

import b24online.api.v1.urls

urlpatterns = [
    url(r'^v1/', include(b24online.api.v1.urls), name='v1'),
]
