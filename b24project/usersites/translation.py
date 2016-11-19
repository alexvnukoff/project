 # -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from usersites.models import ExternalSiteTemplate, UserSite, UserSiteTemplate


@register(ExternalSiteTemplate)
class ExternalSiteTemplateTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(UserSite)
class UserSiteTranslationOptions(TranslationOptions):
    fields = ('slogan', 'footer_text',)


@register(UserSiteTemplate)
class UserSiteTemplateTranslationOptions(TranslationOptions):
    fields = ('description', )
