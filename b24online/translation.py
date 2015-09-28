from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from b24online.models import Country, Branch, Chamber, Company, Department, Vacancy, BusinessProposalCategory, \
    InnovationProject, B2BProductCategory, B2BProduct, NewsCategory, Greeting, News, Tender, \
    Profile, Exhibition, StaticPage, BusinessProposal, Gallery, Document, AdditionalPage, BannerBlock, Banner


@register(Gallery)
class GalleryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Document)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(AdditionalPage)
class AdditionalPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'slug')


@register(Branch)
class BranchTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(Chamber)
class ChamberTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'short_description', 'keywords', 'director', 'address',)


@register(Company)
class CompanyTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'short_description', 'keywords', 'director', 'address',)


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(Vacancy)
class VacancyTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(BusinessProposalCategory)
class BusinessProposalCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', )


@register(BusinessProposal)
class BusinessProposalCategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'description', 'keywords',)


@register(InnovationProject)
class InnovationProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'keywords', 'product_name', 'business_plan')


@register(B2BProductCategory)
class B2BProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(B2BProduct)
class B2BProductTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'short_description', 'keywords',)


@register(NewsCategory)
class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(Greeting)
class GreetingTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'content', 'position_name', 'organization_name')


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'keywords', 'short_description')


@register(Tender)
class TenderTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'keywords', )


@register(Profile)
class ProfileTranslationOptions(TranslationOptions):
    fields = ('first_name', 'middle_name', 'last_name', 'profession', )


@register(Exhibition)
class ExhibitionTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'description', 'keywords', 'route', 'city', )


@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', )


@register(BannerBlock)
class BannerBlockTranslationOptions(TranslationOptions):
    fields = ('name', 'description', )


@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('title', )


