from django.db.models.signals import post_delete
from django.dispatch import receiver
from elasticsearch_dsl import DocType, analyzer, String, Boolean, Integer, Date, Double, token_filter, Search
from elasticsearch_dsl.connections import connections

from local_settings import ELASTIC_SEARCH_HOSTS

html_strip = analyzer('html_strip',
                      tokenizer="standard",
                      filter=["standard", "lowercase", "stop"],
                      char_filter=["html_strip"]
                      )

autocomplete_filter = token_filter('autocomplete_filter',
                                   type='nGram',
                                   min_gram=3,
                                   max_gram=10
                                   )

autocomplete = analyzer('autocomplete',
                        type='custom',
                        tokenizer="standard",
                        filter=["standard", "lowercase", "lowercase", autocomplete_filter]
                        )


class GreetingIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    organization_name = String(analyzer='snowball')

    @staticmethod
    def get_model():
        from b24online.models import Greeting
        return Greeting

    @classmethod
    def to_index(cls, obj):
        return cls(
            django_id=obj.pk,
            name=obj.name,
            organization_name=obj.organization
        )


class CompanyIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    is_active = Boolean()
    is_deleted = Boolean()
    country = Integer()
    organization = Integer()
    branches = Integer(multi=True)
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import Company
        return Company

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().prefetch_related('countries', 'parent', 'branches')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=obj.name,
            description=obj.description,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            country=obj.countries.all().values_list('pk', flat=True)[0],
            created_at=obj.created_at
        )

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        index_instance.organization = obj.parent.pk if obj.parent else None

        return index_instance


class ExhibitionIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    city = String(analyzer='snowball')
    organization = Integer()
    country = Integer()
    created_at = Date()
    is_active = Boolean()
    is_deleted = Boolean()
    branches = Integer(multi=True)

    @staticmethod
    def get_model():
        from b24online.models import Exhibition
        return Exhibition

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().select_related('country', 'organization').prefetch_related('branches')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            title=obj.title,
            description=obj.description,
            city=obj.city,
            organization=obj.organization.pk,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            country=obj.country.pk,
            created_at=obj.created_at
        )

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class BusinessProposalIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    organization = Integer()
    country = Integer()
    branches = Integer(multi=True)
    bp_categories = Integer(multi=True)
    created_at = Date()
    is_active = Boolean()
    is_deleted = Boolean()

    @staticmethod
    def get_model():
        from b24online.models import BusinessProposal
        return BusinessProposal

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().select_related('country', 'organization') \
            .prefetch_related('branches', 'categories')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            title=obj.title,
            description=obj.description,
            organization=obj.organization.pk,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            country=obj.country.pk,
            created_at=obj.created_at
        )

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        index_instance.bp_categories = list(set([item for category in obj.categories.all()
                                            for item in
                                            category.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class CountryIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from b24online.models import Country
        return Country

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name,
        )

        return index_instance


class NewsCategoryIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from b24online.models import NewsCategory
        return NewsCategory

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name
        )

        return index_instance


class B2bProductCategoryIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from b24online.models import B2BProductCategory
        return B2BProductCategory

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name
        )

        return index_instance


class B2cProductCategoryIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from centerpokupok.models import B2CProductCategory
        return B2CProductCategory

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name
        )

        return index_instance


class BusinessProposalCategoryIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from b24online.models import BusinessProposalCategory
        return BusinessProposalCategory

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name
        )

        return index_instance


class BranchIndex(DocType):
    django_id = Integer()
    name_auto = String(analyzer=autocomplete)

    @staticmethod
    def get_model():
        from b24online.models import Branch
        return Branch

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name_auto=obj.name
        )

        return index_instance


class ChamberIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    name_auto = String(analyzer=autocomplete)
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    countries = Integer(multi=True)
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import Chamber
        return Chamber

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().prefetch_related('countries')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=obj.name,
            name_auto=obj.name,
            description=obj.description,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            created_at=obj.created_at
        )

        if obj.org_type != 'affiliate':
            countries = obj.countries.all().values_list('pk', flat=True)
        else:
            countries = obj.parent.countries.all().values_list('pk', flat=True)

        if not countries:
            raise ValueError('Can not fetch countries from chamber')

        index_instance.countries = list(countries)

        return index_instance


