from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings

from appl import func
from tppcenter.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate
from b24online.models import Organization
from core.models import Relationship
from jobs.models import Requirement, Resume
from tppcenter.Vacancy.forms import RequirementForm


class RequirementList(ItemsList):

    #pagination url
    url_paginator = "vacancy:paginator"
    url_my_paginator = "vacancy:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Job requirements")
    addUrl = 'vacancy:add'

    #allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = Requirement

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Vacancy/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Vacancy/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('country')

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(vacancy__department__organization_id=current_org)
            else:
                queryset = queryset.objects.none()

        return queryset


class RequirementDetail(ItemDetail):

    model = Requirement
    template_name = 'Vacancy/detailContent.html'

    current_section = _("Vacancy")
    addUrl = 'vacancy:add'

    def _get_user_resume_list(self):
        return Resume.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(RequirementDetail, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            context['resumes'] = self._get_user_resume_list()

        return context


@login_required
def vacancyForm(request, action, item_id=None):
    if item_id:
       if not Requirement.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Vacancy")

    vacancyPage = deleteVacancy(request, item_id)


    if isinstance(vacancyPage, HttpResponseRedirect) or isinstance(vacancyPage, HttpResponse):
        return vacancyPage

    templateParams = {
        'formContent': vacancyPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def deleteVacancy(request, item_id):
    item = Organization.objects.get(p2c__child__p2c__child__p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_requirement' not in perm_list:
        return func.permissionDenied()

    instance = Requirement.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()


    return HttpResponseRedirect(request.GET.get('next'), reverse('vacancy:main'))


def sendResume(request):
    response = ""
    if request.is_ajax():
        if request.user.is_authenticated() and request.POST.get('VACANCY', False):
            if request.POST.get('RESUME', False):
                requirement = request.POST.get('VACANCY', "")
                resume = request.POST.get('RESUME', '')
                if Relationship.objects.filter(parent=Requirement.objects.get(pk=int(requirement)), child=Resume.objects.get(pk=int(resume))).exists():
                      response = _('You cannot send more than one resume at the same job position.')
                else:
                    Relationship.setRelRelationship(parent=Requirement.objects.get(pk=int(requirement)), child=Resume.objects.get(pk=int(resume)), user=request.user)
                    response = _('You have successfully sent the resume.')

            else:
                response = _('Resume  are required')
        else:
             response = _('Only registred users can send resume')

        return HttpResponse(response)


class RequirementCreate(ItemCreate):
    org_required = False
    model = Requirement
    form_class = RequirementForm
    template_name = 'Vacancy/addForm.html'
    success_url = reverse_lazy('vacancy:main')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.vacancy = form.cleaned_data.get('vacancy')

        result = super().form_valid(form)
        self.object.reindex()

        return result


class RequirementUpdate(ItemUpdate):
    model = Requirement
    form_class = RequirementForm
    template_name = 'Vacancy/addForm.html'
    success_url = reverse_lazy('vacancy:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user

        result = super().form_valid(form)

        if form.changed_data:
            if 'vacancy' in form.changed_data:
                form.instance.vacancy = form.cleaned_data.get('vacancy')

            self.object.reindex()

        return result
