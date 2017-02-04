from urllib.parse import urlparse

from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import gettext as _

from b24online.models import GalleryImage, Gallery, Banner, CURRENCY
from usersites.models import UserSite, UserSiteTemplate, ExternalSiteTemplate, UserSiteSchemeColor

GALLERT_MAX_NUM = 5


class SiteForm(forms.Form):
    pass


class SiteSocialForm(SiteForm):
    facebook = forms.CharField(required=False)
    youtube = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    instagram = forms.CharField(required=False)
    vkontakte = forms.CharField(required=False)
    odnoklassniki = forms.CharField(required=False)


class SiteDomainForm(SiteForm):
    domain = forms.URLField(required=False)
    sub_domain = forms.CharField(required=False)

    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)

    def clean_sub_domain(self):
        sub_domain = self.cleaned_data.get('sub_domain', None)

        if not sub_domain:
            return

        languages = [lan[0] for lan in settings.LANGUAGES]

        if '.' in sub_domain or sub_domain in languages:
            raise ValidationError(_('Enter a valid URL.'))

        root_domain = settings.USER_SITES_DOMAIN

        if self.instance and self.instance.domain_part != self.instance.site.domain:
            root_domain = self.instance.root_domain or root_domain

        full_domain = "%s.%s" % (sub_domain, root_domain)

        validator = validators.URLValidator()
        validator("http://%s" % full_domain)

        queryset = Site.objects.filter(domain=full_domain)

        if self.instance:
            queryset = queryset.exclude(user_site=self.instance.pk)

        if queryset.exists():
            raise ValidationError(_('This domain already taken'))

        return sub_domain

    def clean_domain(self):
        domain = self.cleaned_data.get('domain', None)
        queryset = Site.objects.filter(domain=domain)

        if self.instance:
            queryset = queryset.exclude(user_site=self.instance.pk)

        if queryset.exists():
            raise ValidationError(_('The domain already in use'))

        parsed_uri = urlparse(domain)

        return parsed_uri.netloc

    def clean(self):
        cleaned_data = super().clean()
        sub_domain = cleaned_data.get('sub_domain', None)
        domain = cleaned_data.get('domain', None)

        if not sub_domain and not domain:
            self.add_error('sub_domain', _('Domain is required'))


class SiteGeneralForm(SiteForm):
    slogan = forms.CharField(required=False)
    footer_text = forms.CharField(required=False)
    logo = forms.ImageField(required=True)
    language = forms.ChoiceField(required=False, choices=UserSite.LANG_LIST)
    languages = forms.MultipleChoiceField(required=False,
                                          choices=settings.LANGUAGES, widget=forms.CheckboxSelectMultiple)

    def clean_logo(self):
        logo = self.cleaned_data.get('logo', None)

        if 'logo' not in self.changed_data:
            return logo

        if logo and (logo.image.width > 220 or logo.image.height > 120):
            raise ValidationError(_('Logo exceeded dimension limit'))

        return logo

    def clean(self):
        cleaned_data = super().clean()

        language = cleaned_data.get('language', '')
        languages = cleaned_data.get('languages', [])

        if language != 'auto' and language not in languages:
            self.add_error('language', _('Default language should be included in available languages'))

        return cleaned_data


class SiteDeliveryForm(SiteForm):
    is_delivery_available = forms.BooleanField(required=False)
    delivery_currency = forms.ChoiceField(choices=[(None, '---')] + CURRENCY, required=False)
    delivery_cost = forms.DecimalField(max_digits=15, decimal_places=2, required=False)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('is_delivery_available', False):
            if not cleaned_data.get('delivery_currency', None):
                self.add_error('delivery_currency', _('Delivery is enabled but currency is not set'))

            if not cleaned_data.get('delivery_cost', None):
                self.add_error('delivery_cost', _('Delivery is enabled but delivery cost is not set'))

        return cleaned_data


class SiteCategoryForm(SiteForm):
    template = forms.ModelChoiceField(required=False, queryset=ExternalSiteTemplate.objects.all())


class SiteTemplateForm(SiteForm):
    user_template = forms.ModelChoiceField(required=True, queryset=UserSiteTemplate.objects.all())


class SiteTemplateColorForm(SiteForm):
    def __init__(self, template_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color_template'] = forms.ModelChoiceField(required=True,
                                                               queryset=UserSiteSchemeColor.objects.filter(
                                                                   template_id=template_id)
                                                               )


class SiteGalleryForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    description = forms.CharField(required=True)
    link = forms.URLField(required=True)

    # def clean_image(self):
    #     image_obj = self.cleaned_data.get('image', None)
    #
    #     if 'image' not in self.changed_data:
    #         return image_obj
    #
    #     if image_obj and (image_obj.image.width != 700 or image_obj.image.height != 183):
    #         raise ValidationError(_('Image dimensions not equals required dimension'))
    #
    #     return image_obj

    class Meta:
        model = GalleryImage
        fields = ('image', 'description', 'link')


class SiteBannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ('image', 'block', 'advertisement_ptr', 'link',)

        # def clean(self):
        #    cleaned_data = super().clean()

        #    if 'image' in self.changed_data:
        #        image_obj = cleaned_data.get('image', None)
        #        block = cleaned_data.get('block', None)

        #        if image_obj and block:
        #            if block.width and image_obj.image.width != block.width:
        #                self.add_error('image', _("Image width don't meet the requirements (%s px)" % block.width))
        #            if block.height and image_obj.image.height != block.height:
        #                self.add_error('image', _("Image height don't meet the requirements (%s px)" % block.height))


GalleryImageFormSet = inlineformset_factory(Gallery, GalleryImage,
                                            form=SiteGalleryForm, max_num=GALLERT_MAX_NUM, validate_max=True, extra=5,
                                            fields=('image', 'description', 'link'))
CompanyBannerFormSet = inlineformset_factory(Site, Banner, form=SiteBannerForm,
                                             fields=('image', 'block', 'advertisement_ptr', 'link'),
                                             validate_max=True, max_num=8, extra=8)
ChamberBannerFormSet = inlineformset_factory(Site, Banner, form=SiteBannerForm,
                                             fields=('image', 'block', 'advertisement_ptr', 'link'),
                                             validate_max=True, max_num=8, extra=8)
