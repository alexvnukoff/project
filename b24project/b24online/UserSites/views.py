# -*- encoding: utf-8 -*-
import time
from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from b24online.models import Organization, Company, BannerBlock, Gallery, Banner
from django.utils.translation import ugettext_lazy as _

from b24online.UserSites.forms import (GalleryImageFormSet, SiteCreateForm,
    TemplateForm, LandingForm, CompanyBannerFormSet, ChamberBannerFormSet,
    DomainForm, LanguagesForm, ProductDeliveryForm, SiteSloganForm,
    FooterTextForm, SiteLogoForm, SocialLinksForm, GAnalyticsForm)

from usersites.models import (UserSite, ExternalSiteTemplate,
                UserSiteTemplate, UserSiteSchemeColor, LandingPage)



@login_required()
def form_dispatch(request):
    organization_id = request.session.get('current_company', None)
    if not organization_id:
        return HttpResponseRedirect(reverse('denied'))
    organization = Organization.objects.get(pk=organization_id)

    try:
        site = UserSite.objects.get(organization=organization)
        return UpdateSite.as_view()(request, site=site, organization=organization)
    except ObjectDoesNotExist:
        return CreateSite.as_view()(request, organization=organization)



class SiteDispatch:
    def dispatch(self, request, *args, **kwargs):
        organization_id = request.session.get('current_company', None)
        self.user = request.user
        if not organization_id:
            return HttpResponseRedirect(reverse('denied'))
        self.organization = Organization.objects.get(pk=organization_id)
        try:
            site = UserSite.objects.get(organization=self.organization)
            self.site = site
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('denied'))
        return super().dispatch(request, *args, **kwargs)



class CreateSite(CreateView):
    model = UserSite
    form_class = SiteCreateForm
    template_name = 'b24online/UserSites/createSite.html'
    success_url = reverse_lazy('site:main')

    @method_decorator(login_required)
    def dispatch(self, request, organization, *args, **kwargs):
        self.organization = organization
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['domain'] = settings.USER_SITES_DOMAIN
        context_data['title'] = _("Create Site")
        return context_data

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['domain_part'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        domain_part = form.cleaned_data.get('domain_part', None)
        domain = "{0}.{1}".format(domain_part, settings.USER_SITES_DOMAIN)
        tempate = ExternalSiteTemplate.objects.first()
        user_site = UserSiteTemplate.objects.filter(published=True).first()

        with transaction.atomic():
            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            form.instance.organization = self.organization
            form.instance.template = tempate
            form.instance.user_template = user_site
            form.instance.domain_part = domain_part
            form.instance.logo = self.organization.logo
            form.instance.site = Site.objects.create(
                name='usersites',
                domain=domain)
            self.object = form.save()

        messages.add_message(self.request, messages.SUCCESS, _("Your site has been created!"))
        return HttpResponseRedirect(self.get_success_url())



class UpdateSite(TemplateView):
    template_name = 'b24online/UserSites/updateSite.html'

    @method_decorator(login_required)
    def dispatch(self, request, site, organization, *args, **kwargs):
        self.site = site
        self.organization = organization
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['domain'] = settings.USER_SITES_DOMAIN
        context_data['title'] = _("Update Site")
        context_data['object'] = self.site
        return context_data



class LandingPageView(SiteDispatch, UpdateView):
    model = LandingPage
    form_class = LandingForm
    template_name = 'b24online/UserSites/landingForm.html'
    success_url = reverse_lazy('site:landing_page')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(src=self.site)
        except queryset.model.DoesNotExist:
            obj = queryset.create(src=self.site, created_by=self.user, updated_by=self.user)
            messages.add_message(self.request, messages.SUCCESS, _("Landing page has been created!"))

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Langing Page"
        return context

    def form_valid(self, form):
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS, _("Landing page has been saved!"))
            form.save()

        if 'cover' in form.changed_data:
            self.object.upload_images()
            time.sleep(5)
        return super().form_valid(form)



