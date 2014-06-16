from appl.func import setPaginationForItemsWithValues, getPaginatorRange
from appl.models import Department, UserSites, Cabinet, Vacancy
from core.models import Item
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings

def get_structure_list(request, page=1, language=None):

    contentPage = _get_content(request, page, language)



    current_section = _("Structure")
    title = _("Structure")

    templateParams = {
    'current_section': current_section,
    'contentPage': contentPage,
    'title': title
    }

    return render_to_response("index.html", templateParams, context_instance=RequestContext(request))








def _get_content(request, page, language):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization.pk

     departaments = Department.objects.filter(c2p__parent=organization, c2p__type='hierarchy').order_by('-pk')

     if not language:
         url_paginator = 'structure:paginator'

     else:
         url_paginator ="structure_lang:paginator"
        


     attr = ('NAME',)

     result = setPaginationForItemsWithValues(departaments, *attr, page_num=2, page=page)

     content = result[0]

     cabinets = Cabinet.objects.filter(c2p__type='relation', c2p__parent__in=Vacancy.objects.filter(c2p__parent__in=content.keys())).\
         values('c2p__parent__vacancy', 'pk', 'c2p__parent__c2p__parent__organization')


     vacancy_ids = [dict.get('c2p__parent__vacancy') for dict in cabinets]
     cabinet_ids = [dict.get('pk') for dict in cabinets]

     vacansyValues = Item.getItemsAttributesValues("NAME", vacancy_ids)
     cabinet_attr = ('USER_FIRST_NAME', 'USER_LAST_NAME', 'EMAIL', 'TELEPHONE_NUMBER', 'MOBILE_NUMBER', 'IMAGE')
     cabinet_values = Item.getItemsAttributesValues(cabinet_attr, cabinet_ids)

     for cabinet in cabinets:
        if 'users' not in content[cabinet['c2p__parent__c2p__parent__organization']]:
            content[cabinet['c2p__parent__c2p__parent__organization']]['users'] = []

        curr_vacancy = {'VACANCY_NAME': vacansyValues[cabinet['c2p__parent__vacancy']]['NAME']}
        curr_cabinet = cabinet_values[cabinet['pk']]
        curr_cabinet.update(curr_vacancy)
        cur_departament = content[cabinet['c2p__parent__c2p__parent__organization']]
        cur_departament['users'].append(curr_cabinet)






     page = result[1]

     paginator_range = getPaginatorRange(page)

     templateParams = {
         'url_paginator': url_paginator,
         'content': content,
         'page': page,
         'paginator_range': paginator_range,

         'url_parameter': language if language else [],

     }

     template = loader.get_template('CompanyStructure/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered

























