from urllib.parse import urlparse
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from b24online.models import GalleryImage, Gallery, Banner

from usersites.models import UserSite


class SiteForm(forms.ModelForm):
    domain = forms.URLField(required=False)
    sub_domain = forms.CharField(required=False)
    facebook = forms.CharField(required=False)
    youtube = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    instagram = forms.CharField(required=False)
    vkontakte = forms.CharField(required=False)
    odnoklassniki = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.gallery_images_form = kwargs.pop('gallery_images_form')
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            if self.instance.domain_part == self.instance.site.domain:
                self.initial['domain'] = self.instance.domain_part
            else:
                self.initial['sub_domain'] = self.instance.domain_part

        self.initial['facebook'] = self.instance.facebook
        self.initial['youtube'] = self.instance.youtube
        self.initial['twitter'] = self.instance.twitter
        self.initial['instagram'] = self.instance.instagram
        self.initial['vkontakte'] = self.instance.vkontakte
        self.initial['odnoklassniki'] = self.instance.odnoklassniki

    def clean_sub_domain(self):
        sub_domain = self.cleaned_data.get('sub_domain', None)

        if not sub_domain:
            return

        languages = [lan[0] for lan in settings.LANGUAGES]

        if '.' in sub_domain or sub_domain in languages:
            raise ValidationError(_('Enter a valid URL.'))

        root_domain = settings.USER_SITES_DOMAIN

        if self.instance.pk and self.instance.domain_part != self.instance.site.domain:
            root_domain = self.instance.root_domain or root_domain

        full_domain = "%s.%s" % (sub_domain, root_domain)

        validator = validators.URLValidator()
        validator("http://%s" % full_domain)

        queryset = Site.objects.filter(domain=full_domain)

        if self.instance.pk:
            queryset = queryset.exclude(user_site=self.instance.pk)

        if queryset.exists():
            raise ValidationError(_('This domain already taken'))

        return sub_domain

    def clean_domain(self):
        domain = self.cleaned_data.get('domain', None)
        queryset = Site.objects.filter(domain=domain)

        if self.instance.pk:
            queryset = queryset.exclude(user_site=self.instance.pk)

        if queryset.exists():
            raise ValidationError(_('The domain already in use'))

        parsed_uri = urlparse(domain)

        return parsed_uri.netloc

    def clean_template(self):
        template = self.cleaned_data.get('template', None)

        if not template:
            for gallery_form in self.gallery_images_form:
                if gallery_form['image'].value():
                    return template

            raise ValidationError(_('You should choose a template or provide your own images'))

        return template

    def clean_logo(self):
        logo = self.cleaned_data.get('logo', None)

        if 'logo' not in self.changed_data:
            return logo

        if logo and (logo.image.width > 220 or logo.image.height > 120):
            raise ValidationError(_('Logo exceeded dimension limit'))

        return logo

    def clean(self):
        cleaned_data = super().clean()
        sub_domain = cleaned_data.get('sub_domain', None)
        domain = cleaned_data.get('domain', None)

        if not sub_domain and not domain:
            self.add_error('sub_domain', _('Domain is required'))

    class Meta:
        model = UserSite
        fields = ('slogan', 'template', 'footer_text', 'logo', 'language')


class GalleryForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ('image', 'description', 'link')

   # def clean_image(self):
   #     image_obj = self.cleaned_data.get('image', None)

   #     if 'image' not in self.changed_data:
   #         return image_obj

   #     if image_obj and (image_obj.image.width != 700 or image_obj.image.height != 183):
   #         raise ValidationError(_('Image dimensions not equals required dimension'))

   #     return image_obj


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ('image', 'block', 'advertisement_ptr', 'link',)

    #def clean(self):
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
                                            form=GalleryForm, max_num=5, validate_max=True, extra=5, fields=('image', 'description', 'link'))
CompanyBannerFormSet = inlineformset_factory(Site, Banner, form=BannerForm, fields=('image', 'block', 'advertisement_ptr', 'link'),
                                             validate_max=True, max_num=8, extra=8)
ChamberBannerFormSet = inlineformset_factory(Site, Banner, form=BannerForm, fields=('image', 'block', 'advertisement_ptr', 'link'),
                                             validate_max=True, max_num=8, extra=8)


class TemplateForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('user_template',)
