__author__ = 'Art'
from haystack import indexes
from appl.models import Company, Country, Tpp, News, Product, Category, Branch, NewsCategories, \
    BusinessProposal, Exhibition, Tender, InnovationProject, Cabinet, TppTV
from core.models import Relationship
from django.conf import Settings
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

class SearchIndexActive(indexes.SearchIndex):
    def index_queryset(self, using=None):
        return self.get_model().active.get_active()


class SearchIndexActive(indexes.SearchIndex):
    def index_queryset(self, using=None):
        return self.get_model().active.get_active()

################## Exhibition Index #############################

class ExhibitionProposalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    tpp = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    branch = indexes.MultiValueField(null=True)
    id = indexes.IntegerField()
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()
    start_event_date = indexes.DateField(null=True)
    end_event_date = indexes.DateField(null=True)
    create_date = indexes.DateTimeField(null=True)

    def prepare_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return Exhibition

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(ExhibitionProposalIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'start_event_date': 'START_EVENT_DATE',
            'end_event_date': 'END_EVENT_DATE'
        }

        attributes = obj.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if field_name == 'start_event_date' or field_name == 'end_event_date':
                    self.prepared_data[field.index_fieldname] = datetime.strptime(attributes[attr][0], "%m/%d/%Y")
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0]


        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None
            
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
                self.prepared_data[tppIndexfield] = None

        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[companyIndex] = None
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
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    tpp = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    branch = indexes.MultiValueField(null=True)
    id = indexes.IntegerField()
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()
    create_date = indexes.DateTimeField(null=True)

    def prepate_create_date(self, obj):
        return obj.create_date

    def get_model(self):
        return BusinessProposal


    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(BusinessProposalIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
        }

        attributes = obj.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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
                self.prepared_data[tppIndexfield] = None

        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[companyIndex] = None
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
    text = indexes.CharField(document=True, null=True)
    id = indexes.IntegerField()
    title_auto = indexes.NgramField(null=True)

    def get_model(self):
        return Country

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(CountryIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME')

        if len(attr) == 0 or attr[0] == '':
            return self.prepared_data

        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname


        self.prepared_data[textIndex] = attr[0]
        self.prepared_data[titleAutoIndex] = attr[0]

        return self.prepared_data


########################## Category Index #############################

class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    id = indexes.IntegerField()
    title_auto = indexes.NgramField(null=True)

    def get_model(self):
        return Category

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(CategoryIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME')

        if len(attr) == 0 or attr[0] == '':
            return self.prepared_data

        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname


        self.prepared_data[textIndex] = attr[0]
        self.prepared_data[titleAutoIndex] = attr[0]

        return self.prepared_data

########################## Branches Index #############################

class BranchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    id = indexes.IntegerField()
    title_auto = indexes.NgramField(null=True)

    def get_model(self):
        return Branch

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(BranchIndex, self).prepare(obj)

        attr = obj.getAttributeValues('NAME')

        if len(attr) == 0 or attr[0] == '':
            return self.prepared_data

        textIndex = self.fields['text'].index_fieldname
        titleAutoIndex = self.fields['title_auto'].index_fieldname


        self.prepared_data[textIndex] = attr[0]
        self.prepared_data[titleAutoIndex] = attr[0]

        return self.prepared_data

########################## Company Index #############################

class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    branch = indexes.MultiValueField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    title_auto = indexes.NgramField(null=True)
    id = indexes.IntegerField()
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()
    create_date = indexes.DateTimeField(null=True)

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(CompanyIndex, self).prepare(obj)


        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'title_auto': 'NAME'
        }

        attributes = obj.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.MultiValueField(null=True)
    title_auto = indexes.NgramField(null=True)
    id = indexes.IntegerField()
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()
    create_date = indexes.DateTimeField(null=True)

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(TppIndex, self).prepare(obj)


        field_to_attr = {
            'title': 'NAME',
            'title_auto': 'NAME',
            'text': 'DETAIL_TEXT'
        }

        attributes = obj.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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
            return list(Country.objects.filter(p2c__child_id=obj.pk, p2c__type='dependence').values_list('pk', flat=True))
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return Tpp

########################## Products Index #############################

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    branch = indexes.MultiValueField(null=True)
    categories = indexes.MultiValueField(null=True)
    discount = indexes.FloatField(null=True)
    coupon = indexes.FloatField(null=True)
    coupon_start = indexes.DateTimeField(null=True)
    coupon_end = indexes.DateTimeField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    country = indexes.IntegerField(null=True)
    create_date = indexes.DateTimeField(null=True)
    price = indexes.FloatField(null=True)
    currency = indexes.CharField(null=True)
    discount_price = indexes.FloatField(null=True)

    sites = indexes.MultiValueField(null=True)
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()

    id = indexes.IntegerField()

    def get_model(self):
        return Product

    def prepare_id(self, obj):
        return obj.pk

    def prepare(self, obj):
        self.prepared_data = super(ProductIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'price': 'COST',
            'currency': 'CURRENCY'
        }

        attributes = obj.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if attr is "COST":
                    self.prepared_data[field.index_fieldname] = float(attributes[attr][0])
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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
            self.prepared_data[discountIndex] = None


        couponIndex = self.fields['coupon'].index_fieldname
        couponEndIndex = self.fields['coupon_end'].index_fieldname

        #Coupon Discount
        if 'COUPON_DISCOUNT' in attributes:
            self.prepared_data[couponIndex] = float(attributes['COUPON_DISCOUNT'][0]['title'])
            self.prepared_data[couponEndIndex] = attributes['COUPON_DISCOUNT'][0]['end_date']
        else:
            self.prepared_data[couponIndex] = None
            self.prepared_data[couponEndIndex] = None

        #Company
        companyIndex = self.fields['company'].index_fieldname
        self.prepared_data[companyIndex] = comp.pk

        #Country
        countryIndex = self.fields['country'].index_fieldname
        self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type="dependence").pk

        #Create Date
        createIndex = self.fields['create_date'].index_fieldname
        self.prepared_data[createIndex] = obj.create_date

        #Discount price
        discountPriceIndex = self.fields['discount_price'].index_fieldname
        priceIndex = self.fields['price'].index_fieldname

        if self.prepared_data.get(discountIndex, None) and self.prepared_data.get(priceIndex, None):
            price = float(self.prepared_data[priceIndex])
            discount = float(self.prepared_data[discountIndex])
            discount_price = price - (price * discount / 100)
            self.prepared_data[discountPriceIndex] = float(discount_price)
        else:
            self.prepared_data[discountPriceIndex] = None

        #TPP
        tppIndexfield = self.fields['tpp'].index_fieldname

        try:
            self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child_id=comp.pk, p2c__type="relation").pk
        except ObjectDoesNotExist:
            self.prepared_data[tppIndexfield] = None

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

    def prepare_sites(self, obj):
        return [site.pk for site in obj.sites.all()]

