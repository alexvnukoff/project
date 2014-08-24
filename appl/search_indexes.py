from django.utils.timezone import now, get_current_timezone

from appl import func


__author__ = 'Art'
from haystack import indexes
from appl.models import Company, Country, Tpp, News, Product, Category, Branch, NewsCategories, \
    BusinessProposal, Exhibition, Tender, InnovationProject, Cabinet, TppTV, Department, Vacancy, Resume, Requirement, Organization, \
    BpCategories, Greeting
from core.models import Relationship
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import datetime

class SearchIndexActive(indexes.SearchIndex):
    def index_queryset(self, using=None):
        return self.get_model().active.get_active()

class GreetignsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    tpp_name = indexes.CharField(null=True)
    image = indexes.CharField(null=True, indexed=False)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField(null=True)

    slug = indexes.CharField(indexed=False)
    position = indexes.CharField(indexed=False, null=True)

    title_sort = indexes.CharField(null=True, indexed=False, faceted=True, stored=True)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return Greeting

    def prepare_obj_start_date(self, obj):
        return obj.start_date

    def prepare_obj_end_date(self, obj):
        return obj.end_date

    def prepare(self, obj):
        self.prepared_data = super(GreetignsIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'position': 'POSITION',
            'tpp': 'TPP',
            'image': 'IMAGE'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        return self.prepared_data

################## Exhibition Index #############################
class ExhibitionProposalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    tpp = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    branch = indexes.MultiValueField(null=True)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    start_event_date = indexes.DateField(null=True)
    end_event_date = indexes.DateField(null=True)
    obj_create_date = indexes.DateTimeField(null=True)

    slug = indexes.CharField(indexed=False)
    city = indexes.CharField(indexed=False, null=True)
    position = indexes.CharField(indexed=False, null=True)
    route_description = indexes.CharField(indexed=False, null=True)
    doc_1 = indexes.CharField(null=True, indexed=False)
    doc_2 = indexes.CharField(null=True, indexed=False)
    doc_3 = indexes.CharField(null=True, indexed=False)


    title_sort = indexes.CharField(null=True, indexed=False, faceted=True, stored=True)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return Exhibition

    def prepare(self, obj):
        self.prepared_data = super(ExhibitionProposalIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'start_event_date': 'START_EVENT_DATE',
            'end_event_date': 'END_EVENT_DATE',
            'slug': 'SLUG',
            'city': 'CITY',
            'position': 'POSITION',
            'route_description': 'ROUTE_DESCRIPTION',
            'doc_1': 'DOCUMENT_1',
            'doc_2': 'DOCUMENT_2',
            'doc_3': 'DOCUMENT_3'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if field_name == 'start_event_date' or field_name == 'end_event_date':
                    self.prepared_data[field.index_fieldname] = datetime.strptime(attributes[attr][0], "%m/%d/%Y")
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()


        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        timezoneInfo = get_current_timezone()

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)
            
        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:
            
            if parentRelEnd > obj.end_date:
                self.prepared_data[endDateIndex] = obj.end_date
            else:
                self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date            

        #country
        countryIndex = self.fields['country'].index_fieldname

        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        comp = Company.objects.filter(p2c__child=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child=obj.pk).pk
        except ObjectDoesNotExist:
            pass


        if comp.exists():
            comp = comp[0]

            self.prepared_data[companyIndex] = comp.pk

            if not self.prepared_data[countryIndex]:
                self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type='dependence').pk

            try:
                self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child=obj.pk, p2c__type="relation").pk
            except ObjectDoesNotExist:
                self.prepared_data[tppIndexfield] = 0

        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[companyIndex] = 0
            self.prepared_data[tppIndexfield] = tpp.pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='dependence')

                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk


        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

################## Business Proposal Index #############################

class BusinessProposalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    tpp = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    branch = indexes.MultiValueField(null=True)
    bp_category = indexes.IntegerField(null=True)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField(null=True)


    title_sort = indexes.CharField(null=True, indexed=False, faceted=True, stored=True)
    slug = indexes.CharField(null=False, indexed=False)
    doc_1 = indexes.CharField(null=True, indexed=False)
    doc_2 = indexes.CharField(null=True, indexed=False)
    doc_3 = indexes.CharField(null=True, indexed=False)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return BusinessProposal

    def prepare(self, obj):
        self.prepared_data = super(BusinessProposalIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'doc_1': 'DOCUMENT_1',
            'doc_2': 'DOCUMENT_2',
            'doc_3': 'DOCUMENT_3'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        bp_categoryIndex = self.fields['bp_category'].index_fieldname
        cat = BpCategories.objects.filter(p2c__child=obj.pk)

        if cat.exists():

            cat = cat[0]
            self.prepared_data[bp_categoryIndex] = cat.pk
        else:
            self.prepared_data[bp_categoryIndex] = 0



        comp = Company.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")

        if comp.exists():
            comp = comp[0]

            self.prepared_data[companyIndex] = comp.pk

            if not self.prepared_data[countryIndex]:
                self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type='dependence').pk

            try:
                self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child=obj.pk, p2c__type="relation").pk
            except ObjectDoesNotExist:
                self.prepared_data[tppIndexfield] = 0

        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[companyIndex] = 0
            self.prepared_data[tppIndexfield] = tpp.pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='dependence')

                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk

        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

################## Countries  Index #############################

class CountryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)

    title_sort = indexes.CharField(indexed=False, faceted=True)
    
    title_auto = indexes.NgramField()
    flag = indexes.CharField(indexed=False)

    def get_model(self):
        return Country

    def prepare(self, obj):

        self.prepared_data = super(CountryIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME', 'COUNTRY_FLAG')

        if len(attr) == 0 or attr.get('NAME', [''])[0] == '':
            return self.prepared_data
        else:
            name = attr.get('NAME', [''])[0]

        if len(attr) == 0 or attr.get('COUNTRY_FLAG', [''])[0] == '':
            return self.prepared_data
        else:
            flag = attr.get('COUNTRY_FLAG', [''])[0]


        flagIndex = self.fields['flag'].index_fieldname
        self.prepared_data[flagIndex] = flag

        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname

        self.prepared_data[sortIndex] = name.lower().strip().replace(' ','_')
        self.prepared_data[textIndex] = name.strip()
        self.prepared_data[titleAutoIndex] = name.strip()

        return self.prepared_data


########################## Category Index #############################

class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    
    title_auto = indexes.NgramField()
    slug = indexes.CharField(indexed=False)

    def get_model(self):
        return Category

    def prepare(self, obj):
        self.prepared_data = super(CategoryIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME', 'SLUG')

        if len(attr) == 0 or attr.get('NAME', [''])[0] == '':
            return self.prepared_data
        else:
            name = attr.get('NAME', [''])[0]

        if len(attr) == 0 or attr.get('SLUG', [''])[0] == '':
            return self.prepared_data
        else:
            slug = attr.get('SLUG', [''])[0]

        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname
        slugIndex = self.fields['slug'].index_fieldname

        self.prepared_data[sortIndex] = name.lower().strip().replace(' ','_')
        self.prepared_data[textIndex] = name.strip()
        self.prepared_data[titleAutoIndex] = name.strip()
        self.prepared_data[slugIndex] = slug.strip()

        return self.prepared_data

########################## Branches Index #############################

class BranchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    
    title_auto = indexes.NgramField()

    def get_model(self):
        return Branch

    def prepare(self, obj):
        self.prepared_data = super(BranchIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME')

        if len(attr) == 0 or attr[0].strip() == '':
            return self.prepared_data
        else:
            name = attr[0].strip()

        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname

        self.prepared_data[sortIndex] = name.lower().replace(' ','_')
        self.prepared_data[textIndex] = name
        self.prepared_data[titleAutoIndex] = name

        return self.prepared_data

########################## BpCategories Index #############################

class BpCategoriesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    
    title_auto = indexes.NgramField()
    slug = indexes.CharField(indexed=False)


    def get_model(self):
        return BpCategories

    def prepare(self, obj):
        self.prepared_data = super(BpCategoriesIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME', 'SLUG')

        if len(attr) == 0 or attr.get('NAME', [''])[0] == '':
            return self.prepared_data
        else:
            name = attr.get('NAME', [''])[0]

        if len(attr) == 0 or attr.get('SLUG', [''])[0] == '':
            return self.prepared_data
        else:
            slug = attr.get('SLUG', [''])[0]

        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname
        slugIndex = self.fields['slug'].index_fieldname

        self.prepared_data[sortIndex] = name.lower().strip().replace(' ','_')
        self.prepared_data[textIndex] = name.strip()
        self.prepared_data[titleAutoIndex] = name.strip()
        self.prepared_data[slugIndex] = slug.strip()

        return self.prepared_data

########################## Company Index #############################

class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    anons = indexes.CharField(null=True)
    title = indexes.CharField()
    branch = indexes.MultiValueField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    title_auto = indexes.NgramField(null=True)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField()
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    slug = indexes.CharField(indexed=False)
    image = indexes.CharField(indexed=False, null=True)
    email = indexes.CharField(indexed=False, null=True)
    site = indexes.CharField(indexed=False, null=True)
    address = indexes.CharField(indexed=False, null=True)
    phone = indexes.CharField(indexed=False, null=True)
    fax = indexes.CharField(indexed=False, null=True)
    position = indexes.CharField(indexed=False, null=True)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):
        self.prepared_data = super(CompanyIndex, self).prepare(obj)


        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'title_auto': 'NAME',
            'slug': 'SLUG',
            'image': 'IMAGE',
            'email': 'EMAIL',
            'site': 'SITE_NAME',
            'address': 'ADDRESS',
            'phone': 'TELEPHONE_NUMBER',
            'fax': 'FAX',
            'anons': 'ANONS',
            'position': 'POSITION'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None


        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        return self.prepared_data

    def prepare_tpp(self, object):
        try:
            return Tpp.objects.get(p2c__child_id=object.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            return None

    def prepare_branch(self, object):
        try:
            branches = Branch.objects.filter(p2c__child_id=object.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def prepare_country(self, object):
        try:
            return Country.objects.get(p2c__child_id=object.pk, p2c__type='dependence').pk
        except ObjectDoesNotExist:
            return None        

    def get_model(self):
        return Company

########################## Tpp Index #############################

class TppIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    anons = indexes.CharField(null=True)
    title = indexes.CharField()
    country = indexes.MultiValueField(null=True)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField()

    title_auto = indexes.NgramField()
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    slug = indexes.CharField(indexed=False)
    image = indexes.CharField(indexed=False, null=True)
    email = indexes.CharField(indexed=False, null=True)
    site = indexes.CharField(indexed=False, null=True)
    address = indexes.CharField(indexed=False, null=True)
    phone = indexes.CharField(indexed=False, null=True)
    fax = indexes.CharField(indexed=False, null=True)
    flag = indexes.CharField(indexed=False, null=True)
    position = indexes.CharField(indexed=False, null=True)



    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):
        self.prepared_data = super(TppIndex, self).prepare(obj)


        field_to_attr = {
            'title': 'NAME',
            'title_auto': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'image': 'IMAGE',
            'email': 'EMAIL',
            'site': 'SITE_NAME',
            'address': 'ADDRESS',
            'phone': 'TELEPHONE_NUMBER',
            'fax': 'FAX',
            'flag': 'FLAG',
            'position': 'POSITION',
            'anons': 'ANONS'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        return self.prepared_data

    def prepare_country(self, obj):
        try:
            return list(Country.objects.filter(p2c__child_id=obj.pk).values_list('pk', flat=True))
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return Tpp

########################## Products Index #############################

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    branch = indexes.MultiValueField(null=True)
    categories = indexes.MultiValueField(null=True)
    discount = indexes.FloatField(null=True)
    coupon = indexes.FloatField(null=True)
    coupon_start = indexes.DateTimeField(null=True)
    coupon_end = indexes.DateTimeField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)

    price = indexes.FloatField(null=True)
    currency = indexes.CharField(null=True)
    discount_price = indexes.FloatField(null=True)

    

    sites = indexes.MultiValueField(null=True)
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField(null=True)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    slug = indexes.CharField(indexed=False)
    image = indexes.CharField(indexed=False, null=True)
    sku = indexes.CharField(indexed=False, null=True)
    meas_unit = indexes.CharField(indexed=False, null=True)
    doc_1 = indexes.CharField(indexed=False, null=True)
    doc_2 = indexes.CharField(indexed=False, null=True)
    doc_3 = indexes.CharField(indexed=False, null=True)

    def get_model(self):
        return Product

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):
        self.prepared_data = super(ProductIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'price': 'COST',
            'currency': 'CURRENCY',
            'slug': 'SLUG',
            'image': 'IMAGE',
            'sku': 'SKU',
            'meas_unit': 'MEASUREMENT_UNIT',
            'doc_1': 'DOCUMENT_1',
            'doc_2': 'DOCUMENT_2',
            'doc_3': 'DOCUMENT_3'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if attr is "COST":
                    self.prepared_data[field.index_fieldname] = float(attributes[attr][0])
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        comp = Company.objects.get(p2c__child_id=obj.pk, p2c__type="dependence")

        attributes = obj.getAttributeValues('DISCOUNT', 'COUPON_DISCOUNT', fullAttrVal=True)

        #Discount
        discountIndex = self.fields['discount'].index_fieldname

        if 'DISCOUNT' in attributes:
            self.prepared_data[discountIndex] = float(attributes['DISCOUNT'][0]['title'])
        else:
            self.prepared_data[discountIndex] = 0


        couponIndex = self.fields['coupon'].index_fieldname
        couponEndIndex = self.fields['coupon_end'].index_fieldname
        couponStartIndex = self.fields['coupon_start'].index_fieldname

        #Coupon Discount
        if 'COUPON_DISCOUNT' in attributes:
            self.prepared_data[couponIndex] = float(attributes['COUPON_DISCOUNT'][0]['title'])
            self.prepared_data[couponEndIndex] = attributes['COUPON_DISCOUNT'][0]['end_date']
            self.prepared_data[couponStartIndex] = attributes['COUPON_DISCOUNT'][0]['start_date']
        else:
            self.prepared_data[couponIndex] = 0
            self.prepared_data[couponEndIndex] = datetime(1, 1, 1)
            self.prepared_data[couponStartIndex] = now()

        #Company
        companyIndex = self.fields['company'].index_fieldname
        self.prepared_data[companyIndex] = comp.pk

        #Country
        countryIndex = self.fields['country'].index_fieldname
        self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type="dependence").pk

        #Discount price
        discountPriceIndex = self.fields['discount_price'].index_fieldname
        priceIndex = self.fields['price'].index_fieldname

        if self.prepared_data.get(discountIndex, None) and self.prepared_data.get(priceIndex, None):
            price = float(self.prepared_data[priceIndex])
            discount = float(self.prepared_data[discountIndex])
            discount_price = price - (price * discount / 100)
            self.prepared_data[discountPriceIndex] = float(discount_price)
        else:
            self.prepared_data[discountPriceIndex] = 0

        #TPP
        tppIndexfield = self.fields['tpp'].index_fieldname

        try:
            self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child_id=comp.pk, p2c__type="relation").pk
        except ObjectDoesNotExist:
            self.prepared_data[tppIndexfield] = 0

        return self.prepared_data

    def prepare_categories(self, obj):

        try:
            categories = Category.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            categoryList = []

            for category in categories:
                hierarchy = Category.hierarchy.getDescendants(category.pk, includeSelf=True)
                categoryList += [int(cat['ID']) for cat in hierarchy if cat['ID'] not in categoryList]

            return categoryList
        except ObjectDoesNotExist:
            return None

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def prepare_obj_creae_date(self, obj):
        return obj.create_date

    def prepare_sites(self, obj):
        return [site.pk for site in obj.sites.all()]

########################## News Index #############################

class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    anons = indexes.CharField(null=True)
    title = indexes.CharField()
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    categories = indexes.MultiValueField(null=True)
    branch = indexes.MultiValueField(null=True)
    
    obj_end_date = indexes.DateTimeField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_create_date = indexes.DateTimeField()
    video = indexes.BooleanField(default=False)
    image = indexes.CharField(null=True, indexed=False)

    slug = indexes.CharField(indexed=False)
    youtube_code = indexes.CharField(indexed=False, null=True)


    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    def prepare(self, obj):
        self.prepared_data = super(NewsIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'video': 'YOUTUBE_CODE',
            'slug': 'SLUG',
            'image': 'IMAGE',
            'anons': 'ANONS',
            'youtube_code': 'YOUTUBE_CODE'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if field_name == 'video':
                    if attributes[attr][0] == '':
                        self.prepared_data[field.index_fieldname] = False
                    else:
                        self.prepared_data[field.index_fieldname] = True
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=obj.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None



        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        comp = Company.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")

        if comp.exists():
            self.prepared_data[companyIndex] = comp[0].pk


            if not self.prepared_data[countryIndex]:
                self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp[0].pk, p2c__type='dependence').pk

            self.prepared_data[tppIndexfield] = 0
        elif tpp.exists():

            tpp = tpp.all()

            self.prepared_data[companyIndex] = 0
            self.prepared_data[tppIndexfield] = tpp[0].pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp[0].pk, p2c__type='dependence')

                if country.exists():

                    self.prepared_data[countryIndex] = country[0].pk

        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def prepare_categories(self, obj):
        try:
            categories = NewsCategories.objects.filter(p2c__child=obj.pk, p2c__type='relation')
            return [category.pk for category in categories]
        except ObjectDoesNotExist:
            return None

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return News

########################## Tenders Index #############################

class TenderIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    start_event_date = indexes.DateField(null=True)
    end_event_date = indexes.DateField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    obj_create_date = indexes.DateTimeField()
    price = indexes.FloatField(null=True)
    currency = indexes.CharField(null=True)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    slug = indexes.CharField(indexed=False)

    doc_1 = indexes.CharField(indexed=False, null=True)
    doc_2 = indexes.CharField(indexed=False, null=True)
    doc_3 = indexes.CharField(indexed=False, null=True)


    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):
        self.prepared_data = super(TenderIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'start_event_date': 'START_EVENT_DATE',
            'end_event_date': 'END_EVENT_DATE',
            'price': 'COST',
            'slug': 'SLUG',
            'doc_1': 'DOCUMENT_1',
            'doc_2': 'DOCUMENT_2',
            'doc_3': 'DOCUMENT_3',
            'currency': 'CURRENCY'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if field_name == 'start_event_date' or field_name == 'end_event_date':
                    self.prepared_data[field.index_fieldname] = datetime.strptime(attributes[attr][0], "%m/%d/%Y")
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=obj.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None

        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        comp = Company.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")

        if comp.exists():

            self.prepared_data[companyIndex] = comp[0].pk


            if not self.prepared_data[countryIndex]:
                self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp[0].pk, p2c__type='dependence').pk

            self.prepared_data[tppIndexfield] = 0
        elif tpp.exists():
            tpp = tpp.all()

            self.prepared_data[companyIndex] = 0
            self.prepared_data[tppIndexfield] = tpp[0].pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp[0].pk, p2c__type='dependence')

                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk

        return self.prepared_data

    def get_model(self):
        return Tender

