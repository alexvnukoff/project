from urllib.parse import urlparse
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from b24online.models import GalleryImage, Gallery, Banner
from usersites.models import UserSite, LandingPage



class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('domain_part',)

    def clean_domain_part(self):
        domain_part = self.cleaned_data.get('domain_part', None)
        if not domain_part:
            return

        languages = [lan[0] for lan in settings.LANGUAGES]
        if '.' in domain_part or domain_part in languages:
            raise ValidationError(_('Enter a valid URL.'))

        root_domain = settings.USER_SITES_DOMAIN
        full_domain = "%s.%s" % (domain_part, root_domain)
        validator = validators.URLValidator()
        validator("http://%s" % full_domain)

        if Site.objects.filter(domain=full_domain).exists():
            raise ValidationError(_('This domain already taken'))
        return domain_part



class DomainForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('slogan',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            if self.instance.domain_part == self.instance.site.domain:
                self.initial['domain'] = self.instance.domain_part
            else:
                self.initial['sub_domain'] = self.instance.domain_part

    domain = forms.URLField(required=False)
    sub_domain = forms.CharField(required=False)

    def clean_sub_domain(self):
        sub_domain = self.cleaned_data.get('sub_domain', None)

        if not sub_domain:
            return

        languages = [lan[0] for lan in settings.LANGUAGES]

        if '.' in sub_domain or sub_domain in languages:
            raise ValidationError(_('Enter a valid URL'))

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

    def clean(self):
        cleaned_data = super().clean()
        sub_domain = cleaned_data.get('sub_domain', None)
        domain = cleaned_data.get('domain', None)

        if not sub_domain and not domain:
            self.add_error('sub_domain', _('Domain is required'))



class LanguagesForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('language', 'languages',)

    languages = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            required=False,
            choices=settings.LANGUAGES
        )



class ProductDeliveryForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('is_delivery_available', 'delivery_currency', 'delivery_cost',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['delivery_currency'].widget.attrs.update({
            'style': 'width:200px;float:none;',
        })



class SiteSloganForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('slogan',)



class FooterTextForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('footer_text',)



class TemplateForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('user_template', 'color_template',)



class LandingForm(forms.ModelForm):
    class Meta:
        model = LandingPage
        fields = ('title', 'description', 'cover')



class SiteLogoForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('logo',)

    def clean_logo(self):
        logo = self.cleaned_data.get('logo', None)
        if 'logo' not in self.changed_data:
            return logo

        if logo and (logo.image.width > 220 or logo.image.height > 120):
            raise ValidationError(_('Logo exceeded dimension limit'))
        return logo



class GalleryForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ('image', 'description', 'link')

GalleryImageFormSet = inlineformset_factory(
        Gallery,
        GalleryImage,
        form=GalleryForm,
        max_num=5,
        validate_max=True,
        extra=5,
        fields=('image', 'description', 'link')
    )



class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ('image', 'block', 'advertisement_ptr', 'link',)

CompanyBannerFormSet = inlineformset_factory(
    Site,
    Banner,
    form=BannerForm,
    fields=('image', 'block', 'advertisement_ptr', 'link'),
    validate_max=True, max_num=24, extra=24)

ChamberBannerFormSet = inlineformset_factory(
    Site,
    Banner,
    form=BannerForm,
    fields=('image', 'block', 'advertisement_ptr', 'link'),
    validate_max=True, max_num=8, extra=8)



class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('id',)

    facebook = forms.CharField(required=False)
    youtube = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    instagram = forms.CharField(required=False)
    vkontakte = forms.CharField(required=False)
    odnoklassniki = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial['facebook'] = self.instance.facebook
        self.initial['youtube'] = self.instance.youtube
        self.initial['twitter'] = self.instance.twitter
        self.initial['instagram'] = self.instance.instagram
        self.initial['vkontakte'] = self.instance.vkontakte
        self.initial['odnoklassniki'] = self.instance.odnoklassniki



class GAnalyticsForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('id',)

    google_analytics = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial['google_analytics'] = self.instance.google_analytics
