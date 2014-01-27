from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News, Category, Country, Product, Cabinet
from core.models import Value, Item, Attribute, Dictionary, User
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


@login_required(login_url=("/registration/"))
def get_profile(request):
    user = request.user
    try:
        cabinet = Cabinet.objects.get(user=user.pk)
    except ObjectDoesNotExist:
        cabinet = Cabinet(user=user, create_user=user)
        cabinet.save()

    return render_to_response("Cabinet/index.html")











