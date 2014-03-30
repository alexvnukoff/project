from django import forms
import os
import uuid
from django.forms.models import BaseModelFormSet
from django.contrib.contenttypes.models import ContentType
from core.models import AttrTemplate, Dictionary, Item, Relationship, Attribute, Value
from appl.models import *

from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile,  FieldFile, FileField
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.forms.models import modelformset_factory
from django.db import transaction
from core.amazonMethods import add, delete, addFile, deleteFile
from appl import func
from django.db.models import Q
from PIL import Image



class ItemForm(forms.Form):

    def __init__(self, item, values=None, id=None, addAttr=None):
        '''
        Overriding of BaseForm __init__
        parameters:
        item = class Name of Item (News, Company)
        values = Dict that contain values to forms field (Post)

        id = pk, of specific item , if needs update of values
        Example :
        form = Form("News" , values = request.POST, id = 4)(Update News with id 4 by values)
        '''
        self.to_delete_if_exception = []
        self.document_to_delete_if_exception = []
        self.item = item
        self.id = id
        self.file_to_delete = []
        self.document_to_delete = []



        super(ItemForm, self).__init__()
        # Get id of ContentType of specific Item
        object_id = ContentType.objects.get(model=str(item).lower()).id
        # Get default attributes of Item

        attributess = AttrTemplate.objects.filter(classId=object_id).select_related("attrId", "attrId__dict")
        if addAttr:
            attributes = Attribute.objects.filter(Q(attrTemplate__classId=object_id) | Q(title__in=addAttr.keys())).\
              select_related("attrTemplate", "dict").distinct()
        else:
            attributes = Attribute.objects.filter(attrTemplate__classId=object_id).select_related("attrTemplate", "dict")


         #IF id parameter isn't null , and we want update form ,need to populate field with initial values
        if self.id:
            self.obj = globals()[item].objects.get(id=self.id)
        if self.id and not values:
            attrs = [str(attr.title) for attr in attributes]
            values = self.obj.getAttributeValues(*attrs)


        # Build form fields , depends on type of attribute
        for attribute in attributes:
            dictr = attribute.dict
            attr = attribute

            title = str(attr.title)
            if addAttr and title in addAttr:
                required = addAttr[title]
            else:
                required = attribute.attrTemplate.get(classId=object_id).required
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
                formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M',  '%m/%d/%Y',
                 '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M', '%m/%d/%y']
                self.fields[title] = forms.DateField(required=bool(required), input_formats=formats)
                self.fields[title].widget.input_type = 'date'
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

            #FileField
            if(attr.type == "Ffl") and dictr is None:
                self.fields[title] = forms.FileField(required=bool(required))
                self.fields[title].initial = value[0] if value and isinstance(value, list) else value
                if isinstance(value, list):
                    value = value[0]
                if value:

                    if not isinstance(value, InMemoryUploadedFile):
                           self.fields[title].initial = FieldFile(instance=None, field=FileField(), name=value)
                    else:
                           self.fields[title].initial = value
                    if self.id and self.obj:
                         file = self.obj.getAttributeValues(title) if self.id else ""
                         self.document_to_delete.extend(file)


                else:
                     file = self.obj.getAttributeValues(title) if self.id else ""
                     value = file[0] if self.id and file else ""

                     if values and values.get(title + '-CLEAR', False) and values[title + '-CLEAR'] == value:
                         self.fields[title].initial = ""
                         self.document_to_delete.append(values[title + '-CLEAR'])
                     else:
                         self.fields[title].initial = FieldFile(instance=None, field=FileField(), name=value) if value else ""




            #ImageField
            if(attr.type == "Img") and dictr is None:
                 self.fields[title] = forms.ImageField(required=bool(required))
                 value = value[0] if value and isinstance(value, list) else value

                 if value:
                    if isinstance(value, TemporaryUploadedFile):
                        self.fields[title].initial = value
                    elif not isinstance(value, InMemoryUploadedFile):
                           self.fields[title].initial = ImageFieldFile(instance=None, field=FileField(), name=value)
                    else:
                           self.fields[title].initial = value
                    if self.id and self.obj:
                         picture = self.obj.getAttributeValues(title) if self.id else ""
                         self.file_to_delete.extend(picture)
                 else:
                     picture = self.obj.getAttributeValues(title) if self.id else ""
                     value = picture if self.id and picture else [""]
                     if values and values.get(title + '-CLEAR', False) and values[title + '-CLEAR'] == value[0]:
                         self.fields[title].initial = ""
                         self.file_to_delete.append(values[title + '-CLEAR'])
                     else:
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
                if isinstance(self.fields[title].initial, TemporaryUploadedFile):
                  self._errors[title] = _('Image size must be less than 2 mb ')
                if ((isinstance(self.fields[title], forms.ImageField) or isinstance(self.fields[title], forms.FileField))
                    and not isinstance(self.fields[title].initial, InMemoryUploadedFile) and self.fields[title].initial):


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

    @transaction.atomic
    def save(self, user, site_id, dates=None, disableNotify=False, sizes=None):
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
        sid = transaction.savepoint()

        try:
            if not self.id:
                site = site_id
                self.obj = globals()[self.item](create_user=user)
                self.obj.save()
                self.obj.sites.add(site_id)
            else:
                self.obj = globals()[self.item].objects.get(id=self.id)
               # self.obj.name = self.fields['NAME'].initial
                #self.obj.title = self.fields['NAME'].initial
                self.obj.save()
            attrValues = {}
            attrValues_to_delte = []

            for title in self.fields:
                if (isinstance(self.fields[title], forms.FileField) or isinstance(self.fields[title], forms.ImageField))\
                        and self.fields[title].initial and isinstance(self.fields[title].initial, InMemoryUploadedFile):
                    self._save_file(self.fields[title].initial, title, user, path_to_images, sizes=sizes)
                    # If Field is Image that call save_file method

                if dates and title in dates:
                    attrValues[title] = {"title": self.fields[title].initial, 'start_date': dates[title][0],
                                         'end_date': dates[title][1]}
                else:
                    if self.fields[title].initial:
                        attrValues[title] = self.fields[title].initial
                    else:
                        attrValues_to_delte.append(title)


            self.obj.setAttributeValue(attrValues, user)

            if len(attrValues_to_delte) > 0:
                Value.objects.filter(item=self.obj, attr__title__in=attrValues_to_delte).delete()


            if len(self.file_to_delete) > 0:
               delete(self.file_to_delete)
            if len(self.document_to_delete) > 0:
                 deleteFile(self.document_to_delete)

        except Exception as e:

            transaction.savepoint_rollback(sid)

            if disableNotify is False:
                func.notify("error_creating", 'notification', user=user)

            if len(self.to_delete_if_exception) > 0:
                 delete(self.to_delete_if_exception)
            if len(self.document_to_delete_if_exception) > 0:
                 deleteFile(self.document_to_delete)

            return False

        else:
            transaction.savepoint_commit(sid)
            return self.obj


    def _save_file(self, file, title, user, path='', sizes=None):
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

        file = '%s/%s' % (settings.MEDIA_ROOT, str(path) + str(filename))

        if isinstance(self.fields[title], forms.ImageField):
            filename = add(imageFile=file, sizes=sizes)
            self.to_delete_if_exception.append(filename)
            self.fields[title].initial = ImageFieldFile(instance=None, field=FileField(),  name=filename)

        if isinstance(self.fields[title], forms.FileField) and not isinstance(self.fields[title], forms.ImageField):
            filename = addFile(file=file)
            self.document_to_delete_if_exception.append(filename)
            self.fields[title].initial = FieldFile(instance=None, field=FileField(),  name=filename)


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
        self.toDelete = []
        self.files_to_delete = []
        super(BasePhotoGallery, self).__init__(*args, **kwargs)
        post = args[0] if args else False
        files = args[1] if args and len(args) > 0 else False

        if post and post.getlist("del[]"):
            self.toDelete.extend(post.getlist("del[]"))

        if post and files:
            for i in range(0, int(post['form-TOTAL_FORMS'])):

                if post.get('form-'+str(i), False) and files.get('form-'+str(i)+'-photo', False):
                    item = post['form-'+str(i)]
                    self.toDelete.append(item)


        self.user = parent_id

        self.queryset = Gallery.objects.filter(c2p__parent_id=parent_id)
    @transaction.atomic
    def save(self, parent=None, user=None,  commit=False):
        """
        Method that create new Gallery , and set relationship with parent object
        Example :
        form.save(parent = 34 , user = request.user, commit =True)
        """
        if self.toDelete:
            items = Gallery.objects.filter(pk__in=self.toDelete).distinct()
            self.toDelete = [item.photo.name for item in items]
            items.delete()
        self.user = user
        sid = transaction.savepoint()

        try:
            instances = super(BasePhotoGallery, self).save(commit)
            for instance in instances:
                instance.create_user = self.user
                instance.save()

            for instance in instances:
                name = instance.photo.file.name
                instance.photo.close()
                file = add(imageFile=name)
                self.files_to_delete.append(file)
                instance.photo = file
                instance.save()


            instances_pk = [instance.pk for instance in instances]
            bulkInsert = []
            item = Item.objects.get(pk=parent)
            for instance in instances:
                bulkInsert.append(Relationship(parent=item, child=instance, create_user=user, type='dependence'))
            if bulkInsert:
                Relationship.objects.bulk_create(bulkInsert)
        except Exception:
            transaction.savepoint_rollback(sid)
            func.notify("error_creating", 'notification', user=user)
            if len(self.files_to_delete) > 0:
               delete(self.files_to_delete)

        else:
            transaction.savepoint_commit(sid)
            if self.toDelete:
                delete(self.toDelete)




