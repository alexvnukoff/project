__author__ = 'Art'
from haystack import indexes
from appl.models import Company
from django.conf import Settings


class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Company