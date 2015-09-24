from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from centerpokupok.models import B2CProduct, B2CProductCategory


@register(B2CProductCategory)
class B2CProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


@register(B2CProduct)
class B2CProductTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'short_description', 'keywords',)