class B2BProductIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    branches = Integer(multi=True)
    b2b_categories = Integer(multi=True)
    organization = Integer()
    price = Double()
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import B2BProduct
        return B2BProduct

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().prefetch_related('company', 'company__countries', 'branches')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=obj.name,
            description=obj.description,
            organization=obj.company.pk,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            country=obj.company.country.pk,
            price=obj.cost,
            created_at=obj.created_at
        )

        index_instance.b2b_categories = list(set([item for category in obj.categories.all()
                                             for item in
                                             category.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class B2cProductIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    b2c_categories = Integer(multi=True)
    organization = Integer()
    price = Double()
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from centerpokupok.models import B2CProduct
        return B2CProduct

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().prefetch_related('company', 'company__countries')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=obj.name,
            description=obj.description,
            organization=obj.company.pk,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            country=obj.company.country.pk,
            price=obj.cost,
            created_at=obj.created_at
        )

        index_instance.b2c_categories = list(set([item for category in obj.categories.all()
                                             for item in
                                             category.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class NewsIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    content = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    news_categories = Integer(multi=True)
    organization = Integer()
    country = Integer()
    is_tv = Boolean()
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import News
        return News

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().prefetch_related('organization', 'organization__countries', 'categories')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            title=obj.title,
            content=obj.content,
            organization=getattr(obj.organization, 'pk', None),
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            is_tv=obj.is_tv,
            created_at=obj.created_at
        )
        country = obj.country if obj.country else getattr(obj.organization, 'country', None)
        index_instance.country = getattr(country, 'pk', None)

        index_instance.news_categories = list(set([item for category in obj.categories.all()
                                              for item in
                                              category.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class TenderIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    content = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    organization = Integer()
    branches = Integer(multi=True)
    start_date = Date()
    end_date = Date()
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import Tender
        return Tender

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().select_related('country', 'organization').prefetch_related('branches')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            title=obj.title,
            content=obj.content,
            organization=obj.organization.pk,
            country=obj.country.pk,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            created_at=obj.created_at
        )

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        if obj.start_date and obj.end_date:
            index_instance.start_date = obj.start_date
            index_instance.end_date = obj.end_date

        return index_instance


class InnovationProjectIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    organization = Integer()
    branches = Integer(multi=True)
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from b24online.models import InnovationProject
        return InnovationProject

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().select_related('created_by', 'created_by__profile') \
            .prefetch_related('branches', 'organization', 'organization__countries')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=obj.name,
            description=obj.description,
            organization=obj.organization.pk if obj.organization else None,
            country=obj.country.pk if obj.country else None,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            created_at=obj.created_at
        )

        index_instance.branches = list(set([item for branch in obj.branches.all()
                                       for item in
                                       branch.get_ancestors(include_self=True).values_list('pk', flat=True)]))

        return index_instance


class ProfileIndex(DocType):
    django_id = Integer()
    email = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    is_active = Boolean()

    @staticmethod
    def get_model():
        from b24online.models import Profile
        return Profile

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all().select_related('country', 'user')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            email=obj.user.email,
            name=obj.full_name,
            is_active=obj.user.is_active
        )

        return index_instance


class ResumeIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    country = Integer()
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from jobs.models import Resume
        return Resume

    @classmethod
    def get_queryset(cls):
        return cls.get_model().objects.all() \
            .select_related('user', 'user__profile', 'user__profile__country')

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            name=getattr(obj.user.profile, 'full_name', None),
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            created_at=obj.created_at
        )

        if obj.user.profile:
            index_instance.country = getattr(obj.user.profile.country, 'pk', None)

        return index_instance


class RequirementIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    country = Integer()
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    is_anonymous = Boolean()
    type_of_employment = String(index='not_analyzed')
    is_active = Boolean()
    is_deleted = Boolean()
    created_at = Date()

    @staticmethod
    def get_model():
        from jobs.models import Requirement
        return Requirement

    @classmethod
    def to_index(cls, obj):
        index_instance = cls(
            django_id=obj.pk,
            title=obj.title,
            country=obj.country.pk,
            description=obj.description,
            is_anonymous=obj.is_anonymous,
            type_of_employment=obj.type_of_employment,
            is_active=obj.is_active,
            is_deleted=obj.is_deleted,
            created_at=obj.created_at
        )

        return index_instance


class SearchEngine(Search):
    _cached_connection = None

    def __init__(self, lang=None, doc_type=None, extra=None, **kwargs):
        from b24online.utils import get_index_name
        index_name = get_index_name(lang)
        using = SearchEngine.get_connection()

        super().__init__(using=using, index=index_name, doc_type=doc_type, extra=extra)

    @staticmethod
    def get_connection():
        if not SearchEngine._cached_connection or not SearchEngine._cached_connection.ping():
            SearchEngine._cached_connection = connections.create_connection(hosts=ELASTIC_SEARCH_HOSTS)

        return SearchEngine._cached_connection


@receiver(post_delete)
def remove_index(sender, instance, **kwargs):
    get_index_model = getattr(instance, "get_index_model", None)

    if get_index_model is not None:
        hits = SearchEngine(doc_type=get_index_model()).query("match", django_id=instance.pk).execute().hits

        if hits.total:
            hits[0].delete()
