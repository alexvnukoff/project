from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import serializers

from appl.func import currency_symbol
from b24online.api.fields import DateTimeToDateField
from b24online.models import B2BProduct, InnovationProject, Branch, Exhibition, BusinessProposal, News, Organization, \
    Company, Chamber, VideoChannel, Banner
from centerpokupok.models import Coupon
from jobs.models import Requirement, Resume
from django.core.urlresolvers import reverse


class B2BProductSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detailUrl = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        extra_options = getattr(instance, 'get_contextmenu_options', None)

        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('products:update', args=[instance.pk]),
                'removeUrl': reverse('products:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
                'extraOptions': dict(zip(['url', 'title'], extra_options))
            }

        return None

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = B2BProduct
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detailUrl', 'image', 'contextMenu')


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Branch


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    detailUrl = serializers.CharField(source='get_absolute_url')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if getattr(instance, 'flag_url', None):
            data['flag_url'] = instance.flag_url
        else:
            data['flag'] = instance.country.flag

        return data

    class Meta:
        model = Organization
        fields = ('id', 'name', 'detailUrl')


class ProjectsSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(required=False, many=True)
    organization = OrganizationSerializer()
    publicationDate = DateTimeToDateField(source='created_at')
    detailUrl = serializers.CharField(source='get_absolute_url')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('innov:update', args=[instance.pk]),
                'removeUrl': reverse('innov:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    class Meta:
        model = InnovationProject
        fields = ('id', 'name', 'cost', 'currency', 'branches', 'organization', 'detailUrl',
                  'cost', 'currency', 'branches', 'publicationDate', 'contextMenu')


class ExhibitionsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    startDate = serializers.DateField()
    endDate = serializers.DateField()
    date = DateTimeToDateField(source='created_at')
    flag = serializers.CharField(source='country.flag')
    countryName = serializers.CharField(source='country.name')
    detailUrl = serializers.CharField(source='get_absolute_url')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('exhibitions:update', args=[instance.pk]),
                'removeUrl': reverse('exhibitions:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    class Meta:
        model = Exhibition
        fields = ('id', 'city', 'startDate', 'endDate', 'title', 'organization',
                  'date', 'flag', 'countryName', 'detailUrl', 'contextMenu')


class ProposalsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    date = DateTimeToDateField(source='created_at')
    flag = serializers.CharField(source='country.flag')
    countryName = serializers.CharField(source='country.name')
    detailUrl = serializers.CharField(source='get_absolute_url')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('proposal:update', args=[instance.pk]),
                'removeUrl': reverse('proposal:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    class Meta:
        model = BusinessProposal
        fields = ('id', 'title', 'organization', 'date', 'flag', 'countryName', 'detailUrl', 'contextMenu')


class NewsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    date = DateTimeToDateField(source='created_at')
    detailUrl = serializers.CharField(source='get_absolute_url')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('news:update', args=[instance.pk]),
                'removeUrl': reverse('news:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/news.jpg')

    class Meta:
        model = News
        fields = ('id', 'title', 'content', 'organization',
                  'date', 'flag', 'image', 'detailUrl', 'contextMenu')


class CompanySerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    detailUrl = serializers.CharField(source='get_absolute_url')
    site = serializers.CharField()
    fax = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    organization = OrganizationSerializer(source='parent')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')
    contactLink = serializers.SerializerMethodField(method_name='get_contact_link')

    def get_contact_link(self, instance):
        return reverse('messages:send_message_to_recipient', args=['organization', instance.pk])

    def get_context_menu(self, instance):
        if not instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('companies:update', args=[instance.pk]),
                'removeUrl': reverse('companies:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
                'setCurrentUrl': reverse('setCurrent', args=[instance.pk]),
            }

        return None

    def get_image(self, instance):
        return instance.logo.big if instance.logo else static('b24online/img/company.jpg')

    def get_description(self, instance):
        return instance.short_description or instance.description

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'image', 'flag', 'detailUrl', 'contextMenu',
                  'site', 'fax', 'phone', 'address', 'logo', 'email', 'organization', 'contactLink')


class ChamberSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    detailUrl = serializers.CharField(source='get_absolute_url')
    site = serializers.CharField()
    fax = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    contactLink = serializers.SerializerMethodField(method_name='get_contact_link')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('tpp:update', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
                'setCurrentUrl': reverse('setCurrent', args=[instance.pk]),
            }

        return None

    def get_image(self, instance):
        return instance.logo.big if instance.logo else static('b24online/img/company.jpg')

    def get_description(self, instance):
        return instance.short_description or instance.description

    def get_contact_link(self, instance):
        return reverse('messages:send_message_to_recipient', args=['organization', instance.pk])

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if getattr(instance, 'flag_url', None):
            data['flag_url'] = instance.flag_url
        else:
            data['flag'] = instance.country.flag

        return data

    class Meta:
        model = Chamber
        fields = ('id', 'name', 'description', 'image', 'detailUrl', 'contactLink',
                  'site', 'fax', 'phone', 'address', 'logo', 'email', 'contextMenu')


class B2CProductSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detailUrl = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('products:updateB2C', args=[instance.pk]),
                'removeUrl': reverse('products:deleteB2C', args=[instance.pk])
            }

        return None

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = B2BProduct
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detailUrl', 'image', 'contextMenu')


class CouponSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detailUrl = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    discountPercent = serializers.FloatField(source='coupon_discount_percent')
    endDate = serializers.DateField(source='end_coupon_date')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('products:updateB2C', args=[instance.pk]),
                'removeUrl': reverse('products:deleteB2C', args=[instance.pk]),
            }

        return None

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = Coupon
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detailUrl',
                  'image', 'discountPercent', 'endDate', 'contextMenu')


class VideoSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    date = DateTimeToDateField(source='created_at')
    detailUrl = serializers.CharField(source='get_absolute_url')
    videoCode = serializers.CharField(source='video_code')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('tv:update', args=[instance.pk]),
                'removeUrl': reverse('tv:delete', args=[instance.pk]),
            }

        return None

    def get_image(self, instance):
        return instance.image.big if instance.image else '//img.youtube.com/vi/%s/0.jpg' % instance.video_code

    class Meta:
        model = VideoChannel
        fields = ('id', 'title', 'content', 'organization', 'date',
                  'flag', 'image', 'detailUrl', 'contextMenu')


class VacancySerializer(serializers.ModelSerializer):
    detailUrl = serializers.CharField(source='get_absolute_url')
    flag = serializers.CharField(source='country.flag')
    countryName = serializers.CharField(source='country.name')
    date = DateTimeToDateField(source='created_at')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('vacancy:update', args=[instance.pk]),
                'removeUrl': reverse('vacancy:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    class Meta:
        model = Requirement
        fields = ('id', 'title', 'city', 'description', 'date',
                  'countryName', 'detailUrl', 'flag', 'contextMenu')


class ResumeSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='user.profile.full_name')
    flag = serializers.CharField(source='user.profile.country.flag')
    date = DateTimeToDateField(source='created_at')
    detailUrl = serializers.CharField(source='get_absolute_url')
    contextMenu = serializers.SerializerMethodField(method_name='get_context_menu')

    def get_context_menu(self, instance):
        if instance.has_perm(self.context['request'].user):
            return {
                'editUrl': reverse('resume:update', args=[instance.pk]),
                'removeUrl': reverse('resume:delete', args=[instance.pk]),
                'advertiseUrl': reverse('adv_top:top_form', args=[self.Meta.model.__name__.lower(), instance.pk]),
            }

        return None

    class Meta:
        model = Resume
        fields = ('id', 'title', 'date', 'flag', 'fullName', 'detailUrl', 'contextMenu')


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='image.big')
    block = serializers.CharField(source='block.name')

    class Meta:
        model = Banner
        fields = ('id', 'title', 'link', 'image', 'block')


class ContextAdvertisementSerializer(serializers.Serializer):
    title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_title(self, instance):
        return getattr(instance, 'title', '') or getattr(instance, 'name', '')

    def get_image(self, instance):
        image = getattr(instance, 'image', None) or getattr(instance, 'logo', None)

        return image.small if image else None

    def get_description(self, instance):
        return getattr(instance, 'description', '') or getattr(instance, 'content', '')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if getattr(instance, 'flag_url', None):
            data['flag_url'] = instance.flag_url
        elif getattr(instance, 'country', None):
            data['flag'] = instance.country.flag
        elif getattr(instance, 'organization', None) and getattr(instance.organization, 'flag', None):
            data['flag_url'] = instance.organization.flag_url

        return data

    class Meta:
        fields = ('title', 'id', 'image', 'description')