class UserTemplateView(ListView):
    model = UserSiteTemplate
    template_name = 'b24online/UserSites/templateList.html'

    def dispatch(self, request, *args, **kwargs):
        organization_id = request.session.get('current_company', None)
        if not organization_id:
            return HttpResponseRedirect(reverse('denied'))
        organization = Organization.objects.get(pk=organization_id)
        try:
            site = UserSite.objects.get(organization=organization)
            self.site = site
        except UserSite.DoesNotExist:
            return HttpResponseRedirect(reverse('denied'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Select Template"
        return context

    def get_queryset(self):
        return self.model.objects.filter(published=True)



class TemplateUpdate(UpdateView):
    model = UserSite
    form_class = TemplateForm
    template_name = 'b24online/UserSites/templateForm.html'
    success_url = reverse_lazy('site:main')

    def dispatch(self, request, *args, **kwargs):
        organization_id = request.session.get('current_company', None)
        self.template_id = self.kwargs.get(self.pk_url_kwarg)

        if not organization_id:
            return HttpResponseRedirect(reverse('denied'))
        organization = Organization.objects.get(pk=organization_id)
        try:
            site = UserSite.objects.get(organization=organization)
            self.site = site
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('denied'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            obj = UserSiteTemplate.objects.get(pk=self.template_id)
        except UserSiteTemplate.DoesNotExist:
            raise Http404("No found matching the template in UserSiteTemplate.")

        context['template'] = obj
        context['title'] = "Applying Template"
        context['template_color'] = UserSiteSchemeColor.objects.filter(template=obj)
        return context

    def get_object(self, queryset=None):
        return self.site



class DomainNameView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = DomainForm
    template_name = 'b24online/UserSites/domainForm.html'
    success_url = reverse_lazy('site:main')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['sub_domain'].errors)
        messages.add_message(self.request, messages.ERROR, form['domain'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        domain = form.cleaned_data.get('domain', None)
        sub_domain = form.cleaned_data.get('sub_domain', None)

        form.instance.updated_by = self.request.user
        root_domain = self.object.root_domain or settings.USER_SITES_DOMAIN

        if form.has_changed() and ('sub_domain' in form.changed_data or 'domain' in form.changed_data):
            form.instance.domain_part = domain or sub_domain

            if not domain:
                domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), root_domain)

            self.object = form.save()
            site = self.object.site
            site.domain = domain
            site.save()
            messages.add_message(self.request, messages.SUCCESS, _("Domain Name has been saved!"))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Domain Name"
        return context

    def get_object(self, queryset=None):
        return self.site



class LanguagesView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = LanguagesForm
    template_name = 'b24online/UserSites/languagesForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Site Languages"
        context['user_site_templates'] = UserSiteTemplate.objects.all()
        return context

    def form_valid(self, form):
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS, _("Site Languages has been saved!"))
        return super().form_valid(form)



class ProductDeliveryView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = ProductDeliveryForm
    template_name = 'b24online/UserSites/product_deliveryForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Product Delivery"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['delivery_cost'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS, _("Product Delivery has been saved!"))
        return super().form_valid(form)



class SiteSloganView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = SiteSloganForm
    template_name = 'b24online/UserSites/site_sloganForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Site Slogan"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['slogan'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS, _("Site Slogan has been saved!"))
        return super().form_valid(form)



class FooterTextView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = FooterTextForm
    template_name = 'b24online/UserSites/footer_textForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Footer Text"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['footer_text'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS, _("Footer Text has been saved!"))
        return super().form_valid(form)



class SiteLogoView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = SiteLogoForm
    template_name = 'b24online/UserSites/logoForm.html'
    success_url = reverse_lazy('site:site_logo')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Site Logo"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['logo'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            self.object = form.save()
            self.object.upload_logo(form.cleaned_data)
            messages.add_message(self.request, messages.SUCCESS, _("Site Logo has been saved!"))
            time.sleep(2)
        return super().form_valid(form)



class SliderImagesView(SiteDispatch, UpdateView):
    model = Gallery
    form_class = GalleryImageFormSet
    template_name = 'b24online/UserSites/slider_imagesForm.html'
    success_url = reverse_lazy('site:slider_images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Slider images"
        return context

    def get_object(self, queryset=None):
        usersite = self.site
        model_type = ContentType.objects.get_for_model(usersite)

        obj, _ = Gallery.objects.get_or_create(
        content_type=model_type,
        object_id=usersite.pk,
        defaults={
            'created_by': self.request.user,
            'updated_by': self.request.user
            }
        )

        return obj

    def form_valid(self, form):
        if form.has_changed():
            for i in form:
                i.instance.created_by = self.request.user
                i.instance.updated_by = self.request.user
            form.save()

            self.object.upload_gallery([obj.instance.image.path for obj in form if obj.has_changed()])
            time.sleep(3)
            messages.add_message(self.request, messages.SUCCESS, _("Slider images has been saved!"))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, _("Please fix the errors below"))
        context_data = self.get_context_data(form=form)
        return self.render_to_response(context_data)



class BannersView(SiteDispatch, UpdateView):
    model = Banner
    template_name = 'b24online/UserSites/bannersForm.html'
    success_url = reverse_lazy('site:banners')

    def get_form_class(self):
        if isinstance(self.organization, Company):
            return CompanyBannerFormSet
        else:
            return ChamberBannerFormSet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Banners"
        context['valid_blocks'] = self.get_valid_blocks()
        return context

    def get_object(self, queryset=None):
        return self.site.site

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

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, _("Please fix the errors below"))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.object = self.get_object()
        if form.has_changed():
            for i in form:
                i.instance.created_by = self.request.user
                i.instance.updated_by = self.request.user
                i.instance.dates = (None, None)
            form.save()

            self.site.upload_banners([obj.instance.image.path for obj in form if obj.has_changed()])
            time.sleep(2)
            messages.add_message(self.request, messages.SUCCESS, _("Banners has been saved!"))
        return HttpResponseRedirect(self.get_success_url())



