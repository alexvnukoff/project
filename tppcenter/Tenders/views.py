from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from core.tasks import addNewTender
from django.conf import settings
from haystack.query import SQ, SearchQuerySet
import json

def get_tenders_list(request, page=1, item_id=None, my=None, slug=None):

    if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
         slug = Value.objects.get(item=item_id, attr__title='SLUG').title
         return HttpResponseRedirect(reverse('tenders:detail',  args=[slug]))

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    if item_id is None:
        try:
            tendersPage = _tendersContent(request, page, my)
        except ObjectDoesNotExist:
            return render_to_response("permissionDen.html")
    else:
        tendersPage = _tenderDetailContent(request, item_id)

    if not request.is_ajax():
        user = request.user
        if user.is_authenticated():
            notification = Notification.objects.filter(user=request.user, read=False).count()
            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = _("Tenders")

        templateParams =  {
            'user_name': user_name,
            'current_section': current_section,
            'tendersPage': tendersPage,
            'notification': notification,
            'current_company': current_company,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'addNew': reverse('tenders:add'),
            'cabinetValues': cabinetValues
        }

        return render_to_response("Tenders/index.html", templateParams, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': tendersPage }))


def _tendersContent(request, page=1, my=None):



    #tenders = Tender.active.get_active().order_by('-pk')
    if not my:
        filters, searchFilter = func.filterLive(request)

        #companies = Company.active.get_active().order_by('-pk')
        sqs = SearchQuerySet().models(Tender)

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


        tenders = sqs.order_by(*order)
        url_paginator = "tenders:paginator"
        params = {'filters': filters,
                  'sortField1': sortField1,
                  'sortField2': sortField2,
                  'order1': order1,
                  'order2': order2
        }
    else:
        current_organization = request.session.get('current_company', False)

        if current_organization:
             tenders = SearchQuerySet().models(Tender).\
                 filter(SQ(tpp=current_organization) | SQ(company=current_organization))

             url_paginator = "tenders:my_main_paginator"
             params = {}
        else:
             raise ObjectDoesNotExist('you need check company')


    result = func.setPaginationForSearchWithValues(tenders, *('NAME', 'COST', 'CURRENCY', 'SLUG'), page_num=5, page=page)

    tendersList = result[0]
    tenders_ids = [id for id in tendersList.keys()]
    func.addDictinoryWithCountryAndOrganization(tenders_ids, tendersList)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    template = loader.get_template('Tenders/contentPage.html')

    templateParams = {
        'tendersList': tendersList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,

    }

    context = RequestContext(request, templateParams)

    return template.render(context)


def _tenderDetailContent(request, item_id):



     tender = get_object_or_404(Tender, pk=item_id)
     tenderValues = tender.getAttributeValues(*('NAME', 'COST', 'CURRENCY', 'START_EVENT_DATE', 'END_EVENT_DATE',
                                                 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'DETAIL_TEXT'))

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     func.addToItemDictinoryWithCountryAndOrganization(tender.id, tenderValues)

     template = loader.get_template('Tenders/detailContent.html')

     context = RequestContext(request, {'tenderValues': tenderValues, 'photos': photos,
                                        'additionalPages': additionalPages})
     return template.render(context)

@login_required(login_url='/login/')
def tenderForm(request, action, item_id=None):
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    user = request.user

    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()

        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name

    else:

        user_name = None
        notification = None

    current_section = _("Tenders")

    if action == 'add':
        tendersPage = addTender(request)
    else:
        tendersPage = updateTender(request, item_id)

    if isinstance(tendersPage, HttpResponseRedirect) or isinstance(tendersPage, HttpResponse):
        return tendersPage

    return render_to_response('Tenders/index.html', {'tendersPage': tendersPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))

def addTender(request):
    current_company = request.session.get('current_company', False)
    if not request.session.get('current_company', False):
         return render_to_response("permissionDen.html")

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)



    if 'add_tender' not in perm_list:
         return render_to_response("permissionDenied.html")



    form = None
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()



    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tender', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTender.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('tenders:main'))

    template = loader.get_template('Tenders/addForm.html')
    context = RequestContext(request, {'form': form, 'currency_slots': currency_slots})
    tendersPage = template.render(context)

    return tendersPage


def updateTender(request, item_id):

    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_tender' not in perm_list:
        return render_to_response("permissionDenied.html")

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()


    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]




    form = ItemForm('Tender', id=item_id)

    if request.POST:


        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tender', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTender.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('tenders:main'))




    template = loader.get_template('Tenders/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form,
                                                        'currency_slots': currency_slots, 'pages': pages})
    tendersPage = template.render(context)


    return tendersPage


def _getValues(request):

    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['COST'] = request.POST.get('COST', "")
    values['CURRENCY'] = request.POST.get('CURRENCY', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['START_EVENT_DATE'] = request.POST.get('START_EVENT_DATE', "")
    values['END_EVENT_DATE'] = request.POST.get('END_EVENT_DATE', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
    values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
    values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")




    return values


