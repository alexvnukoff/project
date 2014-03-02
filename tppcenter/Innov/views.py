from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
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
from core.tasks import addNewProject
from django.conf import settings

def get_innov_list(request, page=1, item_id=None):
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

    current_section = "Innovation Project"
    if item_id is None:
        newsPage = _innovContent(request, page)
    else:
        newsPage = _innovDetailContent(request, item_id)






    return render_to_response("Innov/index.html", {'newsPage': newsPage, 'current_section': current_section,
                                                   'notification': notification, 'user_name': user_name },
                              context_instance=RequestContext(request))





def _innovContent(request, page=1):
    innov_projects = InnovationProject.active.get_active().order_by('-pk')


    result = func.setPaginationForItemsWithValues(innov_projects, *('NAME', 'SLUG'), page_num=7, page=page)

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



    url_paginator = "innov:paginator"
    template = loader.get_template('Innov/contentPage.html')
    context = RequestContext(request, {'innovList': innovList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator})
    return template.render(context)



def _innovDetailContent(request, item_id):
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
     return template.render(context)




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
            addNewProject(request.POST, request.FILES, user, settings.SITE_ID, branch=branch, current_company=current_company)
            return HttpResponseRedirect(reverse('innov:main'))


    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches, 'currency_slots': currency_slots})
    newsPage = template.render(context)


    return render_to_response('Innov/index.html', {'newsPage': newsPage}, context_instance=RequestContext(request))




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
            addNewProject(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch)
            return HttpResponseRedirect(reverse('innov:main'))

    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form, 'pages': pages,
                                       'currentBranch': currentBranch, 'branches': branches,
                                       'currency_slots': currency_slots})
    newsPage = template.render(context)






    return render_to_response('Innov/index.html',{'newsPage': newsPage} ,
                              context_instance=RequestContext(request))




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