class SocialLinksView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = SocialLinksForm
    template_name = 'b24online/UserSites/social_linksForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Social Links"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, _("Please fix the errors below"))
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            form.instance.updated_by = self.request.user
            messages.add_message(self.request, messages.SUCCESS, _("Social Links has been saved!"))

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

        return super().form_valid(form)



class GAnalyticsView(SiteDispatch, UpdateView):
    model = UserSite
    form_class = GAnalyticsForm
    template_name = 'b24online/UserSites/google_analyticsForm.html'
    success_url = reverse_lazy('site:main')

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Google Analytics"
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, form['google_analytics'].errors)
        return super().render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.has_changed():
            form.instance.updated_by = self.request.user
            messages.add_message(self.request, messages.SUCCESS, _("Google Analytics has been saved!"))

        if 'google_analytics' in form.changed_data:
            form.instance.metadata['google_analytics'] = form.cleaned_data['google_analytics']

        return super().form_valid(form)














# @login_required()
# def form_dispatch(request):
#     organization_id = request.session.get('current_company', None)
#     if not organization_id:
#         return HttpResponseRedirect(reverse('denied'))
#     organization = Organization.objects.get(pk=organization_id)
#     try:
#         site = UserSite.objects.get(organization=organization)
#         return SiteUpdate.as_view()(request, site=site, organization=organization)
#     except ObjectDoesNotExist:
#         return SiteCreate.as_view()(request, organization=organization)

# class SiteCreate(CreateView):
#     model = UserSite
#     form_class = SiteForm
#     template_name = 'b24online/UserSites/addForm.html'
#     success_url = reverse_lazy('site:main')

#     @method_decorator(login_required)
#     def dispatch(self, request, organization, *args, **kwargs):
#         self.organization = organization
#         return super().dispatch(request, *args, **kwargs)

#     def get_valid_blocks(self):
#         valid_blocks = [
#                 "SITES LEFT 1",
#                 "SITES LEFT 2",
#                 "SITES FOOTER",
#                 "SITES RIGHT 1",
#                 "SITES RIGHT 2",
#                 "SITES RIGHT 3",
#                 "SITES RIGHT 4",
#                 "SITES RIGHT 5"
#             ]

#         additional = []
#         for i in range(1,18):
#             additional.append("SITES CAT {0}".format(i))
#         valid_blocks += additional

#         return OrderedDict(BannerBlock.objects.filter(
#             block_type='user_site',
#             code__in=valid_blocks
#             ).order_by('id').values_list('pk', 'name'))

#     def get(self, request, *args, **kwargs):
#         """
#         Handles GET requests and instantiates blank versions of the form
#         and its inline formsets.
#         """
#         self.object = None
#         form_class = self.get_form_class()
#         self.gallery_images_form = GalleryImageFormSet()
#         banners_form = self.get_banners_form()
#         form = self.get_form(form_class)

#         return self.render_to_response(self.get_context_data(form=form,
#                                                              gallery_images_form=self.gallery_images_form,
#                                                              banners_form=banners_form))

#     def post(self, request, *args, **kwargs):
#         """
#             Handles POST requests, instantiating a form instance and its inline
#             formsets with the passed POST variables and then checking them for
#             validity.
#             """
#         self.object = None
#         form_class = self.get_form_class()
#         self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES)
#         banners_form = self.get_banners_form(self.request.POST, self.request.FILES)
#         form = self.get_form(form_class)