########################## News Index #############################

class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    categories = indexes.MultiValueField(null=True)
    branch = indexes.MultiValueField(null=True)
    id = indexes.IntegerField()
    end_date = indexes.DateTimeField(null=True)
    start_date = indexes.DateTimeField()
    create_date = indexes.DateTimeField()
    video = indexes.BooleanField(default=False)

    def prepare_id(self, obj):
        return obj.pk

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):
        self.prepared_data = super(NewsIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'video': 'YOUTUBE_CODE'
        }

        attributes = obj.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if field_name == 'video':
                    if attributes[attr][0] == '':
                        self.prepared_data[field.index_fieldname] = False
                    else:
                        self.prepared_data[field.index_fieldname] = True
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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

            self.prepared_data[tppIndexfield] = None
        elif tpp.exists():

            tpp = tpp.all()

            self.prepared_data[companyIndex] = None
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
            categories = NewsCategories.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [category.pk for category in categories]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return News

########################## News Index #############################

class TenderIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    start_event_date = indexes.DateField(null=True)
    end_event_date = indexes.DateField(null=True)
    start_date = indexes.DateTimeField()
    end_date = indexes.DateTimeField(null=True)
    cost = indexes.FloatField(null=True)
    create_date = indexes.DateTimeField()

    id = indexes.IntegerField()

    def prepare_id(self, obj):
        return obj.pk

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):


        self.prepared_data = super(TenderIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'start_event_date': 'START_EVENT_DATE',
            'end_event_date': 'END_EVENT_DATE',
            'cost': 'COST',
        }

        attributes = obj.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                if field_name == 'start_event_date' or field_name == 'end_event_date':
                    self.prepared_data[field.index_fieldname] = datetime.strptime(attributes[attr][0], "%m/%d/%Y")
                else:
                    self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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

            self.prepared_data[tppIndexfield] = None
        elif tpp.exists():
            tpp = tpp.all()

            self.prepared_data[companyIndex] = None
            self.prepared_data[tppIndexfield] = tpp[0].pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp[0].pk, p2c__type='dependence')

                if country.exists():
                    country = country[0]
                    self.prepared_data[countryIndex] = country.pk

        return self.prepared_data

    def get_model(self):
        return Tender


class InnovIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    create_date = indexes.DateTimeField()
    start_date = indexes.DateTimeField()
    end_date = indexes.DateTimeField(null=True)
    branch = indexes.MultiValueField(null=True)

    id = indexes.IntegerField()

    def prepare_id(self, obj):
        return obj.pk

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(InnovIndex, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
        }

        attributes = obj.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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

        comp = Company.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=obj.pk, p2c__type="dependence")
        cabinet = Cabinet.objects.filter(user=obj.create_user)

        if comp.exists():
            comp = comp[0]

            self.prepared_data[companyIndex] = comp.pk

            self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type='dependence').pk

            try:
                self.prepared_data[tppIndexfield] = Tpp.objects.get(p2c__child=obj.pk, p2c__type="relation").pk
            except ObjectDoesNotExist:
                self.prepared_data[tppIndexfield] = None
        elif tpp.exists():
            tpp = tpp[0]

            self.prepared_data[companyIndex] = None
            self.prepared_data[tppIndexfield] = tpp.pk

            country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='dependence')

            if country.exists():
                country = country[0]
                self.prepared_data[countryIndex] = country.pk

        elif cabinet.exists():
            cabinet = cabinet.all()

            country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='relation')

            if country.exists():
                country = country.all()
                self.prepared_data[countryIndex] = country.pk

        return self.prepared_data

    def prepare_branch(self, obj):
        try:
            branches = Branch.objects.filter(p2c__child_id=obj.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return InnovationProject


class TppTv(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.IntegerField(null=True)
    create_date = indexes.DateTimeField()
    start_date = indexes.DateTimeField()
    end_date = indexes.DateTimeField(null=True)
    categories = indexes.MultiValueField(null=True)

    id = indexes.IntegerField()

    def prepare_id(self, obj):
        return obj.pk

    def prepare_create_date(self, obj):
        return obj.create_date

    def prepare(self, obj):

        self.prepared_data = super(TppTv, self).prepare(obj)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
        }

        attributes = obj.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        endDateIndex = self.fields['end_date'].index_fieldname
        startDateIndex = self.fields['start_date'].index_fieldname

        #Get parent active date
        try:
            parentRel = Relationship.objects.get(child=obj.pk, type='dependence')
            parentRelEnd = parentRel.end_date
            parendStart = parentRel.start_date
        except ObjectDoesNotExist:
            parentRelEnd = None
            parendStart = None

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

