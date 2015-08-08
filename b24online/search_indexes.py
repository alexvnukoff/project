from elasticsearch_dsl import DocType, String, analyzer, Completion, Index, Boolean, Integer, Date, Double
from elasticsearch_dsl.connections import connections
from django.utils import translation

# Define a default Elasticsearch client
from local_settings import ELASTIC_SEARCH_HOSTS
from django.conf import settings

connections.create_connection(hosts=ELASTIC_SEARCH_HOSTS)

html_strip = analyzer('html_strip',
                      tokenizer="standard",
                      filter=["standard", "lowercase", "stop"],
                      char_filter=["html_strip"]
                      )

autocomplete = analyzer('autocomplete',
                        tokenizer="standard",
                        filter=["standard", "lowercase", "stop"]
                        )

index_name = 'b24-%s' % (translation.get_language() or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
index = Index(index_name)


@index.doc_type
class GreetingIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    organization = String(analyzer='snowball')
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class CompanyIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    is_active = Boolean()
    country = Integer()
    tpp = Integer(multi=True)
    branch = Integer(multi=True)

    class Meta:
        index = index_name


@index.doc_type
class ExhibitionProposalIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    city = String(analyzer='snowball')
    tpp = Integer()
    country = Integer()
    company = Integer()
    branch = Integer(multi=True)
    created_at = Date()

    class Meta:
        index = index_name


@index.doc_type
class BusinessProposalIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    tpp = Integer()
    country = Integer()
    company = Integer()
    branch = Integer(multi=True)
    bp_category = Integer(multi=True)
    created_by = Integer()
    created_at = Date()

    class Meta:
        index = index_name


@index.doc_type
class CountryIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title_auto = Completion(analyzer=autocomplete)

    class Meta:
        index = index_name


@index.doc_type
class CategoryIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title_auto = Completion(analyzer=autocomplete)
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class BranchIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title_auto = Completion(analyzer=autocomplete)
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class BusinessProposalCategoryIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title_auto = Completion(analyzer=autocomplete)
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class ChamberIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title_auto = Completion(analyzer=autocomplete)
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer(multi=True)
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class ProductIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    branch = Integer(multi=True)
    category = Integer(multi=True)
    tpp = Integer()
    company = Integer()
    price = Double()
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class NewsIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    branch = Integer(multi=True)
    category = Integer(multi=True)
    tpp = Integer()
    country = Integer()
    company = Integer()
    price = Double()
    is_tv = Boolean()
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class TenderIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    tpp = Integer()
    company = Integer()
    branch = Integer(multi=True)
    start_event_date = Date()
    end_event_date = Date()
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class InnovationProjectIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    country = Integer()
    tpp = Integer()
    company = Integer()
    branch = Integer(multi=True)
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class ProfileIndex(DocType):
    django_id = Integer()
    email = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    is_active = Boolean()

    class Meta:
        index = index_name


@index.doc_type
class ResumeIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    country = Integer()

    class Meta:
        index = index_name


@index.doc_type
class ResumeIndex(DocType):
    django_id = Integer()
    name = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    country = Integer()

    class Meta:
        index = index_name


@index.doc_type
class RequirementIndex(DocType):
    django_id = Integer()
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    country = Integer()
    description = String(analyzer=html_strip, fields={'raw': String(index='not_analyzed')})
    is_anonymous = Boolean()
    type_of_employment = String(index='not_analyzed')

    class Meta:
        index = index_name
