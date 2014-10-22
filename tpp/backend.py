from haystack.routers import BaseRouter
from tpp.settings import HAYSTACK_CONNECTIONS

__author__ = 'user'
from django.conf import settings
from django.utils import translation
from haystack import connections
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, ElasticsearchSearchQuery, \
    ElasticsearchSearchEngine
from haystack.constants import DEFAULT_ALIAS

def get_using(language, alias=DEFAULT_ALIAS):
    new_using = alias + "_" + language
    using = new_using if new_using in settings.HAYSTACK_CONNECTIONS else alias
    return using

class MultilingualElasticSearchBackend(ElasticsearchSearchBackend):
    def update(self, index, iterable, commit=True, multilingual=True):
        '''
        if multilingual:

            # retrieve unique backend name
            backends = []
            for language, __ in settings.LANGUAGES:
                using = get_using(language, alias=self.connection_alias)
                # Ensure each backend is called only once
                if using in backends:
                    continue
                else:
                    backends.append(using)

                backend = connections[using].get_backend()
                backend.update(index, iterable, commit, multilingual=False)

        else:
            initial_language = translation.get_language()[:2]
            print("[{0}]".format(self.connection_alias))


            if DEFAULT_ALIAS != self.connection_alias:
                language = self.connection_alias[-2:]
                translation.activate(language)

            super(MultilingualElasticSearchBackend, self).update(index, iterable, commit)
            translation.activate(initial_language)
        '''
        languages = [lan[0] for lan in settings.LANGUAGES]

        initial_language = translation.get_language()[:2]
        language = self.connection_alias[-2:]

        print("[{0}]".format(self.connection_alias))

        if language in languages:
            translation.activate(language)

        super(MultilingualElasticSearchBackend, self).update(index, iterable, commit)
        translation.activate(initial_language)


class MultilingualElasticEngine(ElasticsearchSearchEngine):
    backend = MultilingualElasticSearchBackend

class DefaultRouter(BaseRouter):
    def for_read(self, **hints):
        language = translation.get_language()[:2]
        return get_using(language)

    def for_write(self, **hints):
        language = translation.get_language()[:2]
        return get_using(language)