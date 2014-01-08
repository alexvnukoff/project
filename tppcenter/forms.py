from django import forms
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary, Item
from appl.models import (Advertising, Announce, Article, Basket, Company, Cabinet, Department, Document,
                         Invoice, News, Forum, ForumPost, ForumThread, Order, Payment, Product, Tpp, Tender,
                         Rate, Rating, Review, Service, Site, Shipment,)
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile, FileField
from django.core.files import File


class ItemForm(forms.Form):

    def __init__(self, item, values=None, id=None, *args, **kwrgs ):
        super(ItemForm, self).__init__()
        self.item = item
        self.id = id

        self.new_fields(item, values)



    def new_fields(self, item, values):
        """
       Method that define new form fields for items
       item - specific class (news, company and etc.)
       values - initial values of fields
       """

        object_id = ContentType.objects.get(name=str(item).lower()).id
        attributes = AttrTemplate.objects.filter(classId=object_id).select_related("attrId", "attrId__dict").order_by('order')
        if self.id and not values:
            attrs = [str(attr.attrId.title) for attr in attributes]
            self.obj = globals()[item].objects.get(id=self.id)
            values = self.obj.getAttributeValues(*attrs)[int(self.id)]



        for attribute in attributes:
            dict = attribute.attrId.dict
            attr = attribute.attrId
            required = attribute.required
            title = str(attr.title)
            if values:
                value = values.get(title, "")
            else:
                value = ""





            if dict is not None:
                slots = tuple(dict.getSlotsList().values_list("id", "title"))
                self.fields[title] = forms.ChoiceField(widget=forms.Select, choices=slots)
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            if(attr.type == "Fph") and dict is None:
                self.fields[title] = forms.FilePathField(widget=forms.SelectMultiple, path='%s/%s' % (settings.MEDIA_ROOT, "images/"), required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            if(attr.type == "Bin") and dict is None:
                self.fields[title] = forms.BooleanField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            if(attr.type == "Dat") and dict is None:
                self.fields[title] = forms.DateField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            if(attr.type == "Eml") and dict is None:
                self.fields[title] = forms.EmailField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value



            if(attr.type == "Flo") and dict is None:
                self.fields[title] = forms.FloatField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            if(attr.type == "Ip") and dict is None:
                self.fields[title] = forms.IPAddressField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            if(attr.type == "Tm") and dict is None:
                self.fields[title] = forms.TimeField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            if(attr.type == "Url") and dict is None:
                self.fields[title] = forms.URLField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value



            if(attr.type == "Sdt") and dict is None:
                self.fields[title] = forms.SplitDateTimeField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            if(attr.type == "Str") and dict is None:
                self.fields[title] = forms.CharField(widget=forms.Textarea, required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value






            if(attr.type == "Chr") and dict is None:

                #self.fields[title] = forms.ImageField(required=bool(required))
                #self.files[title] = ImageFieldFile(instance=None, field=FileField(),
                #             name='images/alo.jpg')
                #image_url = '%s/%s' % (settings.MEDIA_ROOT, "images/alo.jpg")
                #f = open('%s/%s' % (settings.MEDIA_ROOT, "images/alo.jpg"), 'rb')
                #myfile = File(f)
                #self.files[title]._file = myfile
                #self.files[title].field = self.fields[title]

                #self.fields[title].initial = value[0]


                self.fields[title] = forms.CharField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            if attr.type == "Dec":
                self.fields[title] = forms.IntegerField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

    def clean(self):
        """
        Method that validate fields of the form

        """
        self._errors = {}
        for title in self.fields:
            try:
                self.fields[title].clean(self.fields[title].initial)
            except Exception as e:
                self._errors[title] = e.messages[0]

    def is_valid(self):
        """
        Method return True if form is valid and False otherwise
        """
        if len(self._errors) > 0:
            return False
        else:
            return True

    def save(self):
        """
        Method create new item and set values of attributes
        if object exist its update his attribute
        """
        path_to_images = "images/"
        if not self.is_valid():
            raise ValidationError
        if not self.id:
            site = settings.SITE_ID
            self.obj = globals()[self.item](name=self.fields['Name'].initial, title=self.fields["Name"].initial,) #TODO change ["Name"] to something else
            self.obj.save()
            self.obj.sites.add(settings.SITE_ID)
        else:
            self.obj = globals()[self.item].objects.get(id=self.id)
            self.obj.name = self.fields['Name'].initial
            self.obj.title = self.fields['Name'].initial
            self.obj.save()
        attrValues = {}
        for title in self.fields:
            if isinstance(self.fields[title], forms.ImageField) and self.fields[title].initial:
                save_file(self.fields[title].initial, path_to_images)
                self.fields[title].initial = path_to_images + str(self.fields[title].initial)
            attrValues[title] = self.fields[title].initial

        self.obj.setAttributeValue(attrValues)

        return self.obj



def save_file(file, path=''):
    filename = file._get_name()
    fd = open('%s/%s' % (settings.MEDIA_ROOT, str(path) + str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()















