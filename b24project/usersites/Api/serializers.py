from django.utils.text import Truncator
from lxml.html.clean import clean_html
from rest_framework import serializers

from appl.func import currency_symbol


class ListNewsSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):

        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.content).words("30", html=True)

        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'cover': obj.image.big if obj.image else '',
            'shortText': clean_html(short_text) if short_text else '',
        }


class DetailNewsSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'cover': obj.image.big if obj.image else '',
            'fullText': clean_html(obj.content) if obj.content else '',
        }


class ListBusinessProposalSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'shortText': clean_html(Truncator(obj.description).words("30", html=True)) if obj.description else '',
        }


class DetailBusinessProposalSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'fullText': clean_html(obj.description) if obj.description else '',
        }


class GallerySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'url': obj.image.original,
            'description': '',
        }


class DepartmentSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'unit': clean_html(obj.name),
            'workers': VacancySerializer(obj.vacancies.all(), many=True).data,
        }


class VacancySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'img': obj.user.profile.avatar.th if obj.user and obj.user.profile.avatar else '',
            'name': clean_html(obj.user.profile.full_name) if obj.user and obj.user.profile.full_name else '',
            'post': clean_html(obj.name) if obj.name else '',
            'phone': clean_html(obj.user.profile.mobile_number) if obj.user and obj.user.profile.mobile_number else ''
        }


class ListB2BProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.description).words("30", html=True)

        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(short_text) if short_text else ''
        }


class DetaiB2BlProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(obj.description) if obj.description else ''
        }


class ListB2CProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.description).words("30", html=True)

        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(short_text) if short_text else ''
        }


class DetaiB2ClProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(obj.description) if obj.description else ''
        }


class B2CProductCategorySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'parentId': obj.parent_id,
        }


class B2BProductCategorySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'parentId': obj.parent_id,
        }