class BasePages(BaseModelFormSet):
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

        self.toDelete = []
        self.files_to_delete = []
        super(BasePages, self).__init__(*args, **kwargs)
        post = args[0] if args else False
        files = args[1] if args and len(args) > 0 else False

        if post and post.getlist("del[]"):
            self.toDelete.extend(post.getlist("del[]"))





        if post.get('pages-0-content', False):
            super(BasePages, self).save(False)
        else:
            self.queryset = AdditionalPages.objects.filter(c2p__parent_id=parent_id)


    @transaction.atomic
    def save(self, parent=None, user=None,  commit=False):
        """
        Method that create new AdditionalPage , and set relationship with parent object
        Example :
        form.save(parent = 34 , user = request.user, commit =True)
        """
        sid = transaction.savepoint()
        try:
            AdditionalPages.objects.filter(c2p__parent=parent).delete()
            instances = super(BasePages, self).save(commit)
            for instance in instances:
                instance.create_user = user
                instance.save()
                instance.setAttributeValue({'NAME': instance.title, 'DETAIL_TEXT': instance.content}, user=user)

            instances_pk = [instance.pk for instance in instances]
            bulkInsert = []
            item = Item.objects.get(pk=parent)
            for instance in instances:
                bulkInsert.append(Relationship(parent=item, child=instance, create_user=user, type='dependence'))
            if bulkInsert:
                Relationship.objects.bulk_create(bulkInsert)
        except Exception as e:

            transaction.savepoint_rollback(sid)
            func.notify("error_creating", 'notification', user=user)
            if len(self.files_to_delete) > 0:
               delete(self.files_to_delete)

        else:
            transaction.savepoint_commit(sid)
            if self.toDelete:
                delete(self.toDelete)























