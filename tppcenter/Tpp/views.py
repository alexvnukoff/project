import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms.models import modelformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils.translation import trans_real
from guardian.shortcuts import get_objects_for_user

from appl import func
from appl.models import Tpp, Country, AdditionalPages
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Chamber, Company, News, Tender, Exhibition, BusinessProposal, InnovationProject, \
    Organization, Department, Vacancy, Gallery, GalleryImage
from core.amazonMethods import add
from core.models import User
from tppcenter.forms import ItemForm, BasePages
from core.tasks import addNewTpp


class ChamberList(ItemsList):
    # pagination url
    url_paginator = "tpp:paginator"
    url_my_paginator = "tpp:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    current_section = _("Tpp")

    # allowed filter list
    filter_list = ['country']

    model = Chamber

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Tpp/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Tpp/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('parent').prefetch_related('countries')

    def get_queryset(self):
        queryset = super(ChamberList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                return queryset.none()
            else:
                queryset = get_objects_for_user(self.request.user, ['manage_organization'], Organization)\
                    .instance_of(Chamber)

        return queryset


class ChamberDetail(ItemDetail):
    model = Chamber
    template_name = 'Tpp/detailContent.html'

    current_section = _("Tpp")


@login_required(login_url='/login/')
def tpp_form(request, action, item_id=None):
    if item_id:
        if not Tpp.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    current_section = _("Tpp")

    if action == 'add':
        tpp_page = add_tpp(request)
    else:
        tpp_page = update_tpp(request, item_id)

    if isinstance(tpp_page, HttpResponseRedirect) or isinstance(tpp_page, HttpResponse):
        return tpp_page

    template_params = {
        'formContent': tpp_page,
        'current_section': current_section
    }

    return render_to_response('forms.html', template_params, context_instance=RequestContext(request))


def add_tpp(request):
    form = None
    countries = func.getItemsList("Country", 'NAME')
    user = request.user

    pages = None

    user_groups = user.groups.values_list('name', flat=True)

    if not user.is_manager or not 'TPP Creator' in user_groups:
        return func.permissionDenied()

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=5, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
            pages = pages.new_objects
        else:
            pages = ""

        form = ItemForm('Tpp', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('tpp:main'))

    template = loader.get_template('Tpp/addForm.html')
    context = RequestContext(request, {'form': form, 'countries': countries, 'pages': pages})
    tppPage = template.render(context)

    return tppPage


def update_tpp(request, item_id):
    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_tpp' not in perm_list:
        return func.permissionDenied()

    try:
        choosen_country = Country.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""

    countries = func.getItemsList("Country", 'NAME')
    tpp = Tpp.objects.get(pk=item_id)

    form = ItemForm('Tpp', id=item_id)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)

        form = ItemForm('Tpp', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                            lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next', reverse('tpp:main')))

    template = loader.get_template('Tpp/addForm.html')

    template_params = {
        'form': form,
        'choosen_country': choosen_country,
        'countries': countries,
        'tpp': tpp,
        'pages': pages
    }

    context = RequestContext(request, template_params)
    tpp_page = template.render(context)

    return tpp_page


def _tab_companies(request, tpp, page=1):
    companies = Company.objects.filter(parent=tpp)
    paginator = Paginator(companies, 10)

    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_companies_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Tpp/tabCompanies.html', template_params, context_instance=RequestContext(request))


def _tab_news(request, tpp, page=1):
    news = News.objects.filter(organization=tpp)
    paginator = Paginator(news, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_news_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Tpp/tabNews.html', template_params, context_instance=RequestContext(request))


def _tab_tenders(request, tpp, page=1):
    tenders = Tender.objects.filter(organization=tpp)
    paginator = Paginator(tenders, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_tenders_paged"

    template_arams = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Tpp/tabTenders.html', template_arams, context_instance=RequestContext(request))


def _tab_exhibitions(request, tpp, page=1):
    exhibitions = Exhibition.objects.filter(organization=tpp)
    paginator = Paginator(exhibitions, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_exhibitions_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Tpp/tabExhibitions.html', template_params, context_instance=RequestContext(request))


def _tab_proposals(request, tpp, page=1):
    proposals = BusinessProposal.objects.filter(organization=tpp)
    paginator = Paginator(proposals, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_proposal_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Companies/tabProposal.html', template_params, context_instance=RequestContext(request))


def _tab_innovation_projects(request, tpp, page=1):
    projects = InnovationProject.objects.filter(organization=tpp)
    paginator = Paginator(projects, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_innov_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render_to_response('Companies/tabInnov.html', template_params, context_instance=RequestContext(request))


def _tab_structure(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
        try:
            item_id = int(request.POST.get("id", 0))
        except ValueError:
            item_id = 0

        name = request.POST.get('name', '').strip()
        action = request.POST.get("action", None)

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "add" and len(name) > 0:
            if item_id == 0:  # new department
                Department.objects.create(
                    name=name, created_by=request.user,
                    updated_by=request.user,
                    organization=organization
                )
            else:  # new vacancy
                department = get_object_or_404(Department, pk=item_id, organization=organization)
                Vacancy.objects.create(
                    name=name,
                    created_by=request.user,
                    updated_by=request.user,
                    department=department
                )
        elif action == "edit" and item_id > 0 and len(name) > 0:
            try:
                obj = organization.departments.get(pk=item_id)
            except ObjectDoesNotExist:
                obj = get_object_or_404(Vacancy, pk=item_id, department__organization=organization)

            obj.name = name
            obj.save()

        elif action == "remove" and item_id > 0:
            try:
                obj = organization.departments.get(pk=item_id, organization=organization)
            except ObjectDoesNotExist:
                obj = get_object_or_404(Vacancy, pk=item_id, department__organization=organization)

            obj.delete()

    departments = organization.departments.all().order_by('name')

    paginator = Paginator(departments, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)
    url_paginator = "tpp:tab_structure_paged"

    template_params = {
        'has_perm': organization.has_perm(request.user),
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
        'item_pk': tpp
    }

    return render_to_response('Tpp/tabStructure.html', template_params, context_instance=RequestContext(request))


def _tab_staff(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
        action = request.POST.get('action', False)
        action = action if action else request.GET.get('action', None)

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "department":
            departments = [{'name': _("Select department"), "value": ""}]

            for department in organization.departments.all().order_by('text'):
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

    url_paginator = "tpp:tab_staff_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
        'item_pk': tpp,
        'has_perm': organization.has_perm(request.user)
    }

    return render_to_response('Tpp/tabStaff.html', template_params, context_instance=RequestContext(request))


def _tab_gallery(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)
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

        url_paginator = "tpp:tabs_gallery_paged"

        template_params = {
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'gallery': page.object_list,
            'has_perm': has_perm,
            'item_id': tpp,
            'pageNum': page.number,
            'url_parameter': tpp
        }

        return render_to_response('Tpp/tabGallery.html', template_params, context_instance=RequestContext(request))


def gallery_structure(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)
    photos = GalleryImage.objects.filter(gallery__in=organization.galleries.all())
    paginator = Paginator(photos, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tabs_gallery_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'gallery': page.object_list,
        'pageNum': page.number,
        'url_parameter': tpp
    }

    return render_to_response(
        'Tpp/tab_gallery_structure.html',
        template_params,
        context_instance=RequestContext(request)
    )


def gallery_remove_item(request, tpp):
    photo = get_object_or_404(GalleryImage, pk=tpp)

    if photo.has_perm(request.user):
        photo.delete()
    else:
        return HttpResponseBadRequest()

    return HttpResponse()
