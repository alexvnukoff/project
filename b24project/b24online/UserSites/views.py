from collections import OrderedDict
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView
from b24online.models import Organization, Company, BannerBlock
from b24online.UserSites.forms import GalleryImageFormSet, SiteForm, TemplateForm, CompanyBannerFormSet, ChamberBannerFormSet
from usersites.models import UserSite, ExternalSiteTemplate, UserSiteTemplate, UserSiteSchemeColor

@login_required()
def form_dispatch(request):
    organization_id = request.session.get('current_company', None)
    if not organization_id:
        return HttpResponseRedirect(reverse('denied'))
    organization = Organization.objects.get(pk=organization_id)
    try:
        site = UserSite.objects.get(organization=organization)
        return SiteUpdate.as_view()(request, site=site, organization=organization)
    except ObjectDoesNotExist:
        return SiteCreate.as_view()(request, organization=organization)

class SiteCreate(CreateView):
    model = UserSite
    form_class = SiteForm
    template_name = 'b24online/UserSites/addForm.html'
    success_url = reverse_lazy('site:main')

    @method_decorator(login_required)
    def dispatch(self, request, organization, *args, **kwargs):
        self.organization = organization
        return super().dispatch(request, *args, **kwargs)

    def get_valid_blocks(self):
        valid_blocks = [
                "SITES LEFT 1",
                "SITES LEFT 2",
                "SITES FOOTER",
                "SITES RIGHT 1",
                "SITES RIGHT 2",
                "SITES RIGHT 3",
                "SITES RIGHT 4",
                "SITES RIGHT 5"
            ]

        additional = []
        for i in range(1,18):
            additional.append("SITES CAT {0}".format(i))
        valid_blocks += additional

        return OrderedDict(BannerBlock.objects.filter(
            block_type='user_site',
            code__in=valid_blocks
            ).order_by('id').values_list('pk', 'name'))

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        self.gallery_images_form = GalleryImageFormSet()
        banners_form = self.get_banners_form()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form,
                                                             gallery_images_form=self.gallery_images_form,
                                                             banners_form=banners_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = None
        form_class = self.get_form_class()
        self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES)
        banners_form = self.get_banners_form(self.request.POST, self.request.FILES)
        form = self.get_form(form_class)

        if form.is_valid() and self.gallery_images_form.is_valid() and banners_form.is_valid():
            return self.form_valid(form, gallery_images_form=self.gallery_images_form, banners_form=banners_form)
        else:
            return self.form_invalid(form, gallery_images_form=self.gallery_images_form, banners_form=banners_form)

    def get_banners_form(self, *args, **kwargs):
        if isinstance(self.organization, Company):
            form = CompanyBannerFormSet(*args, **kwargs)
        else:
            form = ChamberBannerFormSet(*args, **kwargs)

        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery_images_form'] = self.gallery_images_form

        return kwargs

    def form_valid(self, form, gallery_images_form, banners_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.organization = self.organization
        form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

        with transaction.atomic():
            domain = form.cleaned_data.get('domain', None)

            if not domain:
                domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), settings.USER_SITES_DOMAIN)

            form.instance.site = Site.objects.create(name='usersites', domain=domain)
            self.object = form.save()
            gallery_images_form.instance = self.object.get_gallery(self.request.user)
            banners_form.instance = self.object.site

            for gallery in gallery_images_form:
                gallery.instance.created_by = self.request.user
                gallery.instance.updated_by = self.request.user

            gallery_images_form.save()

            for banner in banners_form:
                banner.instance.created_by = self.request.user
                banner.instance.updated_by = self.request.user
                banner.instance.dates = (None, None)

            banners_form.save()

            changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]
            changed_banners = [obj.instance.image.path for obj in banners_form if obj.has_changed()]

        is_logo_changed = 'logo' in form.changed_data
        self.object.upload_images(is_logo_changed, changed_galleries, changed_banners)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, gallery_images_form, banners_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form,
                                             banners_form=banners_form)
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['domain'] = settings.USER_SITES_DOMAIN
        context_data['valid_blocks'] = self.get_valid_blocks()
        context_data['user_site_templates'] = UserSiteTemplate.objects.all()
        template_id = context_data.get('form')['template'].value()
        if template_id:
            context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

        return context_data


