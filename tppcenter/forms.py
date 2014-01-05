from django import forms
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary, Item
from appl.models import (Advertising, Announce, Article, Basket, Company, Cabinet, Department, Document,
                         Invoice, News, Forum, ForumPost, ForumThread, Order, Payment, Product, Tpp, Tender,
                         Rate, Rating, Review, Service, Site, Shipment,)
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext as _


class ItemForm(forms.Form):

    def __init__(self, item, values=None, id=None, *args, **kwrgs ):
        super(ItemForm, self).__init__()
        self.item = item
        self.id = id

        self.new_fields(item, values)


    def new_fields(self, item, values):

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
                self.fields[title] = forms.ChoiceField(widget=forms.Select, choices=slots, required=bool(required),

                                                       error_messages={'required': _('Please enter your Source')})
                self.fields[title].initial = value








            if(attr.type == "Str" or attr.type == "Chr") and dict is None:
                self.fields[title] = forms.CharField(required=bool(required),
                                                      error_messages={'required': _('Field is required')})


                self.fields[title].initial = value[0] if value and isinstance(value, list) else value



            if attr.type == "Dec":
                self.fields[title] = forms.IntegerField(required=bool(required),
                                                        error_messages={'required': 'Please enter your ALo'})
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

    def clean(self):
        self._errors = {}
        for title in self.fields:
            try:
                self.fields[title].clean(self.fields[title].initial)
            except Exception as e:
                self._errors[title] = e.messages[0]

    def is_valid(self):
        if len(self._errors) > 0:
            return False
        else:
            return True

    def save(self):
        if not self.is_valid():
            raise ValidationError
        if not self.id:
            site = settings.SITE_ID
            self.obj = globals()[self.item](name=self.fields['Name'].initial, title=self.fields["Name"].initial,) #change ["Name"] to something else
            self.obj.save()
            self.obj.sites.add(settings.SITE_ID)
        else:
            self.obj = globals()[self.item].objects.get(id=self.id)
            self.obj.name = self.fields['Name'].initial
            self.obj.title = self.fields['Name'].initial
            self.obj.save()
        attrValues = {}
        for title in self.fields:
            attrValues[title] = self.fields[title].initial

        self.obj.setAttributeValue(attrValues)
















