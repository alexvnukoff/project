import json

from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.views.generic import UpdateView, CreateView
from guardian.shortcuts import get_objects_for_user

from appl import func
from appl.models import Cabinet
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Company, News, Tender, Exhibition, B2BProduct, BusinessProposal, InnovationProject, \
    Department, Vacancy, Gallery, GalleryImage, Organization, Branch
from core.models import User
#from core.tasks import addNewCompany
from core.amazonMethods import add
from tppcenter.Companies.forms import AdditionalPageFormSet, CompanyForm
from tppcenter.Messages.views import add_message


class CompanyList(ItemsList):
    # pagination url
    url_paginator = "companies:paginator"
    url_my_paginator = "companies:my_main_paginator"

    current_section = _("Companies")
    addUrl = 'companies:add'

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    # allowed filter list
    # filter_list = ['tpp', 'country', 'branch']

    model = Company

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Companies/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Companies/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('countries', 'parent')

    def get_queryset(self):
        queryset = super(CompanyList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(parent_id=current_org)
            else:
                queryset = get_objects_for_user(self.request.user, ['manage_organization'], Organization)\
                    .instance_of(Company)

        return queryset


class CompanyDetail(ItemDetail):
    model = Company
    template_name = 'Companies/detailContent.html'

    current_section = _("Companies")
    addUrl = 'companies:add'

    def _get_payed_status(self):
        # TODO
        pass


def _tab_news(request, company, page=1):
    news = News.objects.filter(organization=company)
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

    return render_to_response('Companies/tabNews.html', template_params, context_instance=RequestContext(request))


def _tab_tenders(request, company, page=1):
    tenders = Tender.objects.filter(organization=company)
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

    return render_to_response('Companies/tabTenders.html', template_params, context_instance=RequestContext(request))


def _tabs_exhibitions(request, company, page=1):
    exhibitions = Exhibition.objects.filter(organization=company)
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

    return render_to_response('Companies/tabExhibitions.html', template_params,
                              context_instance=RequestContext(request))


def _tab_products(request, company, page=1):
    products = B2BProduct.objects.filter(company=company)
    paginator = Paginator(products, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_products_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company
    }

    return render_to_response('Companies/tabProducts.html', template_params, context_instance=RequestContext(request))


def _tab_proposals(request, company, page=1):
    proposals = BusinessProposal.objects.filter(organization=company)
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

    return render_to_response('Companies/tabProposal.html', template_params, context_instance=RequestContext(request))


def _tab_innovation_projects(request, company, page=1):
    projects = InnovationProject.objects.filter(organization=company)
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

    return render_to_response('Companies/tabInnov.html', template_params, context_instance=RequestContext(request))


def _tab_structure(request, company, page=1):
    organization = get_object_or_404(Company, pk=company)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
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
        'item_pk': company
    }

    return render_to_response('Companies/tabStructure.html', template_params, context_instance=RequestContext(request))


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
                user = User.objects.get(email=user)
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
                user = get_object_or_404(User, pk=cabinet)
                vacancy = get_object_or_404(Vacancy, user=user, department__organization=organization)
                vacancy.remove_employee()

    users = User.objects.filter(work_positions__department__organization=organization).distinct() \
        .select_related('profile').prefetch_related('work_positions', 'work_positions__department')

    paginator = Paginator(users, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tab_staff_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
        'item_pk': company,
        'has_perm': organization.has_perm(request.user)
    }

    return render_to_response('Companies/tabStaff.html', template_params, context_instance=RequestContext(request))


@login_required
def companyForm(request, action, item_id=None):
    if item_id:
        if not Company.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    current_section = _("Companies")

    newsPage = ''

    if action == 'delete':
        newsPage = deleteCompany(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templatePrarams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templatePrarams, context_instance=RequestContext(request))


def deleteCompany(request, item_id):
    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_company' not in perm_list:
        return func.permissionDenied()

    instance = Company.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('companies:main'))


def _tab_gallery(request, item, page=1):
    organization = get_object_or_404(Company, pk=item)
    file = request.FILES.get('Filedata', None)
    has_perm = False

    if organization.has_perm(request.user):
        has_perm = True

    if file is not None:
        if has_perm:
            file = add(request.FILES['Filedata'], {'big': {'box': (130, 120), 'fit': True}})

            if not organization.galleries.exists():
                gallery = Gallery.create_default_gallery(organization, request.user)
            else:
                gallery = organization.galleries.first()

            gallery.add_image(request.user, file)

            return HttpResponse('')
        else:
            return HttpResponseBadRequest()
    else:
        photos = GalleryImage.objects.filter(gallery__in=organization.galleries.all())
        paginator = Paginator(photos, 10)
        page = paginator.page(page)
        paginator_range = func.get_paginator_range(page)

        url_paginator = "companies:tabs_gallery_paged"

        template_params = {
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'gallery': page.object_list,
            'has_perm': has_perm,
            'item_id': item,
            'pageNum': page.number,
            'url_parameter': item
        }

        return render_to_response(
            'Companies/tabGallery.html',
            template_params,
            context_instance=RequestContext(request)
        )


def gallery_structure(request, organization, page=1):
    organization = get_object_or_404(Company, pk=organization)
    photos = GalleryImage.objects.filter(gallery__in=organization.galleries.all())
    paginator = Paginator(photos, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "companies:tabs_gallery_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'gallery': page.object_list,
        'pageNum': page.number,
        'url_parameter': organization.pk
    }

    return render_to_response(
        'Companies/tab_gallery_structure.html',
        template_params,
        context_instance=RequestContext(request)
    )


def gallery_remove_item(request, item):
    photo = get_object_or_404(GalleryImage, pk=item)

    if photo.has_perm(request.user):
        photo.delete()
    else:
        return HttpResponseBadRequest()

    return HttpResponse()


def send_message(request):
    if request.is_ajax():
        if not request.user.is_anonymous() and request.user.is_authenticated() and request.POST.get('company', False):
            if request.POST.get('message', False) or request.FILES.get('file', False):
                company_pk = request.POST.get('company')

                # this condition as temporary design for separation Users and Organizations
                if Cabinet.objects.filter(pk=int(company_pk)).exists():
                    add_message(request, content=request.POST.get('message', ""), recipient_id=int(company_pk))
                    response = _('You have successfully sent the message.')
                # /temporary condition for separation Users and Companies

                else:
                    organization = Company.objects.get(pk=company_pk)

                    if not organization.email:
                        email = 'admin@tppcenter.com'
                        subject = _('This message was sent to company with id: ') + str(organization.pk)
                    else:
                        subject = _('New message')
                    mail = EmailMessage(
                        subject,
                        request.POST.get('message', ""),
                        'noreply@tppcenter.com',
                        [organization.email]
                    )

                    attachment = request.FILES.get('file', False)

                    if attachment:
                        mail.attach(attachment.name, attachment.read(), attachment.content_type)
                    mail.send()

                    response = _('You have successfully sent the message.')

            else:
                response = _('Message or file are required')
        else:
            response = _('Only registered users can send the messages')

        return HttpResponse(response)

    return HttpResponseBadRequest()


class CompanyUpdate(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'Companies/addForm.html'
    success_url = reverse_lazy('companies:main')

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
                form.instance.metadata['location'] = '%s,%s' % (form.cleaned_data['latitude'], form.cleaned_data['longitude']),

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


class CompanyCreate(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'Companies/addForm.html'
    success_url = reverse_lazy('companies:main')

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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