class SiteUpdate(UpdateView):
    model = UserSite
    form_class = SiteForm
    template_name = 'b24online/UserSites/addForm.html'
    success_url = reverse_lazy('site:main')

    @method_decorator(login_required)
    def dispatch(self, request, site, organization, *args, **kwargs):
        self.site = site
        self.organization = organization

        return super().dispatch(request, *args, **kwargs)

    def get_valid_blocks(self):
        valid_blocks = [
                "SITES LEFT 1",
                "SITES LEFT 2",
                "SITES FOOTER",
                "SITES RIGHT 1",
                "SITES RIGHT 2",
                "SITES RIGHT 3",
                "SITES RIGHT 4",
                "SITES RIGHT 5"
            ]

        additional = []
        for i in range(1,18):
            additional.append("SITES CAT {0}".format(i))
        valid_blocks += additional

        return OrderedDict(BannerBlock.objects.filter(
            block_type='user_site',
            code__in=valid_blocks
            ).order_by('id').values_list('pk', 'name'))

    def get_banners_form(self, *args, **kwargs):
        if isinstance(self.organization, Company):
            return CompanyBannerFormSet(*args, **kwargs)

        return ChamberBannerFormSet(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        self.gallery_images_form = GalleryImageFormSet(instance=self.object.get_gallery(self.request.user))
        banners_form = self.get_banners_form(instance=self.object.site)
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form,
                                                             gallery_images_form=self.gallery_images_form,
                                                             banners_form=banners_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES,
                                                       instance=self.object.get_gallery(self.request.user))
        banners_form = self.get_banners_form(self.request.POST, self.request.FILES, instance=self.object.site)
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid() and self.gallery_images_form.is_valid() and banners_form.is_valid():
            return self.form_valid(form, self.gallery_images_form, banners_form=banners_form)
        else:
            return self.form_invalid(form, self.gallery_images_form, banners_form=banners_form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery_images_form'] = self.gallery_images_form

        return kwargs

    def form_valid(self, form, gallery_images_form, banners_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user
        root_domain = self.object.root_domain or settings.USER_SITES_DOMAIN

        if form.has_changed() and ('sub_domain' in form.changed_data or 'domain' in form.changed_data):
            form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

        if 'facebook' in form.changed_data:
            form.instance.metadata['facebook'] = form.cleaned_data['facebook']

        if 'youtube' in form.changed_data:
            form.instance.metadata['youtube'] = form.cleaned_data['youtube']

        if 'twitter' in form.changed_data:
            form.instance.metadata['twitter'] = form.cleaned_data['twitter']

        if 'instagram' in form.changed_data:
            form.instance.metadata['instagram'] = form.cleaned_data['instagram']

        if 'vkontakte' in form.changed_data:
            form.instance.metadata['vkontakte'] = form.cleaned_data['vkontakte']

        if 'odnoklassniki' in form.changed_data:
            form.instance.metadata['odnoklassniki'] = form.cleaned_data['odnoklassniki']

        with transaction.atomic():
            self.object = form.save()
            gallery_images_form.instance = self.object.get_gallery(self.request.user)

            for gallery in gallery_images_form:
                gallery.instance.created_by = self.request.user
                gallery.instance.updated_by = self.request.user

            gallery_images_form.save()

            for banner in banners_form:
                banner.instance.created_by = self.request.user
                banner.instance.updated_by = self.request.user
                banner.instance.dates = (None, None)

            banners_form.save()
            domain = form.cleaned_data.get('domain', None)

            if not domain:
                domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), root_domain)

            site = self.object.site
            site.domain = domain
            site.save()

        changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]
        changed_banners = [obj.instance.image.path for obj in banners_form if obj.has_changed()]
        is_logo_changed = 'logo' in form.changed_data
        self.object.upload_images(is_logo_changed, changed_galleries, changed_banners)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, gallery_images_form, banners_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form, banners_form=banners_form)
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['valid_blocks'] = self.get_valid_blocks()
        template_id = context_data.get('form')['template'].value()
        context_data['user_site_templates'] = UserSiteTemplate.objects.all()

        if template_id:
            context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

        if self.object.domain_part == self.object.site.domain:
            context_data['domain'] = settings.USER_SITES_DOMAIN
        else:
            context_data['domain'] = self.object.root_domain

        return context_data

    def get_object(self, queryset=None):
        return self.site


class UserTemplateView(ListView):
    model = UserSiteTemplate
    template_name = 'b24online/UserSites/templateList.html'

    #def get_context_data(self, **kwargs):
    #    context = super(UserTemplateView, self).get_context_data(**kwargs)
    #    context['parent_category'] = self.cat.parent
    #    context['current_category'] = self.cat
    #    return context

    def get_queryset(self):
        #parent = self.kwargs['parent']
        #category = self.kwargs['category']
        return self.model.objects.filter(published=True)


class TemplateUpdate(UpdateView):
    model = UserSite
    form_class = TemplateForm
    template_name = 'b24online/UserSites/templateForm.html'
    success_url = reverse_lazy('site:main')

    def dispatch(self, request, *args, **kwargs):
        organization_id = request.session.get('current_company', None)
        if not organization_id:
            return HttpResponseRedirect(reverse('denied'))
        organization = Organization.objects.get(pk=organization_id)
        try:
            site = UserSite.objects.get(organization=organization)
            self.site = site
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('denied'))
        return super(TemplateUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            obj = UserSiteTemplate.objects.get(pk=self.template_id)
        except UserSiteTemplate.DoesNotExist:
            raise Http404("No found matching the template in UserSiteTemplate.")

        context['template'] = obj
        context['template_color'] = UserSiteSchemeColor.objects.filter(template=obj)
        return context

    def get_object(self, queryset=None):
        self.template_id = self.kwargs.get(self.pk_url_kwarg)
        return self.site
