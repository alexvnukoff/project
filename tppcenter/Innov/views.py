
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.forms.models import modelformset_factory
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from core.tasks import addNewProject
from django.conf import settings
from haystack.query import SQ, SearchQuerySet
import json


def get_innov_list(request, page=1, item_id=None, my=None):

    filterAdv = []
    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    cabinetValues = func.getB2BcabinetValues(request)

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    if item_id is None:
        try:
            newsPage, filterAdv = _innovContent(request, page, my)
        except ObjectDoesNotExist:
            return render_to_response("permissionDen.html")
    else:
        newsPage, filterAdv = _innovDetailContent(request, item_id)



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

        current_section = _("Innovation Project")

        templateParams = {
            'newsPage': newsPage,
            'current_section': current_section,
            'notification': notification,
            'user_name': user_name,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'current_company': current_company,
            'addNew': reverse('innov:add'),
            'cabinetValues': cabinetValues
        }

        return render_to_response("Innov/index.html", templateParams, context_instance=RequestContext(request))

    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': newsPage}))



def _innovContent(request, page=1, my=None):

    filterAdv = []

    if not my:
        filters, searchFilter, filterAdv = func.filterLive(request)

        #companies = Company.active.get_active().order_by('-pk')
        sqs = SearchQuerySet().models(InnovationProject)

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


        innov_projects = sqs.order_by(*order)
        url_paginator = "innov:paginator"
        params = {'filters': filters,
                  'sortField1': sortField1,
                  'sortField2': sortField2,
                  'order1': order1,
                  'order2': order2
        }
    else:
        current_organization = request.session.get('current_company', False)

        if current_organization:
             innov_projects = SearchQuerySet().models(InnovationProject).\
                 filter(SQ(tpp=current_organization) | SQ(company=current_organization))

             url_paginator = "innov:my_main_paginator"
             params = {}
        else: #TODO Jenya do block try
             raise ObjectDoesNotExist('you need check company')

    result = func.setPaginationForSearchWithValues(innov_projects, *('NAME', 'SLUG'), page_num=7, page=page)
    #innov_projects = InnovationProject.active.get_active().order_by('-pk')


    #result = func.setPaginationForItemsWithValues(innov_projects, *('NAME', 'SLUG'), page_num=7, page=page)

    innovList = result[0]
    innov_ids = [id for id in innovList.keys()]


    branches = Branch.objects.filter(p2c__child__in=innov_ids).values('p2c__child', 'pk')
    branches_ids = [branch['pk'] for branch in branches]
    branchesList = Item.getItemsAttributesValues(("NAME"), branches_ids)

    branches_dict = {}
    for branch in branches:
        branches_dict[branch['p2c__child']] = branch['pk']

    func.addDictinoryWithCountryAndOrganization(innov_ids, innovList)

    for id, innov in innovList.items():

        toUpdate = {'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0 ) if branches_dict.get(id, 0) else [0],
                    'BRANCH_ID': branches_dict.get(id, 0)}
        innov.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)




    template = loader.get_template('Innov/contentPage.html')

    templateParams = {
        'innovList': innovList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,

    }
    templateParams.update(params)

    context = RequestContext(request, templateParams)
    return template.render(context), filterAdv


def _innovDetailContent(request, item_id):

     filterAdv = func.getDeatailAdv(item_id)

     innov = get_object_or_404(InnovationProject, pk=item_id)
     innovValues = innov.getAttributeValues(*('NAME', 'PRODUCT_NAME', 'COST', 'REALESE_DATE', 'BUSINESS_PLAN',
                                                 'CURRENCY', 'DOCUMENT_1', 'DETAIL_TEXT'))

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     branch = Branch.objects.get(p2c__child=item_id)
     branchValues = branch.getAttributeValues('NAME')
     innovValues.update({'BRANCH_NAME': branchValues, 'BRANCH_ID': branch.id})

     func.addToItemDictinoryWithCountryAndOrganization(innov.id, innovValues)

     template = loader.get_template('Innov/detailContent.html')

     context = RequestContext(request, {'innovValues': innovValues, 'photos': photos,
                                        'additionalPages': additionalPages})

     return template.render(context), filterAdv


def innovForm(request, action, item_id=None):
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

    current_section = _("Innovation Project")

    if action == 'add':
        newsPage = addProject(request)
    else:
        newsPage = updateProject(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    return render_to_response('Innov/index.html', {'newsPage': newsPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))

def addProject(request):
    current_company = request.session.get('current_company', False)


    if not request.session.get('current_company', False):
         return render_to_response("permissionDen.html")

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)



    if 'add_innovationproject' not in perm_list:
         return render_to_response("permissionDenied.html")


    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            addNewProject(request.POST, request.FILES, user, settings.SITE_ID, branch=branch, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('innov:main'))


    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches, 'currency_slots': currency_slots})
    newsPage = template.render(context)


    return newsPage



def updateProject(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_innovationproject' not in perm_list:
        return render_to_response("permissionDenied.html")

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

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    form = ItemForm('InnovationProject', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewProject(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('innov:main'))

    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form, 'pages': pages,
                                       'currentBranch': currentBranch, 'branches': branches,
                                       'currency_slots': currency_slots})
    newsPage = template.render(context)






    return newsPage




def _getValues(request):

    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['PRODUCT_NAME'] = request.POST.get('PRODUCT_NAME', "")
    values['COST'] = request.POST.get('COST', "")
    values['CURRENCY'] = request.POST.get('CURRENCY', "")
    values['TARGET_AUDIENCE'] = request.POST.get('TARGET_AUDIENCE', "")
    values['REALESE_DATE'] = request.POST.get('REALESE_DATE', "")
    values['SITE_NAME'] = request.POST.get('SITE_NAME', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['BUSINESS_PLAN'] = request.POST.get('BUSINESS_PLAN', "")
    values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")





    return values


