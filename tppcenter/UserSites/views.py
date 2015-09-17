from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView

from b24online.models import Organization
from tppcenter.UserSites.forms import GalleryImageFormSet, SiteForm
from usersites.models import UserSite, ExternalSiteTemplate


@login_required()
def form_dispatch(request):
    organization_id = request.session.get('current_company', None)
    organization = Organization.objects.get(pk=organization_id)

    try:
        site = UserSite.objects.get(organization=organization)
        return SiteUpdate.as_view()(request, site=site)
    except ObjectDoesNotExist:
        return SiteCreate.as_view()(request)


class SiteCreate(CreateView):
    model = UserSite
    form_class = SiteForm
    template_name = 'UserSites/addForm.html'
    success_url = reverse_lazy('site:main')

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
        self.gallery_images_form = GalleryImageFormSet()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form, gallery_images_form=self.gallery_images_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = None
        form_class = self.get_form_class()
        self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES)
        form = self.get_form(form_class)

        if form.is_valid() and self.gallery_images_form.is_valid():
            return self.form_valid(form, self.gallery_images_form)
        else:
            return self.form_invalid(form, self.gallery_images_form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery_images_form'] = self.gallery_images_form

        return kwargs

    def form_valid(self, form, gallery_images_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        organization_id = self.request.session.get('current_company', None)
        form.instance.organization = Organization.objects.get(pk=organization_id)
        form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

        with transaction.atomic():
            domain = form.cleaned_data.get('domain', None)

            if not domain:
                domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), settings.USER_SITES_DOMAIN)

            form.instance.site = Site.objects.create(name='usersites', domain=domain)
            self.object = form.save()
            gallery_images_form.instance = self.object.get_gallery(self.request.user)

            for gallery in gallery_images_form:
                gallery.instance.created_by = self.request.user
                gallery.instance.updated_by = self.request.user

            gallery_images_form.save()

            changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]

        is_logo_changed = 'logo' in form.changed_data
        self.object.upload_images(is_logo_changed, changed_galleries)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, gallery_images_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form)
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['domain'] = settings.USER_SITES_DOMAIN
        template_id = context_data.get('form')['template'].value()

        if template_id:
            context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

        return context_data


class SiteUpdate(UpdateView):
    model = UserSite
    form_class = SiteForm
    template_name = 'UserSites/addForm.html'
    success_url = reverse_lazy('site:main')

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        self.gallery_images_form = GalleryImageFormSet(instance=self.object.get_gallery(self.request.user))
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form, gallery_images_form=self.gallery_images_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES,
                                                       instance=self.object.get_gallery(self.request.user))
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid() and self.gallery_images_form.is_valid():
            return self.form_valid(form, self.gallery_images_form)
        else:
            return self.form_invalid(form, self.gallery_images_form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['gallery_images_form'] = self.gallery_images_form

        return kwargs

    def form_valid(self, form, gallery_images_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user
        root_domain = self.object.root_domain or settings.USER_SITES_DOMAIN

        if form.has_changed() and ('sub_domain' in form.changed_data or 'domain' in form.changed_data):
            form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

        with transaction.atomic():
            self.object = form.save()
            gallery_images_form.instance = self.object.get_gallery(self.request.user)

            for gallery in gallery_images_form:
                gallery.instance.created_by = self.request.user
                gallery.instance.updated_by = self.request.user

            gallery_images_form.save()

            domain = form.cleaned_data.get('domain', None)

            if not domain:
                domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), root_domain)

            site = self.object.site
            site.domain = domain
            site.save()

        changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]
        is_logo_changed = 'logo' in form.changed_data
        self.object.upload_images(is_logo_changed, changed_galleries)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, gallery_images_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form)
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        template_id = context_data.get('form')['template'].value()

        if template_id:
            context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

        if self.object.domain_part == self.object.site.domain:
            context_data['domain'] = settings.USER_SITES_DOMAIN
        else:
            context_data['domain'] = self.object.root_domain

        return context_data

    def get_object(self, queryset=None):
        return self.site
