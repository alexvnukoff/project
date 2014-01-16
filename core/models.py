from django.db import models, transaction
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver, Signal
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.contrib.auth.models import Group, PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from core.hierarchy import hierarchyManager

from random import randint

from haystack.signals import BaseSignalProcessor
import hashlib

setAttValSignal = Signal()


#----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
#----------------------------------------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
            username=username)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email,
                                password=password,
                                username=username)
        user.is_admin = True
        user.save(using=self._db)
        return user

#----------------------------------------------------------------------------------------------------------
#             Class User define a new user for Django system
#----------------------------------------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True, db_index=True)
    username = models.CharField(verbose_name='Login',  max_length=255, unique=True)
    avatar = models.ImageField(verbose_name='Avatar',  upload_to='images/%Y/%m/%d', blank=True, null=True)
    first_name = models.CharField(verbose_name='Name',  max_length=255, blank=True)
    last_name = models.CharField(verbose_name='Surname',  max_length=255, blank=True)
    date_of_birth = models.DateField(verbose_name='Birth day',  blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
       return self.is_admin

#----------------------------------------------------------------------------------------------------------
#             Class Dictionary defines dictionary for attributes in application
#----------------------------------------------------------------------------------------------------------
class Dictionary(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title

    def getSlotsList(self):
        '''
        Return queryset of Slots  associated with dictionary
        '''
        slots = Slot.objects.filter(dict=self.id)
        return slots

    def createSlot(self, title):
        '''
        Create new Slot
        '''
        slot = Slot(title=title, dict=self)
        slot.save()

    def updateSlot(self,oldTitle,newTitle):
        '''
        Update Slot
        '''
        Slot.objects.filter(dict__id=self.id, title=oldTitle).update(title=newTitle)


    def deleteSlot(self,slotTitle):
        '''
        Delete slot
        '''
        slot = Slot.objects.get(dict=self.id,title=slotTitle)
        slot.delete()

#----------------------------------------------------------------------------------------------------------
#             Class Slot defines row in dictionary for attributes in application
#----------------------------------------------------------------------------------------------------------
class Slot(models.Model):
    title = models.CharField(max_length=128)
    dict = models.ForeignKey(Dictionary, related_name='slot')

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("title", "dict")

#----------------------------------------------------------------------------------------------------------
#             Class Attribute defines attributes for Item in application
#----------------------------------------------------------------------------------------------------------
class Attribute(models.Model):
    title = models.CharField(max_length=128)
    TYPE_OF_ATTRIBUTES = (
        ('Str', 'String'),

        ('Chr', 'Char'),
        ('Img', 'Image'),
        ('Bin', 'Boolean'),
        ("Dat", "Date"),
        ("Eml", "Email"),
        ("Fph", 'FilePath'),
        ("Ffl", "FileField"),
        ("Flo", "FloatField"),
        ("Dec", "Integer"),
        ("Ip", 'IpField'),
        ("Tm", 'TimeField'),
        ("Url", "URLField"),
        ("Sdt", "SplitDateTimeField"))
    type = models.CharField(max_length=3, choices=TYPE_OF_ATTRIBUTES)

    dict = models.ForeignKey(Dictionary, related_name='attr', null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ("title", "type")


    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class AttrTemplate defines default attributes for specific Item class
#----------------------------------------------------------------------------------------------------------
class AttrTemplate(models.Model):
    required = models.BooleanField(default=False)
    classId = models.ForeignKey(ContentType)
    attrId = models.ForeignKey(Attribute)

    def __str__(self):
        return "Class Name:   " + self.classId.name + "    attribute: " + self.attrId.title

    class Meta:
        unique_together = ("classId", "attrId")

#----------------------------------------------------------------------------------------------------------
#             Class State defines current state for particular item instance
#----------------------------------------------------------------------------------------------------------
class State(models.Model):
    title = models.CharField(max_length=128, unique=True)
    perm = models.ForeignKey(Group, related_name='state', null=True)

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Process defines process which is attached to particular Item
#----------------------------------------------------------------------------------------------------------
class Process(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Action defines member of the process, which is attached to particular Item
#----------------------------------------------------------------------------------------------------------
class Action(models.Model):
    title = models.CharField(max_length=128, unique=True)
    papa = models.ForeignKey(Process, related_name='action')
    child_proc = models.ForeignKey(Process, related_name='start_node', default=0) #handle to child process

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class ActionPath defines connection between two Actions in Process
#----------------------------------------------------------------------------------------------------------
class ActionPath(models.Model):
    title = models.CharField(max_length=128, unique=True)
    source = models.ForeignKey(Action, related_name='act2path')
    target = models.ForeignKey(Action, related_name='path2act')

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Item defines basic primitive for application objects
#----------------------------------------------------------------------------------------------------------
class Item(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    member = models.ManyToManyField('self', through='Relationship', symmetrical=False, null=True, blank=True)
    status = models.ForeignKey(State, null=True, blank=True)
    proc = models.ForeignKey(Process, null=True, blank=True)
    sites = models.ManyToManyField(Site)
    community = models.ForeignKey(Group, null=True, blank=True)

    objects = models.Manager()
    hierarchy = hierarchyManager()

    create_user = models.ForeignKey(User, related_name='owner2item')
    create_date = models.DateTimeField(auto_now_add=True)
    update_user = models.ForeignKey(User, null=True, blank=True, related_name='user2item')
    update_date = models.DateField(null=True, blank=True)

    class Meta:
        permissions = (
            ("read_item", "Can read item"),
        )

    #def __init__(self, name):
    #   title = name

    def __str__(self):
        return self.getName()

    def getName(self):
        name = self.getAttributeValues('NAME')
        return name[0] if name else '{EMPTY}'

    def getItemInstPermList(self, user):
        '''
            Returns list of permissions for given User for given Item's instance
            Example:
                usr = User.objects.get(pk=21)           # read usr from database
                comp = Company.objects.get(pk=2)        # read comp from database
                list = comp.getItemInstPermList(usr)    # get list of permissions for usr-comp
        '''

        group_list = []
        if user == self.create_user: # is user object's owner?
            group_list.append('Owner')
            group_list.append('Admin')
            if self.status.perm: # is there permissions group for current object's state?
                group_list.append(self.status.perm.name)
            else: # no permissions group for current state, attach Staff group
                group_list.append('Staff')
        else:
            if user == self.update_user or user.groups.filter(name=self.community.name): # is user community member?
                if user.is_admin: # has user admin flag?
                    group_list.append('Admin')
                    if self.status.perm: # is there permissions group for current object's state?
                        group_list.append(self.status.perm.name)
                    else: # no permissions group for current state, attach Staff group
                        group_list.append('Staff')
                else:
                    if self.status.perm: # is there permissions group for current object's state?
                        group_list.append(self.status.perm.name)
                    else: # no permissions group for current state, attach Staff group
                        group_list.append('Staff')
        # get all permissions from all related groups for current type of item
        obj_type = self.__class__.__name__ # get current object's type
        obj_type = obj_type.lower()
        perm_list = [p['permissions__codename'] for p in Group.objects.filter(name__in=group_list,\
                    permissions__codename__contains=obj_type).values('permissions__codename')]
        # attach user's private permissions
        perm_list += [p.codename for p in user.user_permissions.filter(codename__contains=obj_type).all()]
        perm_list = list(set(perm_list)) # remove duplicated keys in permissions list
        return perm_list

    @staticmethod
    def getItemsAttributesValues(attr, items): #TODO: Jenya add doc
        '''
           Return values of attribute list in items list
        '''

        if not isinstance(attr, tuple):
            attr = tuple(attr)

        if not isinstance(items, tuple):
            items = tuple(items)

        values = Value.objects.filter(attr__title__in=attr, item__in=items).order_by("item")

        values = list(values.values("title", "attr__title", "item__title", "item"))

        valuesAttribute = {}

        for valuesDict in values:
            if valuesDict['item'] not in valuesAttribute:
                valuesAttribute[valuesDict['item']] = {'title': [valuesDict['item__title']]}

            if valuesDict['attr__title'] not in valuesAttribute[valuesDict['item']]:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']] = []

            valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(valuesDict['title'])

        return valuesAttribute

    def getAttributeValues(self, *attr): #TODO: Jenya add doc, and chang usage
        '''
           Return values of attribute list in specific Item
           Example item = News.getAttributeValues("NAME", "DETAIL_TEXT)
           will return :   item = {NAME:['name'] , DETAIL_TEXT:['content']}
        '''

        values = Value.objects.filter(attr__title__in=attr, item=self.id)
        values = list(values.values("title", "attr__title"))

        valuesAttribute = {}

        for valuesDict in values:

            if valuesDict['attr__title'] not in valuesAttribute:
                valuesAttribute[valuesDict['attr__title']] = []

            valuesAttribute[valuesDict['attr__title']].append(valuesDict['title'])

        if len(valuesAttribute) == 0:
            return False

        if(len(attr) > 1):
            return valuesAttribute
        else:
            return valuesAttribute[attr[0]]

    @transaction.atomic
    def setAttributeValue(self, attrWithValues):
        '''
            Set values for attributes (mass)
            Methods set attribute's values for the item
            The parameter "attrWithValues" should be a dictionary
             you can pass many values for one attribute by passing list as dictionary value
                Example:
                    attr = {
                            'Name': 'Company Example'
                            'PhoneNumber': ['123-321-456','789-654-228']
                    }

                    Company(pk=1).setAttributeValue(attr)
                    //It will set the value for attribute "Name" of item = [Company=1] to "Company Example"
                    //and will set many values for attribute "PhoneNumber" item = [Company=1]
        '''
        if not isinstance(attrWithValues, dict) or not attrWithValues :
            raise ValueError

        queries = []
        bulkInsert = []
        attributes = attrWithValues.keys()
        existsAttributes = Attribute.objects.filter(title__in=attributes).all()

        if len(existsAttributes) != len(attrWithValues):
            raise ValueError

        for attr in attributes:
            attributeObj = existsAttributes.get(title=attr)
            dictID = attributeObj.dict_id
            attr = attributeObj.title
            values = attrWithValues[attr]

            if not isinstance(values, list):
                values = [values]

            for value in values:

                if dictID is None:
                    bulkInsert.append(Value(title=value, item=self, attr=attributeObj))
                else:
                    #security
                    dictID = int(dictID)
                    valueID = int(value)

                    #check if dictionary slot exists for this dictionary - creating conditions
                    queries.append('Q(dict=' + str(dictID) + ', pk=' + str(valueID) + ')')

        if len(queries) > 0:
            #check if dictionary slot exists for this dictionary - using conditions
            filter_or = ' | '.join(queries)
            attributesValue = Slot.objects.filter(eval(filter_or)).values('dict__attr__title','title','dict__attr__id')

            if len(attributesValue) < len(queries):
                raise ValueError

            for attribute in attributesValue:
                value = attribute['title']
                attrID = attribute['dict__attr__id']
                attributeObj = existsAttributes.get(pk=attrID)

                bulkInsert.append(Value(title=value, item=self, attr=attributeObj))

        try:
            with transaction.atomic():
                Value.objects.filter(attr__title__in=attributes, item=self.id).delete()
                Value.objects.bulk_create(bulkInsert)
        except IntegrityError:
            raise Exception

        setAttValSignal.send(self._meta.model, instance=self)

        return True

    def getSiblings(self, includeSelf=True):
        '''
            Get siblings in hierarchy
            The method returns hierarchical siblings of the current Item
            by default it will include the current Item
                Example: Department(pk=1).getSiblings()
                    //Returns all siblings of Department = 1 and will include the department itself
            If you will set the parameter "includeSelf" it will not include the item itself
                Example: Department(pk=1).getSiblings(False)//will not include Department=1
        '''

        try:
            parent = Item.hierarchy.getParent(self.pk)
        except Exception:
            return False
        else:
            if includeSelf is True:
                return self._meta.model.hierarchy.getChild(parent)
            else:
                return self._meta.model.hierarchy.getChild(parent).exclude(pk=self.pk)

    def getRelationChildren(self, getItemInstance=True):
        '''
            Get list of ancestors in hierarchy
            List contains item objects
        '''
        translation = {'rev_level': 'level'}

    def getRelatedChildForParent(cls):
        parent = 0
        return cls._meta.model.objects.filter(c2p__parent_id=parent, c2p__type="rel")

#----------------------------------------------------------------------------------------------------------
#             Class Relationship defines relationships between two Items
#----------------------------------------------------------------------------------------------------------
class Relationship(models.Model):
    title = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey(Item, related_name='p2c')
    child = models.ForeignKey(Item, related_name='c2p')
    TYPE_OF_RELATIONSHIP = (
        ('rel', 'Relation'),
        ('hier', 'Hierarchy'),)
    type = models.CharField(max_length=10, choices=TYPE_OF_RELATIONSHIP)

    qty = models.FloatField(null=True, blank=True)
    create_date = models.DateField(auto_now_add=True)
    create_user = models.ForeignKey(User)

    class Meta:
        unique_together = ("parent", "child")

    def __str__(self):
        return self.title

    @staticmethod
    def setRelRelationship(parent, child, user):
        Relationship.objects.create(title=randint(10000, 9999999), parent=parent, child=child, create_user=user, type="rel")       #TODO Jenya remove title

#----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
#----------------------------------------------------------------------------------------------------------
class Value(models.Model):
    title = models.TextField()
    attr = models.ForeignKey(Attribute, related_name='attr2value')
    item = models.ForeignKey(Item, related_name='item2value')
    sha1_code = models.CharField(max_length=40, blank=True) #The length of SHA-1 code is always 20x2 (2 bytes for symbol in Unicode)

    class Meta:
        unique_together = ("sha1_code", "attr", "item")
        #db_tablespace = 'TPP_CORE_VALUES'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.sha1_code = hashlib.sha1(str(self.title).encode()).hexdigest()
        super(Value, self).save()

    def __str__(self):
        return self.title

    def get(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
#             Indexing signal receivers
#----------------------------------------------------------------------------------------------------------
class ItemIndexSignal(BaseSignalProcessor):
    """
    Allows for observing when saves/deletes fire & automatically updates the
    search engine appropriately.
    """
    def setup(self):
        # Naive (listen to all model saves).
        setAttValSignal.connect(self.handle_save)
        models.signals.post_delete.connect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then hooking up signals only for those.

    def teardown(self):
        # Naive (listen to all model saves).
        setAttValSignal.disconnect(self.handle_save)
        models.signals.post_delete.disconnect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then disconnecting signals only for those.



#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
#             Signal receivers
#----------------------------------------------------------------------------------------------------------
@receiver(pre_delete, sender=Item)
def itemPreDelete(instance, **kwargs):

    Relationship.objects.filter(Q(child=instance.pk) | Q(parent=instance.pk)).delete()
    Value.objects.filter(item=instance.pk).delete()


@receiver(post_delete, sender=Item)
def itemPostDelete(instance, **kwargs):
    if instance.community:
        Group.objects.get(pk=instance.community.pk).delete()
