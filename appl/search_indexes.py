__author__ = 'Art'
from haystack import indexes
from appl.models import Company, Country, Tpp, News, Product, Category, Branch, NewsCategories
from django.conf import Settings
from django.core.exceptions import ObjectDoesNotExist

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


class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    branch = indexes.MultiValueField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    title_auto = indexes.NgramField(null=True)
    id = indexes.IntegerField()

    def prepare_id(self, object):
        return object.pk

    def index_queryset(self, using=None):
        return self.get_model().active

    def prepare(self, object):
        self.prepared_data = super(CompanyIndex, self).prepare(object)


        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'title_auto': 'NAME'
        }

        attributes = object.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

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
        return Country.objects.get(p2c__child_id=object.pk, p2c__type='dependence').pk

    def get_model(self):
        return Company

class TppIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.MultiValueField(null=True)
    title_auto = indexes.NgramField(null=True)
    id = indexes.IntegerField()

    def index_queryset(self, using=None):
        return self.get_model().active

    def prepare_id(self, object):
        return object.pk

    def prepare(self, object):
        self.prepared_data = super(TppIndex, self).prepare(object)


        field_to_attr = {
            'title': 'NAME',
            'title_auto': 'NAME',
            'text': 'DETAIL_TEXT'
        }

        attributes = object.getAttributeValues('NAME', 'DETAIL_TEXT')

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        return self.prepared_data

    def prepare_country(self, object):
        try:
            return [Country.objects.get(p2c__child_id=object.pk, p2c__type='relation').pk]
        except ObjectDoesNotExist:
            countries = Country.objects.filter(c2p__parent_id=object.pk, p2c__type='dependence')

            return [country.pk for country in countries]

    def get_model(self):
        return Tpp


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
    id = indexes.IntegerField()
    site = indexes.MultiValueField(null=True)

    def prepare_id(self, object):
        return object.pk

    def index_queryset(self, using=None):
        return self.get_model().active

    def prepare(self, object):
        self.prepared_data = super(ProductIndex, self).prepare(object)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT',
            'price': 'COST',
            'currency': 'CURRENCY'
        }

        attributes = object.getAttributeValues(*field_to_attr.values())

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

        comp = Company.objects.get(p2c__child_id=object.pk, p2c__type="dependence")

        attributes = object.getAttributeValues('DISCOUNT', 'COUPON_DISCOUNT', fullAttrVal=True)

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
        self.prepared_data[createIndex] = object.create_date

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

    def prepare_categories(self, object):
        try:
            categories = Category.objects.filter(p2c__child_id=object.pk, p2c__type='relation')
            return [category.pk for category in categories]
        except ObjectDoesNotExist:
            return None

    def prepare_branch(self, object):
        try:
            branches = Branch.objects.filter(p2c__child_id=object.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return Product


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, null=True)
    title = indexes.CharField(null=True)
    country = indexes.IntegerField(null=True)
    tpp = indexes.IntegerField(null=True)
    company = indexes.IntegerField(null=True)
    categories = indexes.MultiValueField(null=True)
    branch = indexes.MultiValueField(null=True)
    id = indexes.IntegerField()

    def prepare_id(self, object):
        return object.pk

    def index_queryset(self, using=None):
        return self.get_model().active

    def prepare(self, object):
        self.prepared_data = super(NewsIndex, self).prepare(object)

        field_to_attr = {
            'title': 'NAME',
            'text': 'DETAIL_TEXT'
        }

        attributes = object.getAttributeValues(*field_to_attr.values())

        if 'NAME' not in attributes or len(attributes['NAME']) == 0 or len(attributes['NAME'][0]) == 0:
            return self.prepared_data

        for field_name, field in self.fields.items():
            if field_name in field_to_attr:
                attr = field_to_attr[field_name]

                if attr not in attributes:
                    continue

                self.prepared_data[field.index_fieldname] = attributes[attr][0]

        #country
        countryIndex = self.fields['country'].index_fieldname

        try:
            self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=object.pk, p2c__type='relation').pk
        except ObjectDoesNotExist:
            self.prepared_data[countryIndex] = None



        #company , tpp
        companyIndex = self.fields['company'].index_fieldname
        tppIndexfield = self.fields['tpp'].index_fieldname

        comp = Company.objects.filter(p2c__child_id=object.pk, p2c__type="dependence")
        tpp = Tpp.objects.filter(p2c__child_id=object.pk, p2c__type="relation")

        if comp.exists():
            self.prepared_data[companyIndex] = comp.pk

            if not self.prepared_data[countryIndex]:
                self.prepared_data[countryIndex] = Country.objects.get(p2c__child_id=comp.pk, p2c__type='dependence').pk

            self.prepared_data[tppIndexfield] = None
        elif tpp.exists():
            self.prepared_data[companyIndex] = None
            self.prepared_data[tppIndexfield] = tpp.pk

            if not self.prepared_data[countryIndex]:
                country = Country.objects.filter(p2c__child_id=tpp.pk, p2c__type='dependence')

                if country.exists():
                    self.prepared_data[countryIndex] = country.pk

        return self.prepared_data

    def prepare_branch(self, object):
        try:
            branches = Branch.objects.filter(p2c__child_id=object.pk, p2c__type='relation')
            return [branch.pk for branch in branches]
        except ObjectDoesNotExist:
            return None

    def prepare_categories(self, object):
        try:
            categories = NewsCategories.objects.filter(p2c__child_id=object.pk, p2c__type='relation')
            return [category.pk for category in categories]
        except ObjectDoesNotExist:
            return None

    def get_model(self):
        return News
