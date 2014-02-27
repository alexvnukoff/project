from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task

from core.tasks import addNewExhibition

from haystack.query import SQ, SearchQuerySet
import json

from django.conf import settings

def get_exhibitions_list(request, page=1):

    scripts = []
    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']

    exhibitionPage = _exhibitionsContent(request, page)

    if not request.is_ajax():
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
        current_section = "Exhibitions"



        templateParams = {
            'user_name': user_name,
            'current_section': current_section,
            'exhibitionPage': exhibitionPage,
            'notification': notification,
            'search': request.GET.get('q', '')
        }

        return render_to_response("Exhibitions/index.html", templateParams, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': exhibitionPage}))

def _exhibitionsContent(request, page=1):

    filters, searchFilter = func.filterLive(request)

    sqs = SearchQuerySet().models(Exhibition)

    if len(searchFilter) > 0:
        sqs = sqs.filter(**searchFilter)

    q = request.GET.get('q', '')

    if q != '':
        sqs = sqs.filter(SQ(title=q) | SQ(text=q))

    sortFields = {
        'date': 'id',
        'name': 'title'
    }

    order = []

    sortField1 = request.GET.get('sortField1', 'date')
    sortField2 = request.GET.get('sortField2', None)
    order1 = request.GET.get('order1', 'desc')
    order2 = request.GET.get('order2', None)

    if sortField1 and sortField1 in sortFields:
        if order1 == 'desc':
            order.append('-' + sortFields[sortField1])
        else:
            order.append(sortFields[sortField1])
    else:
        order.append('-id')

    if sortField2 and sortField2 in sortFields:
        if order2 == 'desc':
            order.append('-' + sortFields[sortField2])
        else:
            order.append(sortFields[sortField2])

    exhibitions = sqs.order_by(*order)

    result = func.setPaginationForSearchWithValues(exhibitions, *('NAME', 'CITY', 'COUNTRY', 'EVENT_DATE'), page_num=5, page=page)

    #exhibitions = Exhibition.active.get_active_related().order_by('-pk')
    #result = func.setPaginationForItemsWithValues(exhibitions, *('NAME', 'CITY', 'COUNTRY', 'EVENT_DATE'), page_num=5, page=page)


    exhibitionsList = result[0]
    exhibitions_ids = [id for id in exhibitionsList.keys()]

    func.addDictinoryWithCountryAndOrganization(exhibitions_ids, exhibitionsList)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "exhibitions:paginator"
    template = loader.get_template('Exhibitions/contentPage.html')

    templateParams = {
        'exhibitionsList': exhibitionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2
    }

    context = RequestContext(request, templateParams)

    return template.render(context)







def addExhibition(request):
    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Exhibition', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            addNewExhibition(request.POST, request.FILES, user, settings.SITE_ID, branch=branch)
            return HttpResponseRedirect(reverse('exhibitions:main'))

    return render_to_response('Exhibitions/addForm.html', {'form': form, 'branches': branches},
                              context_instance=RequestContext(request))



def updateExhibition(request, item_id):
    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)
    try:
        currentBranch = Branch.objects.get(p2c__child=item_id)
    except Exception:
        currentBranch = ""

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]




    form = ItemForm('Exhibition', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)


        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Exhibition', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewExhibition(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch)
            return HttpResponseRedirect(reverse('exhibitions:main'))







    return render_to_response('Exhibitions/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form,
                                                           'pages': pages, 'currentBranch': currentBranch,
                                                           'branches': branches},
                              context_instance=RequestContext(request))




def _getValues(request):

    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['CITY'] = request.POST.get('CITY', "")
    values['START_EVENT_DATE'] = request.POST.get('START_EVENT_DATE', "")
    values['END_EVENT_DATE'] = request.POST.get('END_EVENT_DATE', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['ROUTE_DESCRIPTION'] = request.POST.get('ROUTE_DESCRIPTION', "")
    values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
    values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
    values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")




    return values



