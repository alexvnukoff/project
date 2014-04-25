from urllib.parse import urlencode
from django.http.response import HttpResponsePermanentRedirect
from haystack.backends import SQ
from appl import func
from appl.func import getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import News, Organization, NewsCategories, Gallery, Country, UserSites
from core.models import Item, Group
from datetime import datetime
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseGone
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext as _
from django.utils.timezone import now
import tppcenter
from tppcenter.forms import ItemForm,BasePhotoGallery
from pytz import timezone
import pytz
import json
import requests
from django.contrib.sites.models import Site


from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request):

   contentPage = _get_content(request)

   current_section = _("Contacts")
   title = _("Contacts")

   templateParams = {
       'current_section': current_section,
       'contentPage': contentPage,
       'title': title
   }



   return render_to_response("index.html", templateParams, context_instance=RequestContext(request))








def _get_content(request):

     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization

     attr = ('NAME', 'ADDRESS', 'TELEPHONE_NUMBER', 'SLUG', 'POSITION')


     organizationValues = organization.getAttributeValues(*attr)





     templateParams = {
         'organizationValues': organizationValues,

     }


     template = loader.get_template('Contact/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered






















