from math import ceil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import activate, deactivate
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index, DocType

from b24online.search_indexes import SearchEngine
from b24online.utils import get_index_name

a = {}
activate('en')
for d in organization.departments.all():
    a[d.id] = d.name

deactivate()

for d in organization.departments.all():
    d.name = a[d.id]
    d.save()



class Command(BaseCommand):

    def handle(self, *args, **options):
        languages = [lan[0] for lan in settings.LANGUAGES]
        conn = SearchEngine.get_connection()

        # TODO find another way to get all index models
        index_models = [model for model in DocType.__subclasses__() if model.__module__ == 'b24online.search_indexes']
        index = Index('b24')

        for index_model in index_models:
            index.doc_type(index_model)

        index_data = index.to_dict()

        bulk_size = 2000
       
        for lang in languages:
            activate(lang)
            index_name = get_index_name(lang)
            conn.indices.delete(index=index_name, ignore=404)
            conn.indices.create(index=index_name, body=index_data)

            for index_model in index_models:
                queryset = getattr(index_model, 'get_queryset', index_model.get_model().objects.all)()
                count = queryset.count()
                loop_times = ceil(count / bulk_size)
                start_size = 0

                for _ in range(loop_times):
                    end_size = start_size + bulk_size if (start_size + bulk_size) <= count else count
                    objects = [index_model.to_index(obj) for obj in queryset[start_size:end_size]]
                    actions = []

                    for d in objects:
                        actions.append({
                            '_index': index_name,
                            '_type': d._doc_type.name,
                            '_source': d.to_dict()
                        })

                    bulk(conn, actions)
                    start_size = end_size
            deactivate()
