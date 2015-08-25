from django.conf import settings
from django.utils import translation
from django.utils.text import slugify
from unidecode import unidecode


def get_index_name(lang=None, index_prefix='b24-'):
    if lang:
        return '%s%s' % (index_prefix, lang)

    if translation.get_language():
        return '%s%s' % (index_prefix, translation.get_language()[0:2])

    return '%s%s' % (index_prefix, settings.MODELTRANSLATION_DEFAULT_LANGUAGE)


def deep_merge_dict(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deep_merge_dict(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]

    return a


def reindex_instance(instance):
    get_index_model = getattr(instance, "get_index_model", None)

    if get_index_model is not None:
        from b24online.search_indexes import SearchEngine
        hits = SearchEngine(doc_type=get_index_model()).query("match", django_id=instance.pk).execute().hits

        if hits.total:
            hits[0].delete()


def create_slug(string):
    """
        Creating url slug from some string using unicode to acii decoder( unidecode library)

        str string - unicode string to convert to slug
        int pk - item pk to append to the slug
    """
    # TODO: Create map for each lang
    string = unidecode(string)

    return slugify(string)
