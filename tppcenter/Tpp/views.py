from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task

from core.tasks import addNewTpp
from django.conf import settings

def get_tpp_list(request, page=1, item_id=None):
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
    current_section = "Organizations"

    if item_id is None:
        tppPage = _tppContent(request, page)
    else:
        tppPage = _tppDetailContent(request, item_id)






    return render_to_response("Tpp/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'tppPage': tppPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _tppContent(request, page=1):
    tpp = Tpp.active.get_active().order_by('-pk')


    result = func.setPaginationForItemsWithValues(tpp, *('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME',
                                                               'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'FLAG',
                                                               'SLUG'),
                                                  page_num=5, page=page)

    tppList = result[0]
    tpp_ids = [id for id in tppList.keys()]
    countries = Country.objects.filter(p2c__child__in=tpp_ids).values('p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child']] = country['pk']

    for id, tpp in tppList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        tpp.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "tpp:paginator"
    template = loader.get_template('Tpp/contentPage.html')
    context = RequestContext(request, {'tppList': tppList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator})
    return template.render(context)



def _tppDetailContent(request, item_id):

    tpp = get_object_or_404(Tpp, pk=item_id)
    tppValues = tpp.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'FLAG', 'IMAGE'))


    if not tppValues.get('FLAG', False):
       country = Country.objects.get(p2c__child=tpp).getAttributeValues(*('FLAG', 'NAME'))
    else:
       country = ""















    template = loader.get_template('Tpp/detailContent.html')
    context = RequestContext(request, {'tppValues': tppValues, 'country': country})
    return template.render(context)



def addTpp(request):
    form = None

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tpp', values=values)
        form.clean()

        if form.is_valid() and pages.is_valid():
            addNewTpp(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('tpp:main'))





    return render_to_response('Tpp/addForm.html', {'form': form},
                              context_instance=RequestContext(request))



def updateTpp(request, item_id):


    if request.method != 'POST':
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
        pages = pages.queryset

        form = ItemForm('Tpp', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")


        values = _getValues(request)


        form = ItemForm('Tpp', values=values, id=item_id)
        form.clean()

        if form.is_valid() and pages.is_valid() :
            addNewTpp(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('tpp:main'))







    return render_to_response('Tpp/addForm.html', {'form': form, 'pages': pages},
                              context_instance=RequestContext(request))



def _getValues(request):
    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['IMAGE'] = request.FILES.get('IMAGE', "")
    values['FLAG'] = request.FILES.get('FLAG', "")
    values['ADDRESS'] = request.POST.get('ADDRESS', "")
    values['SITE_NAME'] = request.POST.get('SITE_NAME', "")
    values['TELEPHONE_NUMBER'] = request.POST.get('TELEPHONE_NUMBER', "")
    values['FAX'] = request.POST.get('FAX', "")
    values['INN'] = request.POST.get('INN', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['SLOGAN'] = request.POST.get('SLOGAN', "")
    values['EMAIL'] = request.POST.get('EMAIL', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DIRECTOR'] = request.POST.get('DIRECTOR', "")
    values['KPP'] = request.POST.get('KPP', "")
    values['OKPO'] = request.POST.get('OKPO', "")
    values['OKATO'] = request.POST.get('OKATO', "")
    values['OKVED'] = request.POST.get('OKVED', "")
    values['ACCOUNTANT'] = request.POST.get('ACCOUNTANT', "")
    values['ACCOUNT_NUMBER'] = request.POST.get('ACCOUNT_NUMBER', "")
    values['BANK_DETAILS'] = request.POST.get('BANK_DETAILS', "")

    return values


