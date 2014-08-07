from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import get_language
from appl import func
from appl.func import getActiveSQS
from appl.models import Resume, Country, Requirement
from core.models import Item


@csrf_protect
def home(request):

    cache_name = 'job_home_page_%s' % get_language()
    cached = cache.get(cache_name)

    if not cached:

        resumes = getActiveSQS().models(Resume).order_by('-obj_create_date')[:5]

        resumeCountryDict = {}

        for resume in resumes:
            resumeCountryDict[resume.id] = resume.country

        ids = list(resumeCountryDict.keys()) + list(resumeCountryDict.values())

        ResumeWithAttr = Item.getItemsAttributesValues(('NAME', 'SLUG', 'FLAG'), ids)

        resumes = {}
        countries = {}

        for id, attrs in ResumeWithAttr.items():

            if id in resumeCountryDict:

                if id not in resumes[id]:
                    resumes[id] = {}

                resumes[id]['NAME'] = attrs.get('NAME', [''])[0]
                resumes[id]['SLUG'] = attrs.get('SLUG', [''])[0]
            else:

                if id not in countries[id]:
                    countries[id] = {}

                countries[id]['COUNTRY_NAME'] = attrs.get('NAME', [''])[0]
                countries[id]['COUNTRY_FLAG'] = attrs.get('FLAG', [''])[0]


        vacancys = getActiveSQS().models(Requirement).order_by('-obj_create_date')[:5]

        vacancy_id = []

        for vacancy in vacancys:
            vacancy_id.append(vacancy)

        vacancys = Item.getItemsAttributesValues(('NAME', 'SLUG'), vacancy_id)
        vacancys = func.addDictinoryWithCountryToVacancy(vacancy_id, vacancys)


        templateParams = {
            'resumes': resumes,
            'vacancys': vacancys
        }



        cache.set(cache_name, templateParams)
    else:
        templateParams = cache.get(cache_name)

    template = loader.get_template('job_index.html')
    context = RequestContext(request, templateParams)
    rendered = template.render(context)


    return HttpResponse(rendered)
