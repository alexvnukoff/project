# -*- encoding: utf -*-

import json
import logging


from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from guardian.shortcuts import get_objects_for_user

from appl import func
from b24online.cbv import (ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate,
                      GalleryImageList, DeleteGalleryImage, DeleteDocument, DocumentList)
from b24online.models import (Company, News, Tender, Exhibition, B2BProduct,
        BusinessProposal, InnovationProject, Vacancy, Organization, Branch,
        Chamber, StaffGroup, PermissionsExtraGroup, Video)
from centerpokupok.models import B2CProduct
from b24online.Companies.forms import AdditionalPageFormSet, CompanyForm, AdminCompanyForm
from b24online.Messages.forms import MessageForm

logger = logging.getLogger(__name__)


class CompanyList(ItemsList):
    # pagination url
    url_paginator = "companies:paginator"
    url_my_paginator = "companies:my_main_paginator"

    current_section = _("Companies")
    addUrl = 'companies:add'

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css',
        settings.STATIC_URL + 'b24online/css/tpp.reset.css'
    ]

    # allowed filter list
    # filter_list = ['tpp', 'country', 'branch']

    model = Company

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Companies/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Companies/index.html'

    def get_add_url(self):
        if self.request.user.is_authenticated():
            return self.addUrl

        return None

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('countries', 'parent')

    def get_queryset(self):
        queryset = super(CompanyList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects().filter(Q(parent_id=current_org) | Q(pk=current_org))
            else:
                queryset = get_objects_for_user(self.request.user, ['b24online.manage_organization'],
                                                Organization.get_active_objects().all()) \
                    .instance_of(Company)

        return queryset


class CompanyDetail(ItemDetail):
    model = Company
    template_name = 'b24online/Companies/detailContent.html'

    current_section = _("Companies")
    addUrl = 'companies:add'

    def get_add_url(self):
        if self.request.user.is_authenticated():
            return self.addUrl

        return None

    def _get_payed_status(self):
        # TODO
        pass

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({'staffgroups': StaffGroup.get_options()})
        context_data.update({
            'extragroups': PermissionsExtraGroup.get_options()
        })
        return context_data


def _tab_news(request, company, page=1):
    news = News.get_active_objects().filter(organization=company)
    paginator = Paginator(news, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_news_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tabNews.html', template_params, context_instance=RequestContext(request))


def _tab_tenders(request, company, page=1):
    tenders = Tender.get_active_objects().filter(organization=company)
    paginator = Paginator(tenders, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_tenders_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,

    }

    return render_to_response('b24online/Companies/tabTenders.html', template_params, context_instance=RequestContext(request))


def _tabs_exhibitions(request, company, page=1):
    exhibitions = Exhibition.get_active_objects().filter(organization=company)
    paginator = Paginator(exhibitions, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_exhibitions_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tabExhibitions.html', template_params,
                              context_instance=RequestContext(request))


def _tab_b2b_products(request, company, page=1):
    products = B2BProduct.get_active_objects().filter(company=company)
    paginator = Paginator(products, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_b2b_products_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tab_B2BProducts.html', template_params, context_instance=RequestContext(request))


def _tab_b2c_products(request, company, page=1):
    products = B2CProduct.get_active_objects().filter(company=company)
    paginator = Paginator(products, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_b2c_products_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tab_B2CProducts.html', template_params, context_instance=RequestContext(request))


def _tab_proposals(request, company, page=1):
    proposals = BusinessProposal.get_active_objects().filter(organization=company)
    paginator = Paginator(proposals, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_proposal_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tabProposal.html', template_params, context_instance=RequestContext(request))


def _tab_innovation_projects(request, company, page=1):
    projects = InnovationProject.get_active_objects().filter(organization=company)
    paginator = Paginator(projects, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_innov_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tabInnov.html', template_params, context_instance=RequestContext(request))


def _tab_structure(request, company, page=1):
    """
    Company view's tab 'Structure' processing.
    """
    organization = get_object_or_404(Company, pk=company)
    if request.is_ajax() and not request.user.is_anonymous() \
        and request.user.is_authenticated():

        item_id = request.POST.get("id", None)
        name = request.POST.get('name', '').strip()
        action = request.POST.get("action", None)
        request_type = request.POST.get("type", None)

        if not (request_type in ('department', 'vacancy')) and action is not None:
            return HttpResponseBadRequest()

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "add" and len(name) > 0:
            if request_type == 'department':
                organization.create_department(name, request.user)
            elif item_id is not None:  # new vacancy
                obj = get_object_or_404(organization.departments, pk=item_id)
                organization.create_vacancy(name, obj, request.user)

        elif action == "edit" and item_id is not None and len(name) > 0:
            if request_type == 'department':
                obj = get_object_or_404(organization.departments, pk=item_id)
            else:
                obj = get_object_or_404(organization.vacancies, pk=item_id)
            obj.name = name
            obj.save()
        elif action == "remove" and item_id is not None:
            if request_type == 'department':
                obj = get_object_or_404(organization.departments, pk=item_id)
            else:
                obj = get_object_or_404(organization.vacancies, pk=item_id)

            obj.delete()

    departments = organization.departments.all().prefetch_related('vacancies').order_by('name')

    paginator = Paginator(departments, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)
    url_paginator = "companies:tab_structure_paged"

    template_params = {
        'has_perm': organization.has_perm(request.user),
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
        'item_pk': company,
    }

    return render_to_response('b24online/Companies/tabStructure.html', template_params, context_instance=RequestContext(request))


def _tab_staff(request, company, page=1):
    organization = get_object_or_404(Company, pk=company)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
        action = request.POST.get('action', False)
        action = action if action else request.GET.get('action', None)

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "department":
            departments = [{'name': _("Select department"), "value": ""}]

            for department in organization.departments.all().order_by('name'):
                departments.append({"name": department.name, "value": department.pk})

            return HttpResponse(json.dumps(departments))

        elif action == "vacancy":
            department = int(request.GET.get("department", 0))

            if department <= 0:
                return HttpResponseBadRequest()

            vacancies = [{'name': _("Select vacancy"), "value": ""}]

            for department in organization.departments.all():
                for vacancy in department.vacancies.all().order_by('name'):
                    vacancies.append({"name": vacancy.name, "value": vacancy.pk})

            return HttpResponse(json.dumps(vacancies))

        elif action == "add":
            user = request.POST.get('user', "").strip()
            department = int(request.POST.get('department', 0))
            vacancy = int(request.POST.get('vacancy', 0))

            if not user or department <= 0 or vacancy <= 0:
                return HttpResponseBadRequest()

            try:
                user = get_user_model().objects.get(email=user, is_active=True)
                vacancy = Vacancy.objects.get(pk=vacancy, department__organization=organization)
            except ObjectDoesNotExist:
                return HttpResponseBadRequest(_('User not found'))

            # One user for vacancy
            if vacancy.user:
                return HttpResponseBadRequest(_("The vacancy already have employee attached"))

            if user.work_positions.filter(department__organization=organization).exists():
                return HttpResponseBadRequest(_("The user already employed in your organization"))

            admin = bool(int(request.POST.get('admin', 0)))
            vacancy.assign_employee(user, admin)

        elif action == "remove":
            cabinet = int(request.POST.get('id', 0))

            if cabinet > 0:
                user = get_object_or_404(get_user_model(), pk=cabinet)
                vacancy = get_object_or_404(Vacancy, user=user, department__organization=organization)
                vacancy.remove_employee()

    vacancies = Vacancy.objects.filter(user__isnull=False, department__organization=organization)\
        .select_related('user', 'user__profile', 'department')

    paginator = Paginator(vacancies, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_staff_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
        'item_pk': company,
        'has_perm': organization.has_perm(request.user),
    }

    return render_to_response('b24online/Companies/tabStaff.html', template_params, context_instance=RequestContext(request))


def _tab_video(request, company, page=1):
    video = Video.get_active_objects().filter(organization=company)
    paginator = Paginator(video, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_video_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('b24online/Companies/tabVideo.html', template_params, context_instance=RequestContext(request))



class DeleteCompany(ItemDeactivate):
    model = Company

    def reindex_kwargs(self):
        kwargs = super().reindex_kwargs()
        kwargs['is_active_changed'] = True

        return kwargs


class CompanyGalleryImageList(GalleryImageList):
    owner_model = Company
    namespace = 'companies'


class DeleteCompanyGalleryImage(DeleteGalleryImage):
    owner_model = Company


class CompanyDocumentList(DocumentList):
    owner_model = Company
    namespace = 'companies'


class DeleteCompanyDocument(DeleteDocument):
    owner_model = Company


def send_message(request):
    """
    Send the message to :class:`Organization` (and `User` as recipient).
    """
    response_code = 'error'
    response_text = 'Error'
    if not request.is_ajax() or request.method != 'POST':
        return HttpResponseBadRequest()
    elif request.user.is_anonymous() or not request.user.is_authenticated():
        response_text = _('Only registered users can send the messages')
    else:
        form = MessageForm(request, data=request.POST, files=request.FILES)    
        if form.is_valid():
            try:
                form.send()        
            except IntegrityError as exc:
                response_text = _('Error during data saving') + str(exc)
            else:
                response_code = 'success'
                response_text = _('You have successfully sent the message')
        else:
            response_text = form.get_errors()  
    return HttpResponse(
        json.dumps({'code': response_code, 'message': response_text}),
        content_type='application/json'
    )


class CompanyUpdate(ItemUpdate):
    model = Company
    form_class = CompanyForm
    template_name = 'b24online/Companies/addForm.html'
    success_url = reverse_lazy('companies:main')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(instance=self.object)

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))

    def get_form_class(self):
        form_class = super().get_form_class()

        if self.request.user.is_admin or self.request.user.is_commando:
            form_class = AdminCompanyForm

        return form_class

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        form_class = self.get_form_class()

        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data:
            if 'vatin' in form.changed_data:
                form.instance.metadata['vat_identification_number'] = form.cleaned_data['vatin']

            if 'phone' in form.changed_data:
                form.instance.metadata['phone'] = form.cleaned_data['phone']

            if 'fax' in form.changed_data:
                form.instance.metadata['fax'] = form.cleaned_data['fax']

            if 'email' in form.changed_data:
                form.instance.metadata['email'] = form.cleaned_data['email']

            if 'site' in form.changed_data:
                form.instance.metadata['site'] = form.cleaned_data['site']

            if 'longitude' in form.changed_data or 'latitude' in form.changed_data:
                form.instance.metadata['location'] = '%s,%s' % (
                form.cleaned_data['latitude'], form.cleaned_data['longitude']),

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                if not page_form.instance.pk:
                    page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

            if form.changed_data:
                self.object.countries = [form.cleaned_data['country']]

                if 'chamber' in form.changed_data:
                    self.object.parent = form.cleaned_data.get('chamber')
                    self.object.save()

        if form.changed_data:
            self.object.reindex()

            if 'logo' in form.changed_data:
                self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))


class CompanyCreate(ItemCreate):
    model = Company
    form_class = CompanyForm
    template_name = 'b24online/Companies/addForm.html'
    success_url = reverse_lazy('companies:main')
    org_required = False
    org_model = Chamber

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet()

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user

        form.instance.metadata = {
            'vat_identification_number': form.cleaned_data['vatin'],
            'phone': form.cleaned_data['phone'],
            'fax': form.cleaned_data['fax'],
            'email': form.cleaned_data['email'],
            'site': form.cleaned_data['site'],
            'location': '%s,%s' % (form.cleaned_data['latitude'], form.cleaned_data['longitude'])
        }

        with transaction.atomic():
            self.object = form.save()
            self.object.countries.add(form.cleaned_data['country'])

            if form.cleaned_data.get('chamber'):
                self.object.parent = form.cleaned_data.get('chamber')
                self.object.save()

            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        self.object.reindex()

        if 'logo' in form.changed_data:
            self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        return self.render_to_response(context_data)
