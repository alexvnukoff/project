from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import serializers

from appl.func import currency_symbol
from b24online.api.fields import DateTimeToDateField
from b24online.models import B2BProduct, InnovationProject, Branch, Exhibition, BusinessProposal, News, Organization, \
    Company, Chamber, VideoChannel
from centerpokupok.models import Coupon
from jobs.models import Requirement, Resume


class B2BProductSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detail_url = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = B2BProduct
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detail_url', 'image')


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Branch


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    detail_url = serializers.CharField(source='get_absolute_url')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if getattr(instance, 'flag_url', None):
            data['flag_url'] = instance.flag_url
        else:
            data['flag'] = instance.country.flag

        return data

    class Meta:
        model = Organization
        fields = ('name', 'detail_url')


class ProjectsSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(required=False, many=True)
    organization = OrganizationSerializer()
    publication_date = DateTimeToDateField(source='created_at')
    detail_url = serializers.CharField(source='get_absolute_url')

    class Meta:
        model = InnovationProject
        fields = ('id', 'name', 'cost', 'currency', 'branches', 'organization', 'detail_url',
                  'cost', 'currency', 'branches', 'publication_date')


class ExhibitionsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    date = DateTimeToDateField(source='created_at')
    flag = serializers.CharField(source='country.flag')
    country_name = serializers.CharField(source='country.name')
    detail_url = serializers.CharField(source='get_absolute_url')

    class Meta:
        model = Exhibition
        fields = ('id', 'city', 'start_date', 'end_date', 'title', 'organization',
                  'date', 'flag', 'country_name', 'detail_url')


class ProposalsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    date = DateTimeToDateField(source='created_at')
    flag = serializers.CharField(source='country.flag')
    country_name = serializers.CharField(source='country.name')
    detail_url = serializers.CharField(source='get_absolute_url')

    class Meta:
        model = BusinessProposal
        fields = ('id', 'title', 'organization', 'date', 'flag', 'country_name', 'detail_url')


class NewsSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    date = DateTimeToDateField(source='created_at')
    detail_url = serializers.CharField(source='get_absolute_url')

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/news.jpg')

    class Meta:
        model = News
        fields = ('id', 'title', 'content', 'organization', 'date', 'flag', 'image', 'detail_url')


class CompanySerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    detail_url = serializers.CharField(source='get_absolute_url')
    site = serializers.CharField()
    fax = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    organization = OrganizationSerializer(source='parent')

    def get_image(self, instance):
        return instance.logo.big if instance.logo else static('b24online/img/company.jpg')

    def get_description(self, instance):
        return instance.short_description or instance.description

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'image', 'flag', 'detail_url',
                  'site', 'fax', 'phone', 'address', 'logo', 'email', 'organization')


class ChamberSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    detail_url = serializers.CharField(source='get_absolute_url')
    site = serializers.CharField()
    fax = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()

    def get_image(self, instance):
        return instance.logo.big if instance.logo else static('b24online/img/company.jpg')

    def get_description(self, instance):
        return instance.short_description or instance.description

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if getattr(instance, 'flag_url', None):
            data['flag_url'] = instance.flag_url
        else:
            data['flag'] = instance.country.flag

        return data

    class Meta:
        model = Chamber
        fields = ('id', 'name', 'description', 'image', 'detail_url',
                  'site', 'fax', 'phone', 'address', 'logo', 'email')


class B2CProductSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detail_url = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = B2BProduct
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detail_url', 'image')


class CouponSerializer(serializers.ModelSerializer):
    flag = serializers.CharField(source='country.flag')
    detail_url = serializers.CharField(source='get_absolute_url')
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    discount_percent = serializers.FloatField(source='coupon_discount_percent')
    end_date = serializers.DateField(source='end_coupon_date')

    def get_image(self, instance):
        return instance.image.big if instance.image else static('b24online/img/item.jpg')

    def get_currency(self, instance):
        return currency_symbol(instance.currency)

    class Meta:
        model = Coupon
        fields = ('id', 'name', 'cost', 'currency', 'flag', 'detail_url', 'image', 'discount_percent', 'end_date')


class VideoSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    image = serializers.SerializerMethodField()
    flag = serializers.CharField(source='country.flag')
    date = DateTimeToDateField(source='created_at')
    detail_url = serializers.CharField(source='get_absolute_url')

    def get_image(self, instance):
        return instance.image.big if instance.image else '//img.youtube.com/vi/%s/0.jpg' % instance.video_code

    class Meta:
        model = VideoChannel
        fields = ('id', 'title', 'content', 'organization', 'date', 'flag', 'image', 'detail_url')


class VacancySerializer(serializers.ModelSerializer):
    detail_url = serializers.CharField(source='get_absolute_url')
    flag = serializers.CharField(source='country.flag')
    country_name = serializers.CharField(source='country.name')
    publication_date = DateTimeToDateField(source='created_at')

    class Meta:
        model = Requirement
        fields = ('id', 'title', 'city', 'description', 'publication_date', 'country_name', 'detail_url', 'flag')




class ResumeSerializer(serializers.ModelSerializer):
    publication_date = DateTimeToDateField(source='created_at')
    full_name = serializers.CharField(source='user.profile.full_name')
    flag = serializers.CharField(source='user.profile.country.flag')

    class Meta:
        model = Resume
        fields = ('id', 'title', 'publication_date', 'flag', 'full_name')
