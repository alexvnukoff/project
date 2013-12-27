from django import forms
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary , Item
from django.views.generic import FormView



class ItemForm(forms.Form):

    def __init__(self, item, *args, **kwrgs ):
        super(ItemForm, self).__init__()
        self.new_values(item)

    def new_values(self, item):
        object_id = ContentType.objects.get(name=str(item).lower()).id
        attributes = AttrTemplate.objects.filter(classId=object_id).select_related("attrId", "attrId__dict")

        for attribute in attributes:
            dict = attribute.attrId.dict
            attr = attribute.attrId
            required = attribute.required
            title = str(attr.title)
            if dict is not None:
                slots = tuple(dict.getSlotsList().values_list("id", "title"))
                self.fields[title] = forms.ChoiceField(widget=forms.Select,
                                                       choices=slots, required=bool(required), initial=title)



            if(attr.type == "Str" or attr.type == "Chr") and dict is None:
                self.fields[title] = forms.CharField(required=bool(required))

            if attr.type == "Dec":
                self.fields[title] = forms.IntegerField(required=bool(required))















