from django.db import models, transaction
from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.contrib.auth.models import Group, PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from core.hierarchy import hierarchyManager
from copy import copy
from random import randint
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import warnings
from collections import OrderedDict
from operator import itemgetter

from django.utils.timezone import now
import datetime
import hashlib
from django.utils.timezone import now
from django.shortcuts import render_to_response
from tpp.SiteUrlMiddleWare import get_request

def createHash(string):
    return hashlib.sha1(str(string).encode()).hexdigest()


#----------------------------------------------------------------------------------------------------------
#             Class UserManager defines manager for user
#----------------------------------------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):

        request = get_request()

        if request:
            ip = request.META['REMOTE_ADDR']
        else: # for data migration as batch process generate random IP address 0.rand().rand().rand() for avoiding bot checking
            ip = '0.'+str(randint(0, 255))+'.'+str(randint(0, 255))+'.'+str(randint(0, 255))

        time = now() - datetime.timedelta(minutes=1)
        users = User.objects.filter(ip=ip, date_joined__gt=time)
        if users:
            raise ValueError("Bot")
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
            username=username, ip=ip)

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
class SiteProfileNotAvailable(Exception):
    pass

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True, db_index=True)
    username = models.CharField(verbose_name='Login',  max_length=255, unique=True)
    avatar = models.ImageField(verbose_name='Avatar',  upload_to='images/%Y/%m/%d', blank=True, null=True)
    first_name = models.CharField(verbose_name='Name',  max_length=255, blank=True)
    last_name = models.CharField(verbose_name='Surname',  max_length=255, blank=True)
    date_of_birth = models.DateField(verbose_name='Birth day',  blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    ip = models.GenericIPAddressField()

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        if obj is None:
            return PermissionsMixin.has_perms(self, perm_list)
        else:
            group_list = []
            if self == obj.create_user: # is user object's owner?
                group_list.append('Owner')
                group_list.append('Admin')
                if obj.status.perm: # is there permissions group for current object's state?
                    group_list.append(obj.status.perm.name)
                else: # no permissions group for current state, attach Staff group
                    group_list.append('Staff')
            else:
                if self == obj.update_user or self.groups.filter(name=obj.community.name): # is user community member?
                    if self.is_admin: # has user admin flag?
                        group_list.append('Admin')
                        if obj.status.perm: # is there permissions group for current object's state?
                            group_list.append(obj.status.perm.name)
                        else: # no permissions group for current state, attach Staff group
                            group_list.append('Staff')
                    else:
                        if obj.status.perm: # is there permissions group for current object's state?
                            group_list.append(obj.status.perm.name)
                        else: # no permissions group for current state, attach Staff group
                            group_list.append('Staff')
            # get all permissions from all related groups for current type of item
            obj_type = obj.__class__.__name__ # get current object's type
            obj_type = obj_type.lower()
            p_list = [p['permissions__codename'] for p in Group.objects.filter(name__in=group_list,\
                            permissions__codename__contains=obj_type).values('permissions__codename')]
            # attach user's private permissions
            p_list += [p['codename'] for p in self.user_permissions.filter(codename__contains=obj_type).values('codename')]
            p_list = list(set(p_list)) #remove duplicated keys in permissions list
            for i in perm_list:
                if i not in p_list:
                    return False
            return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
       return self.is_admin

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            DeprecationWarning, stacklevel=2)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

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

    def updateSlot(self, oldTitle, newTitle):
        '''
        Update Slot
        '''
        Slot.objects.filter(dict__id=self.id, title=oldTitle).update(title=newTitle)

    def getSlotID(self, title):
        slot = Slot.objects.get(dict=self.id, title=title)
        return self.id
    def deleteSlot(self, slotTitle):
        '''
        Delete slot
        '''
        slot = Slot.objects.get(dict=self.id, title=slotTitle)
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
    f_order = models.BooleanField(default=False)# set in True if attribute participate in sort list of the fields in
                                                # setup view form in User's Cabinet
    f_cache = models.BooleanField(default=False)# reserved field for fast access to item's main attributes
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

    @staticmethod
    @transaction.atomic
    def setHierarchy(parent, child):
        '''
            Set hierarchical relationship between parent and list of child
            you should pass an instance of a parent object to a "parent" parameter
                Example: comp = Company.objects.get(pk=1)
                            Departments.hierarchy.setHierarchy(comp, [3,2,4,5])
                It will create an hierarchical relation between Company = 1
                and Departments pk__in=[3,2,4,5]
        '''

        if not isinstance(parent, Item):
            raise ValueError("Parent is not Item instance")

        if not isinstance(child, list):
            child = list(child)

        num = Item.objects.filter(~Q(c2p__parent_id=parent, c2p__type="hier", p2c__child_id=parent), pk__in=child).count()

        if num != len(child):
            raise ValueError('Wrong child count')

        bulkInsert = []

        for item in child:
            title = [str(parent.pk),'hier',str(item)]
            bulkInsert.append(Relationship(title='-'.join(title), parent_id=parent.pk,
                                           child_id=item, type="hier", create_user_id=1))

        try:
            with transaction.atomic():
                Relationship.objects.bulk_create(bulkInsert)
        except IntegrityError as e:
            raise e

        return True

    def getItemInstPermList(self, user):
        '''
            Returns list of permissions for given User for given Item's instance
            Example:
                usr = User.objects.get(pk=21)           # read usr from database
                comp = Company.objects.get(pk=2)        # read comp from database
                list = comp.getItemInstPermList(usr)    # get list of permissions for usr-comp pair
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
        perm_list += [p['codename'] for p in user.user_permissions.filter(codename__contains=obj_type).values('codename')]
        perm_list = list(set(perm_list)) # remove duplicated keys in permissions list
        return perm_list

    @staticmethod

    def getItemsAttributesValues(attr, items, fullAttrVal=False):

        '''
           Return values of attribute list for items list
           Example item = News.getAttributeValues(("NAME", "DETAIL_TEXT", "TAGS"), (1,2))
           will return :
                {
                    '1':
                        {
                            'NAME': ['news title']
                            'DETAIL_TEXT': ['Text of the news']
                            'TAGS': ['TAG1', 'TAG2']
                        }
                    '2':
                        {
                            'NAME': ['news title2']
                            'DETAIL_TEXT': ['Text of the news2']
                            'TAGS': ['TAG3']
                        }
                }
        '''
        if not isinstance(attr, tuple):
            attr = (attr,)

        if not isinstance(items, tuple):
            items = tuple(items)



        #TODO: Jenya maybe change items to queryset
        valuesObj = Value.objects.filter(Q(end_date__gt=now()) | Q(end_date__isnull=True),
                                         Q(start_date__lte=now()) | Q(start_date__isnull=True),
                                         attr__title__in=attr, item__in=items)

        getList = ["title", "attr__title", "item__title", "item"]

        if fullAttrVal:
            getList += ['start_date','end_date']

        values = list(valuesObj.values(*getList))

        valuesAttribute = {}


        for key in range(0, len(items)):
            if items[key] in valuesAttribute:
                continue

            valuesAttribute[items[key]] = key

        valuesAttribute = OrderedDict(sorted(((k, v) for k, v in valuesAttribute.items()), key=lambda i: i[1]))

        for valuesDict in values:

            if not isinstance(valuesAttribute[valuesDict['item']], dict):

                valuesAttribute[valuesDict['item']] = {}

            if valuesDict['attr__title'] not in valuesAttribute[valuesDict['item']]:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']] = []

            if fullAttrVal:
                attrValDict = {
                    'start_date': valuesDict['start_date'],
                    'end_date': valuesDict['end_date'],
                    'title': valuesDict['title']
                }
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(attrValDict)
            else:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(valuesDict['title'])

        return valuesAttribute

    def getAttributeValues(self, *attr, fullAttrVal=False):
        '''
           Return values of attribute list for specific Item
           Example item = News.getAttributeValues("NAME", "DETAIL_TEXT")
           will return :   item = {NAME:['name'] , DETAIL_TEXT:['content']}
        '''

        values = Value.objects.filter(Q(end_date__gt=now()) | Q(end_date__isnull=True),
                                      Q(start_date__lte=now()) | Q(start_date__isnull=True),
                                      attr__title__in=attr, item=self.id)
        getList = ["title", "attr__title"]

        if fullAttrVal:
            getList += ['start_date','end_date']

        values = list(values.values(*getList))

        valuesAttribute = {}

        for valuesDict in values:

            if valuesDict['attr__title'] not in valuesAttribute:
                valuesAttribute[valuesDict['attr__title']] = []

            if fullAttrVal:
                attrValDict = {
                    'start_date': valuesDict['start_date'],
                    'end_date': valuesDict['end_date'],
                    'title': valuesDict['title']
                }
                valuesAttribute[valuesDict['attr__title']].append(attrValDict)
            else:
                valuesAttribute[valuesDict['attr__title']].append(valuesDict['title'])

        if len(valuesAttribute) == 0:
            return []

        if(len(attr) > 1):
            return valuesAttribute
        else:
            return valuesAttribute[attr[0]]

    @transaction.atomic
    def setAttributeValue(self, attrWithValues, user):

        '''
            Set values for list of attributes
            The parameter "attrWithValues" should be a dictionary
            and you should pass the user object
             you can pass many values for one attribute by passing list as dictionary value
                Example:
                    attr = {
                                'NAME': 'bla',
                                'DISCOUNT': [95,
                                    {
                                        'end_date': now(),
                                        'title': 50,
                                        'create_user': request.user #not required
                                    }
                                ]
                            }
                    Company(pk=1).setAttributeValue(attr, request.user)
        '''
        if not isinstance(attrWithValues, dict) or not attrWithValues:
            raise ValueError

        queries = []
        bulkInsert = []
        attributes = copy(attrWithValues).keys()
        uniqDict = {}

        #get all passed attributes
        existsAttributes = Attribute.objects.filter(title__in=attributes).all()

        if len(existsAttributes) != len(attrWithValues):
            raise ValueError("Attribute does not exists")

        for attr in attributes:
            attributeObj = existsAttributes.get(title=attr)
            dictID = attributeObj.dict_id
            values = attrWithValues[attr]

            if not isinstance(values, list):
                values = [values]

            for value in values:

                if isinstance(value, dict) and "title" not in value:
                    raise ValueError('Value is missing')

                if dictID is None:

                    if attr in attrWithValues:
                        del attrWithValues[attr]

                    if isinstance(value, dict):
                        if 'create_user' not in value:
                            value['create_user'] = user

                        value['sha1_code'] = createHash(value['title'])

                        bulkInsert.append(Value(item=self, attr=attributeObj, **value))
                    else:
                        bulkInsert.append(Value(title=value, item=self, attr=attributeObj,
                                                create_user=user, sha1_code=createHash(value)))
                else:
                    #security
                    dictID = int(dictID)

                    if isinstance(value, dict):
                        valueID = int(value['title'])
                    else:
                        valueID = int(value)

                    if dictID not in uniqDict:
                        uniqDict[dictID] = {}

                    if valueID in uniqDict[dictID]:
                        continue
                    else:
                        uniqDict[dictID][str(valueID)] = ''
                        #check if dictionary slot exists for this dictionary - creating conditions
                        queries.append('Q(dict=' + str(dictID) + ', pk=' + str(valueID) + ')')

        if len(queries) > 0:
            #check if dictionary slot exists for this dictionary - using conditions
            filter_or = ' | '.join(queries)
            attributesValue = Slot.objects.filter(eval(filter_or)).values('dict__pk','title','pk')

            if len(attributesValue) < len(queries):
                raise ValueError('Wrong number of dict values')

            for value in attributesValue:
                uniqDict[value['dict__pk']][value['pk']] = value['title']

            for attribute in attrWithValues.keys():
                values = attrWithValues[attribute]
                attributeObj = existsAttributes.get(title=attribute)
                dictID = attributeObj.dict_id

                if not isinstance(values, list):
                    values = [values]

                for value in values:
                    if isinstance(value, dict):
                        value['title'] = uniqDict[dictID][int(value['title'])]

                        if 'create_user' not in value:
                            value['create_user'] = user

                        value['sha1_code'] = createHash(value['title'])

                        bulkInsert.append(Value(item=self, attr=attributeObj, **value))
                    else:
                        value = uniqDict[dictID][int(value)]
                        bulkInsert.append(Value(title=value, item=self, attr=attributeObj,
                                                create_user=user, sha1_code=createHash(value)))

        try:
            with transaction.atomic():
                Value.objects.filter(attr__title__in=attributes, item=self.id).delete()
                Value.objects.bulk_create(bulkInsert)
        except IntegrityError as e:
            raise e
        #send signal to search frontend
        from core.signals import setAttValSignal
        setAttValSignal.send(self._meta.model, instance=self)

        return True

    def getSiblings(self, includeSelf=True):
        '''
            Get siblings in hierarchy
            The method returns hierarchical siblings of the Item
            by default it will include the current Item
                Example: Dep = Department.objects.get(pk=3)
                         Dep.getSiblings()
                    #Returns all siblings of Department = 1 and will include the department itself
            If you will set the parameter "includeSelf"  to `False` it will not include the item itself
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

