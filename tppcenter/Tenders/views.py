from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task

from core.tasks import addNewsAttrubute
from django.conf import settings

def get_tenders_list(request, page=1):
    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "Tenders"

    tendersPage = _tendersContent(request, page)






    return render_to_response("Tenders/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'tendersPage': tendersPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _tendersContent(request, page=1):

    tenders = Tender.active.get_active_related().order_by('-pk')
    result = func.setPaginationForItemsWithValues(tenders, *('NAME', 'COST', 'CURRENCY'), page_num=5, page=page)
    tendersList = result[0]
    tenders_ids = [id for id in tendersList.keys()]
    organizations = Organization.objects.filter(p2c__child__in=tenders_ids).values('c2p__parent__country', 'pk', 'p2c__child__tender')
    organization_dict = {}
    country_dict = {}
    for organization in organizations:
        organization_dict[organization['p2c__child__tender']] = organization['pk']
        country_dict[organization['p2c__child__tender']] = organization['c2p__parent__country']

    countriesList = Item.getItemsAttributesValues(('NAME', 'FLAG'), country_dict.values())
    organizationsList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organization_dict.values())


    for id, tender in tendersList.items():
        toUpdate = {'ORG_NAME': organizationsList[organization_dict[id]].get('NAME', [""]),
                    'ORG_FLAG': organizationsList[organization_dict[id]].get('FLAG', [""]),
                    'ORG_ID': organization_dict[id],
                    'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [""]),
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [""]),
                    'COUNTRY_ID': country_dict[id]}
        tender.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "tenders:paginator"
    template = loader.get_template('Tenders/contentPage.html')
    context = RequestContext(request, {'tendersList': tendersList, 'page': page,
                                       'paginator_range': paginator_range, 'url_paginator': url_paginator})
    return template.render(context)






def addNews(request):
    form = None

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        addAttr={'NAME': 'True'}
        form = ItemForm('News', values=values, addAttr=addAttr)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, addAttr)
            return HttpResponseRedirect(reverse('news:main'))





    return render_to_response('News/addForm.html', {'form': form}, context_instance=RequestContext(request))



def updateNew(request, item_id):

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]
    addAttr = {'NAME': 'True'}
    form = ItemForm('News', id=item_id, addAttr=addAttr)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")

        form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, addAttr , item_id)
            return HttpResponseRedirect(reverse('news:main'))







    return render_to_response('News/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form}, context_instance=RequestContext(request))



