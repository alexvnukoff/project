from django.shortcuts import render
from django.shortcuts import render_to_response, HttpResponse, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.utils.translation import ugettext as _
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
import json
from haystack.query import SearchQuerySet, SQ
from core.tasks import addBusinessPRoposal
from django.conf import settings

from django.utils import timezone

def get_proposals_list(request, page=1, item_id=None,  my=None, slug=None):
    #if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #    slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      #   return HttpResponseRedirect(reverse('proposal:detail',  args=[slug]))

    current_company = request.session.get('current_company', False)
    filterAdv = []

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    cabinetValues = func.getB2BcabinetValues(request)

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    if not item_id:
        try:
            proposalsPage, filterAdv = _proposalsContent(request, page, my)
        except ObjectDoesNotExist:

            proposalsPage = func.emptyCompany()



    else:
        proposalsPage, filterAdv = _proposalDetailContent(request, item_id, current_company)

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    tops = func.getTops(request, filter=filterAdv)


    if not request.is_ajax():
        user = request.user




        current_section = _("Business Proposal")


        templateParams = {

            'current_section': current_section,
            'proposalsPage': proposalsPage,

            'current_company': current_company,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'cabinetValues': cabinetValues,
            'addNew': reverse('proposal:add'),
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return render_to_response("BusinessProposal/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops,
            'styles': styles,
            'scripts': scripts,
            'content': proposalsPage
        }

        return HttpResponse(json.dumps(serialize))


def _proposalsContent(request, page=1, my=None):

    filterAdv = []

    if not my:
        filters, searchFilter, filterAdv = func.filterLive(request)

        #proposal = BusinessProposal.active.get_active_related().order_by('-pk')
        sqs = SearchQuerySet().models(BusinessProposal).filter(SQ(obj_end_date__gt=timezone.now())| SQ(obj_end_date__exact=datetime(1 , 1, 1)),
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

        proposal = sqs.order_by(*order)
        url_paginator = "proposal:paginator"
        params = {
            'filters': filters,
            'sortField1': sortField1,
                    'sortField2': sortField2,
                    'order1': order1,
                    'order2': order2
        }

    else:
        current_organization = request.session.get('current_company', False)

        if current_organization:
             proposal = SearchQuerySet().models(BusinessProposal).\
                 filter(SQ(tpp=current_organization) | SQ(company=current_organization))

             url_paginator = "proposal:my_main_paginator"
             params = {}
        else:
             raise ObjectDoesNotExist('you need check company')
    #result = func.setPaginationForItemsWithValues(proposal, *('NAME',), page_num=5, page=page)
    result = func.setPaginationForSearchWithValues(proposal, *('NAME', 'SLUG'), page_num=5, page=page)



    proposalList = result[0]
    proposal_ids = [id for id in proposalList.keys()]

    func.addDictinoryWithCountryAndOrganization(proposal_ids, proposalList)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)




    template = loader.get_template('BusinessProposal/contentPage.html')

    templateParams = {
        'proposalList': proposalList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,

    }
    templateParams.update(params)

    context = RequestContext(request, templateParams)
    return template.render(context), filterAdv



def _proposalDetailContent(request, item_id, current_company):

     filterAdv = func.getDeatailAdv(item_id)

     proposal = get_object_or_404(BusinessProposal, pk=item_id)
     proposalValues = proposal.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SLUG'))


     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)


     func.addToItemDictinoryWithCountryAndOrganization(proposal.id, proposalValues)

     template = loader.get_template('BusinessProposal/detailContent.html')

     context = RequestContext(request, {'proposalValues': proposalValues, 'photos': photos,
                                        'additionalPages': additionalPages})
     return template.render(context), filterAdv


@login_required(login_url='/login/')
def proposalForm(request, action, item_id=None):
    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    cabinetValues = func.getB2BcabinetValues(request)


    user = request.user



    current_section = _("Business Proposal")

    if action == 'add':
        proposalsPage = addBusinessProposal(request)
    else:
        proposalsPage = updateBusinessProposal(request, item_id)

    if isinstance(proposalsPage, HttpResponseRedirect) or isinstance(proposalsPage, HttpResponse):
        return proposalsPage

    return render_to_response('BusinessProposal/index.html', {'proposalsPage': proposalsPage, 'current_company':current_company,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))




def addBusinessProposal(request):
    current_company = request.session.get('current_company', False)
    if not request.session.get('current_company', False):

         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)
    if 'add_businessproposal' not in perm_list:

         return func.permissionDenied()






    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)




    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")



        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['KEYWORD'] = request.POST.get('KEYWORD', "")
        values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
        values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
        values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")
        branch = request.POST.get('BRANCH', "")





        form = ItemForm('BusinessProposal', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addBusinessPRoposal.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch,
                                current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('proposal:main'))

    template = loader.get_template('BusinessProposal/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches})
    proposalsPage = template.render(context)

    return  proposalsPage









def updateBusinessProposal(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_businessproposal' not in perm_list:
        return func.permissionDenied()


    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)
    try:
        currentBranch = Branch.objects.get(p2c__child=item_id)
    except Exception:
        currentBranch = ""

    if request.method != 'POST':



        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
        pages = pages.queryset


        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(parent_id=item_id)
        photos = ""

        if gallery.queryset:
            photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

        form = ItemForm('BusinessProposal', id=item_id)

    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")



        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")

        values['KEYWORD'] = request.POST.get('KEYWORD', "")
        values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
        values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
        values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")
        branch = request.POST.get('BRANCH', "")





        form = ItemForm('BusinessProposal', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addBusinessPRoposal.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch,
                                lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('proposal:main'))



    template = loader.get_template('BusinessProposal/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form,
                                                                'pages': pages, 'currentBranch': currentBranch,
                                                                'branches': branches})
    proposalsPage = template.render(context)




    return proposalsPage