#----------------------------------------------------------------------------------------------------------
#             Class Relationship defines relationships between two Items
#----------------------------------------------------------------------------------------------------------
class Relationship(models.Model):
    title = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey(Item, related_name='p2c')
    child = models.ForeignKey(Item, related_name='c2p')
    TYPE_OF_RELATIONSHIP = (
        ('rel', 'Relation'),
        ('hier', 'Hierarchy'),
    )
    type = models.CharField(max_length=10, choices=TYPE_OF_RELATIONSHIP, null=False, blank=False)

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
    #The length of SHA-1 code is always 20x2 (2 bytes for symbol in Unicode)
    sha1_code = models.CharField(max_length=40, blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User, related_name='creator')

    class Meta:
        unique_together = ("sha1_code", "attr", "item")
        #db_tablespace = 'TPP_CORE_VALUES'

    def __str__(self):
        return self.title

    def get(self):
        return self.title


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

@receiver(pre_save, sender=Value)
def valueSaveHashCode(instance, **kwargs):
    instance.sha1_code = createHash(instance.title)

@receiver(pre_save, sender=Relationship)
def generateTitleField(instance, **kwargs):
    assert instance.parent.pk != instance.child.pk, 'You cannot create an relationship for class instance with itself!'
    instance.title = 'RS_' + str(instance.type).upper() + '_PARENT:' + str(instance.parent.pk) + '_CHILD:'+ str(instance.child.pk)
