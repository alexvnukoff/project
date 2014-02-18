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

def get_proposals_list(request, page=1):
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

    proposalsPage = _proposalsContent(request, page)






    return render_to_response("BusinessProposal/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'proposalsPage': proposalsPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _proposalsContent(request, page=1):
    proposal = BusinessProposal.active.get_active_related().order_by('-pk')


    result = func.setPaginationForItemsWithValues(proposal, *('NAME',),
                                                  page_num=5, page=page)

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
    context = RequestContext(request, {'proposalList': proposalList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator})
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
    addAttr = {'NAME': 'True'}
    if request.method != 'POST':
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(parent_id=item_id)
        photos = ""

        if gallery.queryset:
            photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

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
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, addAttr, item_id)
            return HttpResponseRedirect(reverse('news:main'))







    return render_to_response('News/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form}, context_instance=RequestContext(request))