#         if form.is_valid() and self.gallery_images_form.is_valid() and banners_form.is_valid():
#             return self.form_valid(form, gallery_images_form=self.gallery_images_form, banners_form=banners_form)
#         else:
#             return self.form_invalid(form, gallery_images_form=self.gallery_images_form, banners_form=banners_form)

#     def get_banners_form(self, *args, **kwargs):
#         if isinstance(self.organization, Company):
#             form = CompanyBannerFormSet(*args, **kwargs)
#         else:
#             form = ChamberBannerFormSet(*args, **kwargs)

#         return form

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['gallery_images_form'] = self.gallery_images_form

#         return kwargs

#     def form_valid(self, form, gallery_images_form, banners_form):
#         """
#         Called if all forms are valid. Creates a Recipe instance along with
#         associated Ingredients and Instructions and then redirects to a
#         success page.
#         """
#         form.instance.created_by = self.request.user
#         form.instance.updated_by = self.request.user
#         form.instance.organization = self.organization
#         form.instance.user_template_id = 1
#         form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

#         with transaction.atomic():
#             domain = form.cleaned_data.get('domain', None)

#             if not domain:
#                 domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), settings.USER_SITES_DOMAIN)

#             form.instance.site = Site.objects.create(name='usersites', domain=domain)
#             self.object = form.save()
#             gallery_images_form.instance = self.object.get_gallery(self.request.user)
#             banners_form.instance = self.object.site

#             for gallery in gallery_images_form:
#                 gallery.instance.created_by = self.request.user
#                 gallery.instance.updated_by = self.request.user

#             gallery_images_form.save()

#             for banner in banners_form:
#                 banner.instance.created_by = self.request.user
#                 banner.instance.updated_by = self.request.user
#                 banner.instance.dates = (None, None)

#             banners_form.save()

#             changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]
#             changed_banners = [obj.instance.image.path for obj in banners_form if obj.has_changed()]

#         is_logo_changed = 'logo' in form.changed_data
#         self.object.upload_images(is_logo_changed, changed_galleries, changed_banners)

#         return HttpResponseRedirect(self.get_success_url())

#     def form_invalid(self, form, gallery_images_form, banners_form):
#         """
#         Called if a form is invalid. Re-renders the context data with the
#         data-filled forms and errors.
#         """
#         context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form,
#                                              banners_form=banners_form)
#         return self.render_to_response(context_data)

#     def get_context_data(self, **kwargs):
#         context_data = super().get_context_data(**kwargs)
#         context_data['domain'] = settings.USER_SITES_DOMAIN
#         context_data['valid_blocks'] = self.get_valid_blocks()
#         context_data['user_site_templates'] = UserSiteTemplate.objects.all()
#         template_id = context_data.get('form')['template'].value()
#         if template_id:
#             context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

#         return context_data























# class SiteUpdate(UpdateView):
#     model = UserSite
#     form_class = SiteForm
#     template_name = 'b24online/UserSites/addForm.html'
#     success_url = reverse_lazy('site:main')

#     @method_decorator(login_required)
#     def dispatch(self, request, site, organization, *args, **kwargs):
#         self.site = site
#         self.organization = organization

#         return super().dispatch(request, *args, **kwargs)

#     def get_valid_blocks(self):
#         valid_blocks = [
#                 "SITES LEFT 1",
#                 "SITES LEFT 2",
#                 "SITES FOOTER",
#                 "SITES RIGHT 1",
#                 "SITES RIGHT 2",
#                 "SITES RIGHT 3",
#                 "SITES RIGHT 4",
#                 "SITES RIGHT 5"
#             ]

#         additional = []
#         for i in range(1,18):
#             additional.append("SITES CAT {0}".format(i))
#         valid_blocks += additional

#         return OrderedDict(BannerBlock.objects.filter(
#             block_type='user_site',
#             code__in=valid_blocks
#             ).order_by('id').values_list('pk', 'name'))

#     def get_banners_form(self, *args, **kwargs):
#         if isinstance(self.organization, Company):
#             return CompanyBannerFormSet(*args, **kwargs)

#         return ChamberBannerFormSet(*args, **kwargs)

#     def get(self, request, *args, **kwargs):
#         """
#         Handles GET requests and instantiates blank versions of the form
#         and its inline formsets.
#         """
#         self.object = self.get_object()
#         self.gallery_images_form = GalleryImageFormSet(instance=self.object.get_gallery(self.request.user))
#         banners_form = self.get_banners_form(instance=self.object.site)
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)

