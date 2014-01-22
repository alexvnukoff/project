__author__ = 'Art'
from haystack import indexes
from appl.models import Company


class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    country = indexes.IntegerField()

    def prepare_country(self, obj):
        return obj.getCountry()

    def get_model(self):
        return Company