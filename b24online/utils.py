from django.conf import settings
from django.utils import translation


def get_index_name(lang=None):
    index_prefix = 'b24-'

    if lang:
        return '%s%s' % (index_prefix, lang)

    if translation.get_language():
        return '%s%s' % (index_prefix, translation.get_language()[0:2])

    return '%s%s' % (index_prefix, settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
