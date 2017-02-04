from collections import OrderedDict
from copy import copy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from formtools_addons import SessionMultipleFormWizardView

from b24online.UserSites.forms import GalleryImageFormSet, CompanyBannerFormSet, ChamberBannerFormSet, \
    SiteDomainForm, SiteGeneralForm, SiteDeliveryForm, SiteSocialForm, SiteCategoryForm, \
    SiteTemplateForm, SiteTemplateColorForm, GALLERT_MAX_NUM
from b24online.models import Organization, Company, BannerBlock
from b24online.utils import ExtendedS3Storage
from usersites.models import UserSite, UserSiteTemplate, ExternalSiteTemplate


def show_color_step(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('template') or {}
    user_template = cleaned_data.get('user_template', None)

    return user_template and user_template.colors.exists()


class PatchedS3Storage(ExtendedS3Storage):
    def delete(self, name):
        # We will handle deletion of temporary files by ourselves
        pass


@login_required()
def form_dispatch(request):
    organization_id = request.session.get('current_company', None)

    if not organization_id:
        return HttpResponseRedirect(reverse('denied'))

    organization = Organization.objects.get(pk=organization_id)
    is_company = isinstance(organization, Company)

    forms = [("domain", SiteDomainForm),
             ("general", SiteGeneralForm),
             ("delivery", SiteDeliveryForm),
             ("social", SiteSocialForm),
             ("category", (('site_category', SiteCategoryForm), ('gallery', GalleryImageFormSet))),
             ("template", SiteTemplateForm),
             ("color", SiteTemplateColorForm),
             ("banners", CompanyBannerFormSet if is_company else ChamberBannerFormSet)
             ]

    try:
        instance = UserSite.objects.get(organization=organization)
        instance_dict = {
            'banners': instance.site,
            'category': {
                'gallery': instance.get_gallery(request.user),
            }
        }
        view = SiteNewCreate.as_view(form_list=forms, instance_dict=instance_dict)
        return view(request, organization=organization, object=instance)
    except ObjectDoesNotExist:
        return SiteNewCreate.as_view(form_list=forms)(request, organization=organization, object=None)


TEMPLATES = {
    "domain": "b24online/UserSites/addDomain.html",
    "general": "b24online/UserSites/addForm.html",
    "delivery": "b24online/UserSites/addDelivery.html",
    "social": "b24online/UserSites/addSocial.html",
    "category": "b24online/UserSites/addCategory.html",
    "template": "b24online/UserSites/addTemplate.html",
    "color": "b24online/UserSites/addTemplateColor.html",
    "banners": "b24online/UserSites/addBanners.html",
}


class SiteNewCreate(SessionMultipleFormWizardView):
    success_url = reverse_lazy('site:main')
    file_storage = PatchedS3Storage()
    condition_dict = {
        'color': show_color_step,
    }

    @method_decorator(login_required)
    def dispatch(self, request, organization, object, *args, **kwargs):
        self.organization = organization
        self.object = object
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        if 'banners' == step:
            return []

        if self.object:
            if 'domain' == step:
                if self.object.domain_part == self.object.site.domain:
                    initial['domain'] = self.object.domain_part
                else:
                    initial['sub_domain'] = self.object.domain_part
            elif 'general' == step:
                initial.update(
                    logo=self.object.logo,
                    slogan=self.object.slogan,
                    footer_text=self.object.footer_text,
                    language=self.object.language,
                    languages=self.object.languages
                )
            elif 'delivery' == step:
                initial.update(
                    is_delivery_available=self.object.is_delivery_available,
                    delivery_currency=self.object.delivery_currency,
                    delivery_cost=self.object.delivery_cost
                )
            elif 'social' == step:
                initial.update(**self.object.metadata)
            elif 'category' == step:
                initial['site_category'] = {
                    'template': self.object.template
                }
            elif 'template' == step:
                initial['user_template'] = self.object.user_template
            elif 'color' == step:
                initial['color_template'] = self.object.color_template

        files = self.storage.get_step_files(step)

        if not self.object and files:
            initial_files = {}

            if step == 'category':
                initial_files = {'gallery': []}

                for i in range(0, GALLERT_MAX_NUM):
                    data = {}
                    file = files.get("category-%s-image" % i, None)

                    if file:
                        data['image'] = file

                    initial_files['gallery'].append(data)
            else:
                for field_name, file in files.items():
                    initial_files[field_name.replace("%s-" % step, "", 1)] = file

            initial.update(**initial_files)

        return initial

    def get_context_data(self, forms, **kwargs):
        context_data = super().get_context_data(forms, **kwargs)
        prefixes = [form.prefix for form in forms]

        if 'domain' in prefixes:
            context_data['domain'] = settings.USER_SITES_DOMAIN

        if 'banners' in prefixes:
            context_data['valid_blocks'] = self.get_valid_blocks()

        if 'category' in prefixes:
            context_data['user_site_templates'] = UserSiteTemplate.objects.all()
            context_data['gallery_images_form'] = forms[1]
            template_id = forms[0]['template'].value()

            if template_id:
                context_data['template'] = ExternalSiteTemplate.objects.get(pk=template_id)

        context_data['form'] = forms[0]

        return context_data

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if 'domain' == step:
            kwargs.update(instance=self.object)

        if 'color' == step:
            kwargs.update(template_id=self.storage.get_step_data('template')['template-user_template'])

        return kwargs

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

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
        for i in range(1, 18):
            additional.append("SITES CAT {0}".format(i))
        valid_blocks += additional

        return OrderedDict(BannerBlock.objects.filter(
            block_type='user_site',
            code__in=valid_blocks
        ).order_by('id').values_list('pk', 'name'))

    def done(self, form_dict, form_list, **kwargs):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """

        for form in form_list:
            if isinstance(form, dict):
                continue

            for name, form_class in self.form_list.items():
                if not isinstance(form_class, dict) and isinstance(form, form_class):
                    form_dict[name] = form

        instance = self.object or UserSite()

        instance.updated_by = self.request.user
        instance.user_template = form_dict['template'].cleaned_data.get('user_template')

        if not instance.pk:
            instance.created_by = self.request.user
            instance.organization = self.organization

        form = form_dict['domain']
        domain = form.cleaned_data.get('domain', None)
        sub_domain = form.cleaned_data.get('sub_domain')
        instance.domain_part = domain or sub_domain

        if not domain:
            domain = "%s.%s" % (form.cleaned_data.get('sub_domain'), settings.USER_SITES_DOMAIN)

        site_kwargs = {'name': 'usersites', 'domain': domain}

        form = form_dict['category']['site_category']
        gallery_images_form = form_dict['category']['gallery']
        instance.template = form.cleaned_data.get('template', None)
        instance.metadata.update(**form_dict['social'].cleaned_data)

        if not instance.template:
            is_image_uploaded = False

            for gallery_form in gallery_images_form:
                if gallery_form.cleaned_data.get('image', None):
                    is_image_uploaded = True
                    break

            if not is_image_uploaded:
                instance.template = ExternalSiteTemplate.objects.first()

        attrs = copy(form_dict['general'].cleaned_data)
        attrs.update(**form_dict['delivery'].cleaned_data)

        for attr, value in attrs.items():
            setattr(instance, attr, value)

        form = form_dict.get('color', None)
        instance.color_template = form and form.cleaned_data.get('color_template')
        banners_form = form_dict['banners']

        with transaction.atomic():
            if instance.pk:
                instance.site.domain = site_kwargs['domain']
                instance.site.save()
            else:
                instance.site = Site.objects.create(**site_kwargs)

            instance.save()

            gallery_images_form.instance = instance.get_gallery(self.request.user)
            banners_form.instance = instance.site

            for gallery in gallery_images_form:
                gallery.instance.created_by = self.request.user
                gallery.instance.updated_by = self.request.user

            gallery_images_form.save()

            for banner in banners_form:
                banner.instance.created_by = self.request.user
                banner.instance.updated_by = self.request.user
                banner.instance.dates = (None, None)

            banners_form.save()
            params = {'gallery': [], 'banners': []}

            for form in gallery_images_form:
                if 'image' not in form.changed_data:
                    continue

                params['gallery'].append({
                    'path': form.cleaned_data['image'].file.key_name,
                    'file': form.instance.image.path,
                    's3file': True
                })

            for form in banners_form:
                if 'image' not in form.changed_data:
                    continue

                params['banners'].append({
                    'path': form.cleaned_data['image'].file.key_name,
                    'file': form.instance.image.path,
                    's3file': True
                })

            if 'logo' in form_dict['general'].changed_data:
                params['logo'] = {
                    'path': form_dict['general'].cleaned_data['logo'].file.key_name,
                    'file': instance.logo.path,
                    's3file': True
                }

        instance.upload_images(**params)

        return HttpResponseRedirect(self.success_url)