########################## Innovation Projects Index #############################

class InnovIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    cabinet = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    obj_create_date = indexes.DateTimeField()
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    branch = indexes.MultiValueField(null=True)
    doc_1 = indexes.CharField(indexed=False, null=True)
    doc_2 = indexes.CharField(indexed=False, null=True)
    doc_3 = indexes.CharField(indexed=False, null=True)

    price = indexes.FloatField(null=True)
    currency = indexes.CharField(null=True)
    product_name = indexes.CharField(null=True)
    bussines_plan = indexes.CharField(null=True, indexed=False)
    release_date = indexes.CharField(null=True, indexed=False)


    slug = indexes.CharField(indexed=False)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(InnovIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'price': 'COST',
            'currency': 'CURRENCY',
            'product_name': 'PRODUCT_NAME',
            'release_date': 'RELEASE_DATE',
            'doc_1': 'DOCUMENT_1',
            'doc_2': 'DOCUMENT_2',
            'doc_3': 'DOCUMENT_3',
            'bussines_plan': 'BUSINESS_PLAN'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if attr is "COST":
                    self.prepared_data[field.index_fieldname] = float(attributes[attr][0])
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date


        #country
        countryIndex = self.fields['country'].index_fieldname
        self.prepared_data[countryIndex] = None

        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname
        cabinetIndex = self.fields['cabinet'].index_fieldname

        comp = Company.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        cabinet = Cabinet.objects.filter(user=obj.create_user)

        if comp.exists():
            comp = comp[0]

            self.prepared_data[cabinetIndex] = 0
            self.prepared_data[companyIndex] = comp.pk

            self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type='dependence').pk

            try:
                self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child=obj.pk, p2c__type="relation").pk
            except ObjectDoesNotExist:
                self.prepared_data[tppIndexfield] = 0
        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[cabinetIndex] = 0
            self.prepared_data[companyIndex] = 0
            self.prepared_data[tppIndexfield] = tpp.pk

            try:

                country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='dependence')

                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk
            except:
                self.prepared_data[countryIndex] = None


        elif cabinet.exists():
            cabinet = cabinet[0]

            self.prepared_data[cabinetIndex] = cabinet.pk

            try:
                country = Country.objects.filter(p2c__child_id=cabinet.pk, p2c__type='relation')
            
                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk
            except:
                self.prepared_data[countryIndex] = None
        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return InnovationProject

