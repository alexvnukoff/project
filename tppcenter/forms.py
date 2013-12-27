from django import forms
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary



class ItemForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        object_id = ContentType.objects.get(name=str(kwargs['initial']).lower()).id
        attributes = AttrTemplate.objects.filter(classId=object_id).select_related("attrId", "attrId__dict")

        for attribute in attributes:
            dict = attribute.attrId.dict
            attr = attribute.attrId
            required = attribute.required
            title = str(attr.title)
            if dict is not None:
                slots = tuple(dict.getSlotsList().values_list("id", "title"))
                self.Name = forms.ChoiceField(widget=forms.Select, choices=slots, required=bool(required))

            if (attr.type == "Str" or attr.type == "Chr") and dict is None:
                self.Book = forms.CharField(required=bool(required))
            if attr.type == "Dec":
                self.Number = forms.IntegerField(required=bool(required))












