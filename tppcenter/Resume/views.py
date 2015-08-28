from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext as _, trans_real

from appl.models import Cabinet
from appl import func
from b24online.cbv import ItemsList, ItemDetail
#from core.tasks import addNewResume
from core.models import Dictionary
from jobs.models import Resume
from tppcenter.forms import ItemForm


class ResumeList(ItemsList):

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(ResumeList, self).dispatch(*args, **kwargs)

    #pagination url
    url_paginator = "resume:paginator"
    url_my_paginator = "resume:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _('Resume')
    addUrl = 'resume:add'

    #allowed filter list
    # filter_list = []

    model = Resume

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Resume/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Resume/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('user__profile')

    def get_queryset(self):
        queryset = super(ResumeList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = queryset.none()
            else:
                queryset = self.model.objects.filter(created_by=self.request.user)

        return queryset


class ResumeDetail(ItemDetail):

    model = Resume
    template_name = 'Resume/detailContent.html'

    current_section = _('Resume')
    addUrl = 'resume:add'

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(ResumeDetail, self).dispatch(*args, **kwargs)


@login_required
def resumeForm(request, action, item_id=None):
    if item_id:
       if not Resume.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Resume")
    resumePage = ''

    if action == 'delete':
        resumePage = deleteResume(request, item_id)
    elif action == 'add':
        resumePage = addResume(request)
    elif action == 'update':
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
            #addNewResume.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('resume:main'))

    template = loader.get_template('Resume/addForm.html')
    context = RequestContext(request, {'form': form, 'marital_slots': marital_slots, 'study_slots': study_slots})
    tendersPage = template.render(context)

    return tendersPage


def updateResume(request, item_id):

    try:
        item = Resume.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return func.emptyCompany()


    perm_list = item.getItemInstPermList(request.user)

    if 'change_resume' not in perm_list:
        return func.permissionDenied()


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
            # addNewResume.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
            #                    lang_code=trans_real.get_language())

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

    try:
        item = Resume.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return func.emptyCompany()
    
    perm_list = item.getItemInstPermList(request.user)

    if 'delete_resume' not in perm_list:
        return func.permissionDenied()


    instance = Resume.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()





    return HttpResponseRedirect(reverse('resume:main'))