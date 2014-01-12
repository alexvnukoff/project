__author__ = 'Art'
from haystack import indexes
from appl.models import Company


class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    branches = indexes.MultiValueField(null=True)

    def prepare_branches(self, obj):
        branchQuerySet = obj.getBranches()

        if branchQuerySet is None:
            return None
        else:
            return [branch['pk'] for branch in branchQuerySet.values('pk')]

    def get_model(self):
        return Company