########################## Tpp Index #############################
class TppTvIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    country = indexes.IntegerField(null=True)
    obj_create_date = indexes.DateTimeField()
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    categories = indexes.MultiValueField(null=True)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    slug = indexes.CharField(indexed=False)
    image = indexes.CharField(null=True, indexed=False)
    youtube_code = indexes.CharField(indexed=False, null=True)


    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(TppTvIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'image': 'IMAGE',
            'youtube_code': 'YOUTUBE_CODE'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child=obj.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None

        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def prepare_categories(self, obj):
        try:
            categories = NewsCategories.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [category.pk for category in categories]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return TppTV


class NewsCategoriesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title_sort = indexes.CharField(indexed=False, faceted=True)
    
    title_auto = indexes.NgramField()

    def prepare(self, obj):

        self.prepared_data = super(NewsCategoriesIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME')

        if len(attr) == 0 or attr[0].strip() == '':
            return self.prepared_data
        else:
            name = attr[0]


        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname

        self.prepared_data[sortIndex] = name.lower().strip().replace(' ','_')
        self.prepared_data[textIndex] = name.strip()
        self.prepared_data[titleAutoIndex] = name.strip()

        return self.prepared_data
    
    def get_model(self):
        return NewsCategories
    


########################## Department Index #############################
class DepartmentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    company = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    slug = indexes.CharField(indexed=False)


    def prepare(self, obj):

        self.prepared_data = super(DepartmentIndex, self).prepare(obj)

        attributes = obj.getAttributeValues('NAME', 'SLUG')

        if len(attributes) == 0 or attributes.get('NAME', [''])[0].strip() == '':
            return self.prepared_data
        else:
            name = attributes.get('NAME', [''])[0].strip()

        if len(attributes) == 0 or attributes.get('SLUG', [''])[0] == '':
            return self.prepared_data
        else:
            slug = attributes.get('SLUG', [''])[0]


        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        slugIndex = self.fields['slug'].index_fieldname

        self.prepared_data[textIndex] = name
        self.prepared_data[sortIndex] = name.lower()
        self.prepared_data[slugIndex] = slug

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='hierarchy')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        comp = Company.objects.filter(p2c__child=obj.pk, p2c__type="hierarchy")
        tpp = Tpp.objects.filter(p2c__child=obj.pk, p2c__type="hierarchy")

        if comp.exists():
            comp = comp[0]

            self.prepared_data[companyIndex] = comp.pk

        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[tppIndexfield] = tpp.pk

        return self.prepared_data

    def get_model(self):
        return Department


########################## Cabinet Index #############################
class CabinetIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    country = indexes.IntegerField(null=True)
    email = indexes.CharField(null=True)
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    image = indexes.CharField(indexed=False, null=True)

    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    def prepare(self, obj):

        self.prepared_data = super(CabinetIndex, self).prepare(obj)

        attributes = obj.getAttributeValues('IMAGE', 'USER_MIDDLE_NAME', 'USER_FIRST_NAME', 'USER_LAST_NAME')

        if not isinstance(attributes, dict):
            return self.prepared_data

        name = []

        try:
            name.append(attributes['USER_FIRST_NAME'][0].strip())
        except KeyError:
            pass

        try:
            name.append(attributes['USER_MIDDLE_NAME'][0].strip())
        except KeyError:
            pass

        try:
            name.append(attributes['USER_LAST_NAME'][0].strip())
        except KeyError:
            pass

        if len(name) == 0:
            return self.prepared_data

        name = ' '.join(name)

        if name == '':
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname
        textIndex = self.fields['text'].index_fieldname
        imageIndex = self.fields['image'].index_fieldname

        self.prepared_data[textIndex] = name
        self.prepared_data[sortIndex] = name.lower()
        self.prepared_data[imageIndex] = attributes.get('NAME', [None])[0]


        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        parendStart = None

        emailIndex = self.fields['email'].index_fieldname
        self.prepared_data[emailIndex] = obj.user.email

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child=obj.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None

        return self.prepared_data


    def get_model(self):
        return Cabinet


########################## Resume Index #############################
class ResumeIndex(indexes.SearchIndex, indexes.Indexable):
    country = indexes.IntegerField(null=True)
    text = indexes.CharField(document=True)

    obj_create_date = indexes.DateTimeField()
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    cabinet = indexes.IntegerField(null=True)

    slug = indexes.CharField(indexed=False)


    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)

    birthday = indexes.CharField(indexed=False, null=True)
    marital_status = indexes.CharField(indexed=False, null=True)
    nationality = indexes.CharField(indexed=False, null=True)
    telephone_number = indexes.CharField(indexed=False, null=True)
    address = indexes.CharField(indexed=False, null=True)
    faculty = indexes.CharField(indexed=False, null=True)
    profession = indexes.CharField(indexed=False, null=True)
    study_start_date = indexes.CharField(indexed=False, null=True)
    study_end_date = indexes.CharField(indexed=False, null=True)
    study_form = indexes.CharField(indexed=False, null=True)
    company_exp_1 = indexes.CharField(indexed=False, null=True)
    company_exp_2 = indexes.CharField(indexed=False, null=True)
    company_exp_3 = indexes.CharField(indexed=False, null=True)
    position_exp_1 = indexes.CharField(indexed=False, null=True)
    position_exp_2 = indexes.CharField(indexed=False, null=True)
    position_exp_3 = indexes.CharField(indexed=False, null=True)
    start_date_exp_1 = indexes.CharField(indexed=False, null=True)
    start_date_exp_2 = indexes.CharField(indexed=False, null=True)
    start_date_exp_3 = indexes.CharField(indexed=False, null=True)
    end_date_exp_1 = indexes.CharField(indexed=False, null=True)
    end_date_exp_2 = indexes.CharField(indexed=False, null=True)
    end_date_exp_3 = indexes.CharField(indexed=False, null=True)
    additional_study = indexes.CharField(indexed=False, null=True)
    language_skill = indexes.CharField(indexed=False, null=True)
    computer_skill = indexes.CharField(indexed=False, null=True)
    additional_skill = indexes.CharField(indexed=False, null=True)
    salary = indexes.CharField(indexed=False, null=True)
    additional_information = indexes.CharField(indexed=False, null=True)
    institution = indexes.CharField(indexed=False, null=True)


    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(ResumeIndex, self).prepare(obj)
        attributes = obj.getAttributeValues('NAME', 'PROFESSION', 'SLUG')

        field_to_attr = {
            'text': 'NAME',
            'slug': 'SLUG',
            'birthday': 'BIRTHDAY',
            'marital_status': 'MARITAL_STATUS',
            'nationality': 'NATIONALITY',
            'telephone_number': 'TELEPHONE_NUMBER',
            'address': 'ADDRESS',
            'faculty': 'FACULTY',
            'profession': 'PROFESSION',
            'study_start_date': 'STUDY_START_DATE',
            'study_end_date': 'STUDY_END_DATE',
            'study_form': 'STUDY_FORM',
            'company_exp_1': 'COMPANY_EXP_1',
            'company_exp_2': 'COMPANY_EXP_2',
            'company_exp_3': 'COMPANY_EXP_3',
            'position_exp_1': 'POSITION_EXP_1',
            'position_exp_2': 'POSITION_EXP_2',
            'position_exp_3': 'POSITION_EXP_3',
            'start_date_exp_1': 'START_DATE_EXP_1',
            'start_date_exp_2': 'START_DATE_EXP_2',
            'start_date_exp_3': 'START_DATE_EXP_3',
            'end_date_exp_1': 'END_DATE_EXP_1',
            'end_date_exp_2': 'END_DATE_EXP_2',
            'end_date_exp_3': 'END_DATE_EXP_3',
            'additional_study': 'ADDITIONAL_STUDY',
            'language_skill': 'LANGUAGE_SKILL',
            'computer_skill': 'COMPUTER_SKILL',
            'additional_skill': 'ADDITIONAL_SKILL',
            'salary': 'SALARY',
            'additional_information': 'ADDITIONAL_INFORMATION',
            'institution': 'INSTITUTION'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()

        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child__p2c__child=obj.pk, p2c__child__p2c__type='dependence').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None


        cabinetIndex = self.fields['cabinet'].index_fieldname

        try:
            self.prepared_data[cabinetIndex] = Cabinet.objects.get(p2c__child=obj.pk).pk
        except ObjectDoesNotExist:
            self.prepared_data[cabinetIndex] = None

        return self.prepared_data


    def get_model(self):
        return Resume



