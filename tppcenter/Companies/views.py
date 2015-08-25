import json

from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.forms.models import modelformset_factory
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.utils.translation import trans_real
from guardian.shortcuts import get_objects_for_user

from appl import func
from appl.models import Country, Branch, Tpp, Cabinet
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Company, News, Tender, Exhibition, B2BProduct, BusinessProposal, InnovationProject, \
    Department, Vacancy, AdditionalPages, Gallery, GalleryImage, Organization
from core.models import Item, User
from core.tasks import addNewCompany
from core.amazonMethods import add
from tppcenter.forms import ItemForm, BasePages
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
                Department.objects.create(
                    name=name,
                    created_by=request.user,
                    updated_by=request.user,
                    organization=organization
                )
            elif item_id is not None:  # new vacancy
                obj = get_object_or_404(Department, pk=item_id, organization=organization)

                Vacancy.objects.create(
                    name=name,
                    created_by=request.user,
                    updated_by=request.user,
                    department=obj
                )

        elif action == "edit" and item_id is not None and len(name) > 0:
            if request_type == 'department':
                obj = get_object_or_404(Department, pk=item_id, organization=organization)
            else:
                obj = get_object_or_404(Vacancy, pk=item_id, department__organization=organization)

            obj.name = name
            obj.save()
        elif action == "remove" and item_id is not None:
            if request_type == 'department':
                obj = get_object_or_404(Department, pk=item_id, organization=organization)
            else:
                obj = get_object_or_404(Vacancy, pk=item_id, department__organization=organization)

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
    elif action == 'add':
        newsPage = addCompany(request)
    elif action == 'update':
        newsPage = updateCompany(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templatePrarams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templatePrarams, context_instance=RequestContext(request))


def addCompany(request):
    user = request.user

    user_groups = user.groups.values_list('name', flat=True)

    if not 'Company Creator' in user_groups:
        return func.permissionDenied()

    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')

    pages = None

    choosen_country = 0
    choosen_tpp = 0
    currentBranch = 0

    if request.POST:

        currentBranch = int(request.POST.get('BRANCH', 0))

        try:
            choosen_tpp = int(request.POST.get('TPP', 0))
        except ValueError:
            choosen_tpp = 0

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")
        choosen_country = request.POST.get('COUNTRY', "")

        form = ItemForm('Company', values=values)
        form.clean()
        try:
            choosen_country = int(choosen_country)
        except ValueError:
            form.errors.update({"COUNTRY": _("Please select a country")})

        if choosen_country not in countries:
            form.errors.update({"COUNTRY": _("Invalid Country")})

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=5, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
            pages = pages.new_objects
        else:
            pages = ""

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)

            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID,
                                branch=branch, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('companies:main'))

    template = loader.get_template('Companies/addForm.html')

    context = RequestContext(request,
                             {'form': form, 'branches': branches, 'countries': countries, 'tpp': tpp, 'pages': pages,
                              'choosen_tpp': choosen_tpp, 'choosen_country': choosen_country,
                              'currentBranch': currentBranch})

    newsPage = template.render(context)

    return newsPage


def updateCompany(request, item_id):
    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_company' not in perm_list:
        return func.permissionDenied()
    try:
        choosen_country = Country.objects.get(p2c__child=item_id).pk
    except ObjectDoesNotExist:
        choosen_country = ""
    try:
        choosen_tpp = Tpp.objects.get(p2c__child=item_id).pk
    except ObjectDoesNotExist:
        choosen_tpp = ""

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')

    company = Company.objects.get(pk=item_id)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset

    branches = {}
    currentBranch = ''
    form = None

    if request.method != 'POST':
        branches = Branch.objects.all()
        branches_ids = [branch.pk for branch in branches]
        branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

        try:
            currentBranch = Branch.objects.get(p2c__child=item_id).pk
        except ObjectDoesNotExist:
            pass

        form = ItemForm('Company', id=item_id)

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")
        country = request.POST.get('COUNTRY', "")

        form = ItemForm('Company', values=values, id=item_id)
        form.clean()

        try:
            country = int(country)
        except ValueError:
            form.errors.update({"COUNTRY": _("Please select a country")})

        if country not in countries:
            form.errors.update({"COUNTRY": _("Invalid Country")})

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch,
                                lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('companies:main'))

    template = loader.get_template('Companies/addForm.html')

    templateParams = {
        'form': form,
        'branches': branches,
        'currentBranch': currentBranch,
        'company': company,
        'choosen_country': choosen_country,
        'countries': countries,
        'choosen_tpp': choosen_tpp,
        'tpp': tpp,
        'pages': pages
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage


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