from django import forms
import os
import uuid
from django.forms.models import BaseModelFormSet
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary, Item, Relationship
from appl.models import (Advertising, Announce, Article, Basket, Company, Cabinet, Department, Document,
                         Invoice, News, Order, Payment, Product, Tpp, Tender,
                         Rate, Rating, Review, Service, Shipment, Gallery, Country, Comment, Category)

from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile, FileField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.models import modelformset_factory


class ItemForm(forms.Form):

    def __init__(self, item, values=None, id=None):
        '''
        Overriding of BaseForm __init__
        parameters:
        item = class Name of Item (News, Company)
        values = Dict that contain values to forms field (Post)

        id = pk, of specific item , if needs update of values
        Example :
        form = Form("News" , values = request.POST, id = 4)(Update News with id 4 by values)
        '''
        self.item = item
        self.id = id
        self.file_to_delete = ""

        super(ItemForm, self).__init__()
        # Get id of ContentType of specific Item
        object_id = ContentType.objects.get(name=str(item).lower()).id
        # Get default attributes of Item
        attributes = AttrTemplate.objects.filter(classId=object_id).select_related("attrId", "attrId__dict")

         #IF id parameter isn't null , and we want update form ,need to populate field with initial values
        if self.id:
            self.obj = globals()[item].objects.get(id=self.id)
        if self.id and not values:
            attrs = [str(attr.attrId.title) for attr in attributes]
            values = self.obj.getAttributeValues(*attrs)


        # Build form fields , depends on type of attribute
        for attribute in attributes:
            dictr = attribute.attrId.dict
            attr = attribute.attrId
            required = attribute.required
            title = str(attr.title)
            if values:
                value = values.get(title, "")
            else:
                value = ""




            # Check , what type of attribute , and choose appropriate field
            #Dictionary attribute
            if dictr is not None:
                slots = tuple(dictr.getSlotsList().values_list("id", "title"))
                self.fields[title] = forms.ChoiceField(widget=forms.Select, choices=slots)

                slotDict = dict([(v, k) for k, v in dict(slots).items()])
                self.fields[title].initial = slotDict.get(value[0], value[0]) if value and isinstance(value, list) else value

            #FilePath attribute
            if(attr.type == "Fph") and dictr is None:
                self.fields[title] = forms.FilePathField(widget=forms.SelectMultiple, path='%s/%s' % (settings.MEDIA_ROOT, "upload/"), required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Boolean
            if(attr.type == "Bin") and dictr is None:
                self.fields[title] = forms.BooleanField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Date
            if(attr.type == "Dat") and dictr is None:
                self.fields[title] = forms.DateField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Email
            if(attr.type == "Eml") and dictr is None:
                self.fields[title] = forms.EmailField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            #Float
            if(attr.type == "Flo") and dictr is None:
                self.fields[title] = forms.FloatField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #IpAdress
            if(attr.type == "Ip") and dictr is None:
                self.fields[title] = forms.IPAddressField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Time
            if(attr.type == "Tm") and dictr is None:
                self.fields[title] = forms.TimeField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Url
            if(attr.type == "Url") and dictr is None:
                self.fields[title] = forms.URLField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value


            #SplitDateTime
            if(attr.type == "Sdt") and dictr is None:
                self.fields[title] = forms.SplitDateTimeField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #String (text area)
            if(attr.type == "Str") and dictr is None:
                self.fields[title] = forms.CharField(widget=forms.Textarea, required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #ImageField
            if(attr.type == "Img") and dictr is None:
                 self.fields[title] = forms.ImageField(required=bool(required))
                 value = value[0] if value and isinstance(value, list) else value

                 if value:
                    if not isinstance(value, InMemoryUploadedFile):
                           self.fields[title].initial = ImageFieldFile(instance=None, field=FileField(),  name=value)
                    else:
                           self.fields[title].initial = value
                    if self.id and self.obj:
                         picture = self.obj.getAttributeValues(title) if self.id else ""
                         self.file_to_delete = picture


                 else:
                     picture = self.obj.getAttributeValues(title) if self.id else ""
                     value = picture if self.id and picture else ""

                     self.fields[title].initial = ImageFieldFile(instance=None, field=FileField(), name=value[0]) if value else ""

            #Text field (input type= "text")
            if(attr.type == "Chr") and dictr is None:
                self.fields[title] = forms.CharField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value

            #Integer field
            if attr.type == "Dec":
                self.fields[title] = forms.IntegerField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value






    def clean(self):
        """
        Method that validate fields of the form
        return ErrorList with Error messages

        """
        self._errors = {}
        for title in self.fields:
            try:
                if (isinstance(self.fields[title], forms.ImageField) and not isinstance(self.fields[title].initial, InMemoryUploadedFile)
                      and self.fields[title].initial):
                    continue
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

    def save(self, user):
        """
        Method create new item and set values of attributes
        if object exist its update his attribute
        user = request.user
        Example: form.update(request.user)
        Return object of Item
        """
        path_to_images = "upload/"
        if not self.is_valid():
            raise ValidationError
        if not self.id:
            site = settings.SITE_ID
            self.obj = globals()[self.item](create_user=user)
            self.obj.save()
            self.obj.sites.add(settings.SITE_ID)
        else:
            self.obj = globals()[self.item].objects.get(id=self.id)
           # self.obj.name = self.fields['NAME'].initial
            #self.obj.title = self.fields['NAME'].initial
            self.obj.save()
        attrValues = {}
        for title in self.fields:
            if (isinstance(self.fields[title], forms.ImageField) and self.fields[title].initial and
                                    isinstance(self.fields[title].initial, InMemoryUploadedFile)):
                self._save_file(self.fields[title].initial, title, path_to_images)
                # If Field is Image that call save_file method

            attrValues[title] = self.fields[title].initial

        self.obj.setAttributeValue(attrValues, user)

        return self.obj



    def _save_file(self, file, title, path=''):
        """
        Method that save new file , and delete old file if exist
        parameters:
        file = self.fields[title].initial (object of InMemoryUploadedFile)
        title = title of the field
        path = path to file
        It's internal method of ItemForm class , to save files
        """


        filename = file._get_name()
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        fd = open('%s/%s' % (settings.MEDIA_ROOT, str(path) + str(filename)), 'wb')
        for chunk in file.chunks():
            fd.write(chunk)
        fd.close()
        filename = str(path) + str(filename)
        self.fields[title].initial = ImageFieldFile(instance=None, field=FileField(),  name=filename)
        if self.file_to_delete:
           filename = '%s/%s' % (settings.MEDIA_ROOT, self.file_to_delete[0])
           if os.path.isfile(filename):
                os.remove(filename)
        #if file has been saved , update initial value of ImageField

    def setlabels(self, dict):
        for oldLabel, newLabel in dict.items():
            self.fields[oldLabel].label = newLabel








class Test(forms.Form):#its TEST , not for documentation




    def __init__(self, item, post=None, files=None, id=None, user=None):
        super(Test, self).__init__()







class BasePhotoGallery(BaseModelFormSet):
    """
    Class that define formset  of photogallery
    Example of usage:
     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=2, fields=("photo", "title"))
     form = Photo()
    Gallery its model that contain field ImageField
    extra its extra field
    fieds its fields that will be desplayed

    """

    def __init__(self, *args, parent_id=None, **kwargs):
        """
        __init__ of BasePhotoGallery
        parent_id = items that in relationship with Gallery
        """
        super(BasePhotoGallery, self).__init__(*args, **kwargs)

        self.user = parent_id
        self.queryset = Gallery.objects.filter(c2p__parent_id=parent_id)
    def save(self, parent=None, user=None, commit=True):
        """
        Method that create new Gallery , and set relationship with parent object
        Example :
        form.save(parent = 34 , user = request.user, commit =True)
        """
        instances = super(BasePhotoGallery, self).save(commit)
        instances_pk = [instance.pk for instance in instances]
        bulkInsert = []
        item = Item.objects.get(pk=parent)

        for instance in instances:
            bulkInsert.append(Relationship(parent=item, child=instance, create_user=user, type='relation'))
        if bulkInsert:
            try:
               Relationship.objects.bulk_create(bulkInsert)
            except Exception:
                pass