########################## Requirement Index #############################
class RequirementIndex(indexes.SearchIndex, indexes.Indexable):
    country = indexes.IntegerField(null=True)
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    organization = indexes.IntegerField(null=True)
    obj_create_date = indexes.DateTimeField()


    slug = indexes.CharField(indexed=False)
    title_sort = indexes.CharField(indexed=False, faceted=True, stored=True)
    city = indexes.CharField(null=True)
    type = indexes.CharField(null=True)
    is_anonymous = indexes.BooleanField(default=False)
    requirements = indexes.CharField(null=True)
    terms = indexes.CharField(null=True)

    def prepare_obj_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(RequirementIndex, self).prepare(obj)


        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'slug': 'SLUG',
            'city': 'CITY',
            'is_anonymous': 'IS_ANONYMOUS_VACANCY',
            'type': 'TYPE_OF_EMPLOYMENT',
            'requirements': 'REQUIREMENTS',
            'terms': 'TERMS'
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        sortIndex = self.fields['title_sort'].index_fieldname

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr == 'NAME':
                    self.prepared_data[sortIndex] = attributes[attr][0].lower().strip()

                if attr == 'IS_ANONYMOUS_VACANCY':
                    self.prepared_data[field.index_fieldname] = True
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()



        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)

        #START DATE
        self.prepared_data[startDateIndex] = obj.start_date

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child__p2c__child__p2c__child__p2c__child=obj.pk).pk
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            self.prepared_data[countryIndex] = None


        #organization
        organizationIndex = self.fields['organization'].index_fieldname


        try:
            self.prepared_data[organizationIndex] = Organization.objects.get(p2c__child__p2c__child__p2c__child=obj.pk).pk
        except ObjectDoesNotExist:
            self.prepared_data[organizationIndex] = None




        return self.prepared_data


    def get_model(self):
        return Requirement


class VacancyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    obj_start_date = indexes.DateTimeField()
    obj_end_date = indexes.DateTimeField(null=True)
    department = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)

    
    slug = indexes.CharField(indexed=False)



    def prepare(self, obj):

        self.prepared_data = super(VacancyIndex, self).prepare(obj)


        field_to_attr = {
            'text': 'NAME',
            'slug': 'SLUG',
        }

        attributes = obj.getAttributeValues(*set(field_to_attr.values()))

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0].strip()) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0].strip()


        endDateIndex = self.fields['obj_end_date'].index_fieldname
        startDateIndex = self.fields['obj_start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='hierarchy')

            parentRel = func.make_object_dates_aware(parentRel)

            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

        obj = func.make_object_dates_aware(obj)

        #END DATE
        if not obj.end_date and parentRelEnd:
            self.prepared_data[endDateIndex] = parentRelEnd
        elif not parentRelEnd and obj.end_date:
            self.prepared_data[endDateIndex] = obj.end_date
        elif parentRelEnd and obj.end_date:

                if parentRelEnd > obj.end_date:
                    self.prepared_data[endDateIndex] = obj.end_date
                else:
                    self.prepared_data[endDateIndex] = parentRelEnd
        else:
            self.prepared_data[endDateIndex] = datetime(1, 1, 1)


        #START DATE
        if not parendStart and obj.start_date:
                self.prepared_data[startDateIndex] = obj.start_date
        elif parendStart and obj.start_date:

            if parendStart > obj.start_date:
                self.prepared_data[startDateIndex] = parendStart
            else:
                self.prepared_data[startDateIndex] = obj.start_date

        #department
        departmentIndex = self.fields['department'].index_fieldname

        dep = Department.objects.filter(p2c__child=obj.pk, p2c__type="hierarchy")

        if dep.exists():
            dep = dep[0]

            self.prepared_data[departmentIndex] = dep.pk

        #company
        companyIndex = self.fields['company'].index_fieldname

        comp = Company.objects.filter(p2c__child__p2c__child=obj.pk, p2c__type="hierarchy")

        if comp.exists():
            comp = comp[0]

            self.prepared_data[companyIndex] = comp.pk

        #tpp
        tppIndex = self.fields['tpp'].index_fieldname

        tpp = Tpp.objects.filter(p2c__child__p2c__child=obj.pk, p2c__type="hierarchy")

        if tpp.exists():
            tpp = tpp[0]

            self.prepared_data[tppIndex] = tpp.pk

        return self.prepared_data

    def get_model(self):
        return Vacancy