#         return self.render_to_response(self.get_context_data(form=form,
#                                                              gallery_images_form=self.gallery_images_form,
#                                                              banners_form=banners_form))

#     def post(self, request, *args, **kwargs):
#         """
#             Handles POST requests, instantiating a form instance and its inline
#             formsets with the passed POST variables and then checking them for
#             validity.
#             """
#         self.object = self.get_object()
#         self.gallery_images_form = GalleryImageFormSet(self.request.POST, self.request.FILES,
#                                                        instance=self.object.get_gallery(self.request.user))
#         banners_form = self.get_banners_form(self.request.POST, self.request.FILES, instance=self.object.site)
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)

#         if form.is_valid() and self.gallery_images_form.is_valid() and banners_form.is_valid():
#             return self.form_valid(form, self.gallery_images_form, banners_form=banners_form)
#         else:
#             return self.form_invalid(form, self.gallery_images_form, banners_form=banners_form)

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['gallery_images_form'] = self.gallery_images_form

#         return kwargs

#     def form_valid(self, form, gallery_images_form, banners_form):
#         """
#         Called if all forms are valid. Creates a Recipe instance along with
#         associated Ingredients and Instructions and then redirects to a
#         success page.
#         """
#         form.instance.updated_by = self.request.user
#         root_domain = self.object.root_domain or settings.USER_SITES_DOMAIN

#         if form.has_changed() and ('sub_domain' in form.changed_data or 'domain' in form.changed_data):
#             form.instance.domain_part = form.cleaned_data.get('domain', None) or form.cleaned_data.get('sub_domain')

#         if 'facebook' in form.changed_data:
#             form.instance.metadata['facebook'] = form.cleaned_data['facebook']

#         if 'youtube' in form.changed_data:
#             form.instance.metadata['youtube'] = form.cleaned_data['youtube']

#         if 'twitter' in form.changed_data:
#             form.instance.metadata['twitter'] = form.cleaned_data['twitter']

#         if 'instagram' in form.changed_data:
#             form.instance.metadata['instagram'] = form.cleaned_data['instagram']

#         if 'vkontakte' in form.changed_data:
#             form.instance.metadata['vkontakte'] = form.cleaned_data['vkontakte']

#         if 'odnoklassniki' in form.changed_data:
#             form.instance.metadata['odnoklassniki'] = form.cleaned_data['odnoklassniki']

#         if 'google_analytics' in form.changed_data:
#             form.instance.metadata['google_analytics'] = form.cleaned_data['google_analytics']

#         with transaction.atomic():
#             self.object = form.save()
#             gallery_images_form.instance = self.object.get_gallery(self.request.user)

#             for gallery in gallery_images_form:
#                 gallery.instance.created_by = self.request.user
#                 gallery.instance.updated_by = self.request.user

#             gallery_images_form.save()

#             for banner in banners_form:
#                 banner.instance.created_by = self.request.user
#                 banner.instance.updated_by = self.request.user
#                 banner.instance.dates = (None, None)

#             banners_form.save()
#             domain = form.cleaned_data.get('domain', None)

#             if not domain:
#                 domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), root_domain)

#             site = self.object.site
#             site.domain = domain
#             site.save()

#         changed_galleries = [obj.instance.image.path for obj in gallery_images_form if obj.has_changed()]
#         changed_banners = [obj.instance.image.path for obj in banners_form if obj.has_changed()]
#         is_logo_changed = 'logo' in form.changed_data
#         self.object.upload_images(is_logo_changed, changed_galleries, changed_banners)

#         return HttpResponseRedirect(self.get_success_url())

#     def form_invalid(self, form, gallery_images_form, banners_form):
#         """
#         Called if a form is invalid. Re-renders the context data with the
#         data-filled forms and errors.
#         """
#         context_data = self.get_context_data(form=form, gallery_images_form=gallery_images_form, banners_form=banners_form)
#         return self.render_to_response(context_data)

#     def get_context_data(self, **kwargs):
#         context_data = super().get_context_data(**kwargs)
#         context_data['valid_blocks'] = self.get_valid_blocks()
#         template_id = context_data.get('form')['template'].value()
#         context_data['user_site_templates'] = UserSiteTemplate.objects.all()

#         if template_id:
#             context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

#         if self.object.domain_part == self.object.site.domain:
#             context_data['domain'] = settings.USER_SITES_DOMAIN
#         else:
#             context_data['domain'] = self.object.root_domain

#         return context_data

#     def get_object(self, queryset=None):
#         return self.site




