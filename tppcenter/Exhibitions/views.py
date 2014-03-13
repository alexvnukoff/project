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
from django.utils import timezone
from datetime import datetime

from core.tasks import addNewExhibition

from haystack.query import SQ, SearchQuerySet
import json

from django.conf import settings

def get_exhibitions_list(request, page=1, item_id=None, my=None, slug=None):
    #if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #  slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      # return HttpResponseRedirect(reverse('exhibitions:detail',  args=[slug]))


    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    scripts = []
    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']

    if not item_id:
        try:
            exhibitionPage = _exhibitionsContent(request, page, my)
        except ObjectDoesNotExist:
            exhibitionPage = func.emptyCompany()
    else:
        exhibitionPage = _exhibitionsDetailContent(request, item_id)

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')
    tops = func.getTops(request)

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
        current_section = _("Exhibitions")



        templateParams = {
            'user_name': user_name,
            'current_section': current_section,
            'exhibitionPage': exhibitionPage,
            'current_company': current_company,
            'notification': notification,
            'search': request.GET.get('q', ''),
            'styles': styles,
            'scripts': scripts,
            'addNew': reverse('exhibitions:add'),
            'cabinetValues': cabinetValues,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return render_to_response("Exhibitions/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops,
            'styles': styles,
            'scripts': scripts,
            'content': exhibitionPage
        }

        return HttpResponse(json.dumps(serialize))

def _exhibitionsContent(request, page=1, my=None):


    if not my:
        filters, searchFilter = func.filterLive(request)

        sqs = SearchQuerySet().models(Exhibition).filter(SQ(obj_end_date__gt=timezone.now())| SQ(obj_end_date__exact=datetime(1 , 1, 1)),
                                                               obj_start_date__lt=timezone.now())

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
        url_paginator = "exhibitions:paginator"
        params = {
            'filters': filters,
            'sortField1': sortField1,
                  'sortField2': sortField2,
                  'order1': order1,
                  'order2': order2}
    else:

         current_organization = request.session.get('current_company', False)

         if current_organization:
             exhibitions = SearchQuerySet().models(Exhibition).\
                 filter(SQ(tpp=current_organization)|SQ(company=current_organization))

             url_paginator = "exhibitions:my_main_paginator"
             params = {}
         else:
             raise ObjectDoesNotExist('you need check company')

    result = func.setPaginationForSearchWithValues(exhibitions, *('NAME', 'CITY', 'COUNTRY', 'START_EVENT_DATE',
                                                                  'END_EVENT_DATE', 'SLUG'),
                                                   page_num=5, page=page)

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

    }
    templateParams.update(params)

    context = RequestContext(request, templateParams)

    return template.render(context)



def _exhibitionsDetailContent(request, item_id):


     exhibition = get_object_or_404(Exhibition, pk=item_id)
     exhibitionlValues = exhibition.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'START_EVENT_DATE', 'END_EVENT_DATE',
                                                         'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'CITY',
                                                         'ROUTE_DESCRIPTION', 'POSITION'))

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)



     func.addToItemDictinoryWithCountryAndOrganization(exhibition.id, exhibitionlValues)

     template = loader.get_template('Exhibitions/detailContent.html')

     context = RequestContext(request, {'exhibitionlValues': exhibitionlValues, 'photos': photos,
                                        'additionalPages': additionalPages})
     return template.render(context)


@login_required(login_url='/login/')
def exhibitionForm(request, action, item_id=None):
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

    current_section = _("Exhibitions")

    if action == 'add':
        exhibitionPage = addExhibition(request)
    else:
        exhibitionPage = updateExhibition(request, item_id)

    if isinstance(exhibitionPage, HttpResponseRedirect) or isinstance(exhibitionPage, HttpResponse):
        return exhibitionPage

    return render_to_response('Exhibitions/index.html', {'exhibitionPage': exhibitionPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))



def addExhibition(request):
    form = None
    current_company = request.session.get('current_company', False)
    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)



    perm_list = item.getItemInstPermList(request.user)
    if 'add_exhibition' not in perm_list:
         return func.permissionDenied()



    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    if request.POST:

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
            func.notify("item_creating", 'notification', user=request.user)
            addNewExhibition.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('exhibitions:main'))

    template = loader.get_template('Exhibitions/addForm.html')
    context = RequestContext(request,  {'form': form, 'branches': branches})
    exhibitionPage = template.render(context)

    return exhibitionPage



def updateExhibition(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_exhibition' not in perm_list:
        return func.permissionDenied()

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
            func.notify("item_creating", 'notification', user=request.user)
            addNewExhibition.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('exhibitions:main'))


    template = loader.get_template('Exhibitions/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form,
                                                           'pages': pages, 'currentBranch': currentBranch,
                                                           'branches': branches})
    exhibitionPage = template.render(context)

    return exhibitionPage




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
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")




    return values



