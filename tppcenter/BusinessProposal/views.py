from django.shortcuts import render
from django.shortcuts import render_to_response, HttpResponse
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
import json
from haystack.query import SearchQuerySet, SQ
from core.tasks import addBusinessPRoposal
from django.conf import settings

def get_proposals_list(request, page=1):

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    proposalsPage = _proposalsContent(request, page)

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
        current_section = "Business Proposal"

        templateParams = {
            'user_name': user_name,
            'current_section': current_section,
            'proposalsPage': proposalsPage,
            'notification': notification,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', '')
        }

        return render_to_response("BusinessProposal/index.html", templateParams, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': proposalsPage}))


def _proposalsContent(request, page=1):

    filters, searchFilter = func.filterLive(request)

    #proposal = BusinessProposal.active.get_active_related().order_by('-pk')
    sqs = SearchQuerySet().models(BusinessProposal)

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

    #result = func.setPaginationForItemsWithValues(proposal, *('NAME',), page_num=5, page=page)
    result = func.setPaginationForSearchWithValues(proposal, *('NAME',), page_num=5, page=page)



    proposalList = result[0]
    proposal_ids = [id for id in proposalList.keys()]
    countries = Country.objects.filter(p2c__child__p2c__child__in=proposal_ids).values('p2c__child__p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

    companies = Company.objects.filter(p2c__child__in=proposal_ids).values('p2c__child', 'pk')
    companies_ids = [company['pk'] for company in companies]
    companiesList = Item.getItemsAttributesValues(("NAME"), companies_ids)
    company_dict = {}
    for company in companies:
        company_dict[company['p2c__child']] = company['pk']


    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, proposal in proposalList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0),
                    'COMPANY_NAME': companiesList[company_dict[id]].get('NAME', 0 ) if company_dict.get(id, 0) else [0],
                    'COMPANY_ID': company_dict.get(id, 0)}
        proposal.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "proposals:paginator"
    template = loader.get_template('BusinessProposal/contentPage.html')

    templateParams = {
        'proposalList': proposalList,
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






def addBusinessProposal(request):
    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)




    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
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
            addBusinessPRoposal(request.POST, request.FILES, user, settings.SITE_ID, branch=branch)
            return HttpResponseRedirect(reverse('proposal:main'))





    return render_to_response('BusinessProposal/addForm.html', {'form': form, 'branches': branches},
                              context_instance=RequestContext(request))



def updateBusinessProposal(request, item_id):

    if request.method != 'POST':
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


        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(parent_id=item_id)
        photos = ""

        if gallery.queryset:
            photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

        form = ItemForm('BusinessProposal', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
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
            addBusinessPRoposal(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch)
            return HttpResponseRedirect(reverse('proposal:main'))







    return render_to_response('BusinessProposal/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form,
                                                                'pages': pages, 'currentBranch': currentBranch,
                                                                'branches': branches},
                              context_instance=RequestContext(request))



