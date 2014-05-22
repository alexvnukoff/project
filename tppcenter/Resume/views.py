from haystack.backends import SQ
from appl.func import getActiveSQS, filterLive, setPaginationForSearchWithValues, getUserPermsForObjectsList, \
    getPaginatorRange
from appl.models import Tender, Gallery, AdditionalPages, Organization, Resume, Cabinet
from appl import func
from core.tasks import addNewResume
from core.models import Dictionary, Item
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.forms.models import modelformset_factory
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
import json

@login_required(login_url='/login/')
def get_resume_list(request, page=1, item_id=None, my=None, slug=None):


   # if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('tenders:detail',  args=[slug]))


    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    title = ''

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]



    scripts = []

    if item_id is None:
        resumepage = _resumeList(request, my=my, page=page)
    else:
        result = _resumeDetailContent(request, item_id)
        resumepage = result[0]
        title = result[1]

    if not request.is_ajax():
        templateParams =  {
                'current_section': 'Resume',
                'resumepage': resumepage,
                'addNew': reverse('resume:add'),
                'item_id': item_id,
                 'title': title
            }

        return render_to_response("Resume/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': resumepage,
        }

        return HttpResponse(json.dumps(serialize))


def _resumeList(request, my=None, page=1):

    query = request.GET.urlencode()

    q = request.GET.get('q', '')

    if not my:
            filters, searchFilter = filterLive(request)

            sqs = getActiveSQS().models(Resume).order_by('-obj_create_date')

            if len(searchFilter) > 0: #Got filter values
                sqs = sqs.filter(searchFilter)

            if q != '': #Search for content
                sqs = sqs.filter(SQ(title=q) | SQ(text=q))

            sortFields = {
                'date': 'id',
                'name': 'title_sort'
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
            url_paginator = "%s:paginator" % ('resume')

            params = {
                'filters': filters,
                'sortField1': sortField1,
                'sortField2': sortField2,
                'order1': order1,
                'order2': order2
            }
    else:
            current_organization = request.session.get('current_company', False)

            cabinet = Cabinet.objects.get(user=request.user.pk).pk
            proposal = getActiveSQS().models(Resume).filter(cabinet=cabinet)


            if q != '': #Search for content
                proposal = proposal.filter(SQ(title=q) | SQ(text=q))

            proposal.order_by('-obj_create_date')

            url_paginator = "%s:my_main_paginator" % 'resume'
            params = {}

    result = setPaginationForSearchWithValues(proposal, *('NAME', 'SLUG'), page_num=5, page=page)

    proposalList = result[0]
    proposal_ids = [id for id in proposalList.keys()]
    redactor = False
    if request.user.is_authenticated():
        items_perms = getUserPermsForObjectsList(request.user, proposal_ids, Resume.__name__)
    else:
        items_perms = ""


    page = result[1]
    paginator_range = getPaginatorRange(page)




    template = loader.get_template("Resume/contentPage.html")

    templateParams = {
       'resumeValues': proposalList,
       'page': page,
       'paginator_range': paginator_range,
       'url_paginator': url_paginator,
       'items_perms': items_perms,
       'current_path': request.get_full_path(),
       'redactor': redactor

    }
    templateParams.update(params)
    context = RequestContext(request, templateParams)
    rendered = template.render(context)


    return rendered






def _resumeDetailContent(request, item_id):

    resume = get_object_or_404(Resume, pk=item_id)


    attr = (
        'NAME', 'BIRTHDAY', 'MARITAL_STATUS', 'NATIONALITY', 'TELEPHONE_NUMBER','ADDRESS', 'FACULTY', 'PROFESSION',
        'STUDY_START_DATE', 'STUDY_END_DATE', 'STUDY_FORM', 'COMPANY_EXP_1', 'COMPANY_EXP_2','COMPANY_EXP_3',
        'POSITION_EXP_1', 'POSITION_EXP_2', 'POSITION_EXP_3', 'START_DATE_EXP_1', 'START_DATE_EXP_2','START_DATE_EXP_3',
        'END_DATE_EXP_1', 'END_DATE_EXP_2', 'END_DATE_EXP_3', 'ADDITIONAL_STUDY', 'LANGUAGE_SKILL','COMPUTER_SKILL',
        'ADDITIONAL_SKILL', 'SALARY', 'ADDITIONAL_INFORMATION', 'INSTITUTION'
    )

    resumeValues = resume.getAttributeValues(*attr)

    title = resumeValues.get('NAME', False)[0] if resumeValues.get('NAME', False) else ""


    template = loader.get_template('Resume/detailContent.html')

    templateParams = {
       'resumeValues': resumeValues,
       'item_id': item_id
        }

    context = RequestContext(request, templateParams)
    rendered = template.render(context)



    return rendered, title



@login_required(login_url='/login/')
def resumeForm(request, action, item_id=None):
    if item_id:
       if not Resume.active.get_active().filter(pk=item_id, c2p__parent=Cabinet.objects.get(user=request.user.pk)).exists():
         return HttpResponseNotFound()


    current_section = _("Resume")
    resumePage = ''

    if action == 'delete':
        resumePage = deleteResume(request, item_id)

    if action == 'add':
        resumePage = addResume(request)

    if action == 'update':
        resumePage = updateResume(request, item_id)

    if isinstance(resumePage, HttpResponseRedirect) or isinstance(resumePage, HttpResponse):
        return resumePage

    templateParams = {
        'formContent': resumePage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

def addResume(request):

    resumes = Resume.active.get_active().filter(c2p__parent=Cabinet.objects.get(user=request.user.pk))



    if resumes.count() == 5:
         return func.permissionDenied()

    form = None

    marital = Dictionary.objects.get(title='MARITAL_STATUS')
    marital_slots = marital.getSlotsList()

    study = Dictionary.objects.get(title='STUDY_FORM')
    study_slots = study.getSlotsList()

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Resume', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewResume.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('resume:main'))

    template = loader.get_template('Resume/addForm.html')
    context = RequestContext(request, {'form': form, 'marital_slots': marital_slots, 'study_slots': study_slots})
    tendersPage = template.render(context)

    return tendersPage


def updateResume(request, item_id):

    form = ItemForm('Resume', id=item_id)

    marital = Dictionary.objects.get(title='MARITAL_STATUS')
    marital_slots = marital.getSlotsList()

    study = Dictionary.objects.get(title='STUDY_FORM')
    study_slots = study.getSlotsList()

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Resume', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewResume.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                               lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('resume:main'))

    template = loader.get_template('Resume/addForm.html')

    templateParams = {
        'marital_slots': marital_slots,
        'study_slots': study_slots,
        'form': form,

    }

    context = RequestContext(request, templateParams)
    tendersPage = template.render(context)

    return tendersPage



def deleteResume(request, item_id):


    instance = Resume.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()





    return HttpResponseRedirect(reverse('resume:main'))



