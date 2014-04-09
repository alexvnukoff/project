from django.db import IntegrityError, transaction, models
from django.db.models import Q
from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import get_language, ugettext_lazy as _
from django.template.defaultfilters import slugify
from copy import copy
from collections import OrderedDict
from core.hierarchy import hierarchyManager
from random import randint
from tpp.SiteUrlMiddleWare import get_request
from unidecode import unidecode
from django.core.cache import cache

import warnings
import datetime
import hashlib

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
    is_manager = models.BooleanField(default=False) #for enterprise content management
    is_commando = models.BooleanField(default=False) #for special purposes
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

    def has_perms(self, perm_list, obj):
        """
        Returns True if the User has all specified permissions perm_list for this object obj.
        """

        if self.is_superuser or self.is_commando:
            return True
        else:
            if obj:
                p_list = obj.getItemInstPermList(self)
                for i in perm_list:
                    if i not in p_list:
                        return False

                return True

            else:
                return False

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
        return slot.id

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
    attrId = models.ForeignKey(Attribute, related_name='attrTemplate')

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
class ItemManager(models.Manager):
    def get_active_related(self):
        '''
        Method filter active items that related to other items with dependense relationship
        example of usage :
        item = Item.active.get_active_related()
        '''
        return self.get_active()

    def get_active(self):
        '''
        Method return active items without relatiopnship:
        Example of usage:
        item = Item.active.get_active()
        '''
        return self.filter(Q(Q(end_date__gt=timezone.now()) | Q(end_date__isnull=True)), start_date__lte=timezone.now())\
            .exclude(Q(c2p__end_date__lte=timezone.now(), c2p__end_date__isnull=False) | Q(c2p__start_date__gt=now()), c2p__type='dependence')


class Item(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    member = models.ManyToManyField('self', through='Relationship', symmetrical=False, null=True, blank=True)
    status = models.ForeignKey(State, null=True, blank=True)
    proc = models.ForeignKey(Process, null=True, blank=True)
    sites = models.ManyToManyField(Site)
    community = models.ForeignKey(Group, null=True, blank=True)

    objects = models.Manager()
    hierarchy = hierarchyManager()
    active = ItemManager()

    create_user = models.ForeignKey(User, related_name='owner2item')
    create_date = models.DateTimeField(auto_now_add=True)
    update_user = models.ForeignKey(User, null=True, blank=True, related_name='user2item')
    update_date = models.DateField(null=True, blank=True)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (
            ("read_item", "Can read item"),
        )

    #def __init__(self, name):
    #   title = name

    @staticmethod
    def _activationRelated(itemList, eDate, sDate=None):
        '''
            Change start_date and end_date for depended items recursively

             list itemsList - Depended items
             datetime eDate - End date
             datetime sDate - Start Date (optional)

             should be called only from "activation" method
        '''

        if isinstance(itemList, int):
            itemList = [itemList]

        if not isinstance(itemList, list):
            raise ValueError('Depended items should be as list or int')

        rel = Relationship.objects.filter(parent__in=itemList, type="dependence")

        if not rel.exists():
            return False

        parents = rel.values_list('child', flat=True)
        parents = list(parents)

        fields = {'end_date': eDate}

        if sDate is not None:
            fields['start_date'] = sDate

        rel.update(**fields)

        Item._activationRelated(parents, eDate, sDate)


    def activation(self, eDate, sDate=None):
        '''
            Change start_date and end_date of the item and depended items
        '''

        fields = {'end_date': eDate}

        if sDate is not None:
            fields['start_date'] = sDate

        Item.objects.filter(pk=self.pk).update(**fields)
        self._activationRelated(self.pk, eDate, sDate)



    def reindexItem(self):
        '''
            Send reindex signal from item instance

            should be called just from item subclass instance
        '''

        if self.__class__.__name__ is 'Item':
            raise ValueError('Should be subclass of Item')

        #send signal to search frontend
        from core.signals import setAttValSignal
        setAttValSignal.send(self._meta.model, instance=self)


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

        num = Item.objects.filter(~Q(c2p__parent_id=parent, c2p__type="hierarchy", p2c__child_id=parent), pk__in=child).count()

        if num != len(child):
            raise ValueError('Wrong child count')

        bulkInsert = []

        for item in child:
            title = [str(parent.pk),'hierarchy',str(item)]
            bulkInsert.append(Relationship(title='-'.join(title), parent_id=parent.pk,
                                           child_id=item, type="hierarchy", create_user_id=1))

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
        is_commando = getattr(user, 'is_commando', False) #Anonymous User has not attribute 'is_commando'
        if user.is_superuser or is_commando or self.create_user == user:
            group_list.append('Owner')
            group_list.append('Admin')
            group_list.append('Staff')
        else:
            #whether there is a User Cabinet
            cabinet = getattr(user, 'cabinet', False) #Anonymous User has not attribute 'cabinet'
            if cabinet:
                #get Cabinet ID
                cab_pk = user.cabinet.filter(user=user).values('pk')
                #check is Cabinet belongs to any Organization
                if Item.objects.filter(c2p__parent__c2p__parent__organization__isnull=False, pk=cab_pk).exists():
                    #get Organization ID
                    org_lst = Item.objects.filter(p2c__child__p2c__child__p2c__child=cab_pk).values('pk')
                    #rs = None
                    for org_pk in org_lst:
                        # if object SELF belongs to the same Company or it is Company itself or belongs to User's TPP or to TPP's parent TPP...
                        if org_pk['pk'] == self.pk or \
                          Item.objects.filter(c2p__parent=org_pk['pk'], pk=self.pk).exists() or \
                          Item.objects.filter(c2p__parent__c2p__parent=org_pk['pk'], pk=self.pk).exists() or \
                          Item.objects.filter(c2p__parent__c2p__parent__c2p__parent=org_pk['pk'], pk=self.pk).exists():

                            rs = Relationship.objects.filter(parent__c2p__parent__c2p__parent=org_pk['pk'], \
                                                                child=cab_pk, type='hierarchy')
                            for r in rs:
                                if r.is_admin:
                                    group_list.append('Admin')
                                    group_list.append('Staff')
                                else:
                                    if self.status:
                                        if self.status.perm: # is there permissions group for current object's state?
                                            group_list.append(self.status.perm.name)
                                        else: # no permissions group for current state, attach Staff group
                                            group_list.append('Staff')

                        else: #User and SELF belongs to different Organization without any correlation
                            group_list = []

                else: # Cabinet still do not attach to any Organization
                    group_list = []
            else: # if User without Cabinet (before first login or unregistered)
                group_list = []

        # get all permissions from all related groups for current type of item
        group_list = list(set(group_list)) # remove duplicated keys in groups list
        perm_list = Group.objects.filter(name__in=group_list).values_list('permissions__codename', flat=True)

        perm_list = list(perm_list)

        # attach user's private permissions
        #perm_list += list(user.user_permissions.filter(codename__contains=obj_type).values_list('codename', flat=True))
        perm_list += list(user.user_permissions.all().values_list('codename', flat=True))
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





        valuesObj = Value.objects.filter(Q(end_date__gt=now()) | Q(end_date__isnull=True),
                                         Q(start_date__lte=now()) | Q(start_date__isnull=True),
                                         attr__title__in=attr, item__in=items)\
            .select_related('attr__title', 'item__create_date', 'item__title')



        valuesAttribute = {}


        for key in range(0, len(items)):
            if items[key] in valuesAttribute:
                continue

            #if item[key] not int, skip
            try:
                valuesAttribute[int(items[key])] = key
            except ValueError:
                continue

        valuesAttribute = OrderedDict(sorted(((k, v) for k, v in valuesAttribute.items()), key=lambda i: i[1]))

        #TODO: Artur fix bug, when just one attribute and it's not exists, will return integer not dict
        for valuesObj in valuesObj:

            itemPk = valuesObj.item.pk

            if itemPk not in valuesAttribute:
                continue

            if not isinstance(valuesAttribute[itemPk], dict):

                valuesAttribute[itemPk] = {}

                if fullAttrVal:
                     valuesAttribute[itemPk]['CREATE_DATE'] = [{
                        'start_date': None,
                        'end_date': None,
                        'title': valuesObj.item.create_date
                    }]

                else:
                     valuesAttribute[itemPk]['CREATE_DATE'] = [valuesObj.item.create_date]

            if valuesObj.attr.title not in valuesAttribute[itemPk]:
                valuesAttribute[itemPk][valuesObj.attr.title] = []


            if fullAttrVal:
                attrValDict = {
                    'start_date': valuesObj.start_date,
                    'end_date': valuesObj.end_date,
                    'title': valuesObj.title
                }
                valuesAttribute[itemPk][valuesObj.attr.title].append(attrValDict)
            else:
                valuesAttribute[itemPk][valuesObj.attr.title].append(valuesObj.title)

        return valuesAttribute

    def getAttributeValues(self, *attr, fullAttrVal=False):
        '''
           Return values of attribute list for specific Item
                      Example item = self.getAttributeValues("NAME", "DETAIL_TEXT")
           will return :   item = {NAME:['name'] , DETAIL_TEXT:['content']}
        '''

        ctime = now()

        values = Value.objects.filter(Q(end_date__gt=ctime) | Q(end_date__isnull=True),
                                      Q(start_date__lte=ctime) | Q(start_date__isnull=True),
                                      attr__title__in=attr, item=self.id)\
            .select_related('attr__title', 'item__create_date', 'item__title')

        valuesAttribute = {}

        for valuesObj in values:
            if 'CREATE_DATE' not in valuesAttribute:
                if fullAttrVal:
                    attrValDict = {
                        'start_date': None,
                        'end_date': None,
                        'title': valuesObj.item.create_date
                    }
                    valuesAttribute['CREATE_DATE'] = [attrValDict]
                else:
                    valuesAttribute['CREATE_DATE'] = [valuesObj.item.create_date]


            if valuesObj.attr.title not in valuesAttribute:
                valuesAttribute[valuesObj.attr.title] = []

            if fullAttrVal:
                attrValDict = {
                    'start_date': valuesObj.start_date,
                    'end_date': valuesObj.end_date,
                    'title': valuesObj.title
                }
                valuesAttribute[valuesObj.attr.title].append(attrValDict)
            else:
                valuesAttribute[valuesObj.attr.title].append(valuesObj.title)

        if len(valuesAttribute) == 0:
            return []

        if(len(attr) > 1):
            return valuesAttribute
        else:
            return valuesAttribute[attr[0]]

    @staticmethod
    def createItemSlug(string, pk):
        '''
            Creating url slug from some string using unicode to acii decoder( unidecode library)

            str string - unicode string to convert to slug
            int pk - item pk to append to the slug
        '''
        #nonDig = ''.join([i for i in string if not i.isdigit()])

        #slug = slugify(nonDig)
        slug = ''
        if slug == '':
            #TODO: Artur remove that hack
            if get_language() == 'ru' or True:
                string = unidecode(string)
            else:
                string = str(pk)

        return slugify(string) + '-' + str(pk)

    def _setAttrDictValues(self, attrWithValues, existsAttributes, queries, uniqDict, user):
        '''
            set attribute values from dictionary,

            dict attrWithValues - Dictionary of dict attributes and slot ids {'SEX': 1, 'CURRENCY': [1, 2, 3]}
            QuerySet existsAttributes - QuerySet of the attributes form attrWithValues
            list queries - QuerySet filter parameters to check if attribute slots are exists
            dict uniqDict - Dictionary of dict and sub dict of slots
            User user - User object to sear as create user

            should be called only from setAttributeValue method
        '''

        bulkInsert = []

        #check if dictionary slot exists for this dictionary - using conditions
        filter_or = ' | '.join(queries)

        valueFileds = ['title']

        #get slot value for all languages
        for lang in settings.LANGUAGES:
            valueFileds.append(valueFileds[0] + '_' + lang[0])

        params = valueFileds + ['dict__pk', 'pk']

        #apply filter to get values
        attributesValue = Slot.objects.filter(eval(filter_or)).values(*params)

        if len(attributesValue) < len(queries):
            raise ValueError('Dict slot does not exists')

        for value in attributesValue:

            uniqDict[value['dict__pk']][value['pk']] = {
                'title': value['title']
            }

            for langDict in valueFileds: #set value for all languages
                uniqDict[value['dict__pk']][value['pk']].update({langDict: value[langDict]})

        #Insert dict slot
        for attribute in attrWithValues.keys():
            values = attrWithValues[attribute]
            attributeObj = existsAttributes.get(title=attribute)
            dictID = attributeObj.dict_id

            if not isinstance(values, list):
                values = [values]

            for value in values:
                if isinstance(value, dict):
                    value.update(uniqDict[dictID][int(value['title'])])

                    if 'create_user' not in value:
                        value['create_user'] = user

                    value['sha1_code'] = createHash(value['title'])



                    bulkInsert.append(Value(item=self, attr=attributeObj, **value))
                else:
                    value = uniqDict[dictID][int(value)]

                    bulkInsert.append(Value(item=self, attr=attributeObj, create_user=user,
                                                sha1_code=createHash(value), **value))

        return bulkInsert


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
        item_id = self.pk
        cache_name = "detail_%s" % item_id
        description_cache_name = "description_%s" % item_id

        cache.delete(cache_name)
        cache.delete(description_cache_name)

        #check if valid dictionary given
        if not isinstance(attrWithValues, dict) or not attrWithValues:
            raise ValueError

        #generate slug
        if 'NAME' in attrWithValues:

            if isinstance(attrWithValues['NAME'], dict) and len(attrWithValues['NAME']) > 0:
                attrWithValues['SLUG'] = {}

                for attrTitle, attrValue in attrWithValues['NAME'].items():

                    if attrTitle[:5] == 'title':
                        attrWithValues['SLUG'][attrTitle] = Item.createItemSlug(attrValue, self.pk)

            elif isinstance(attrWithValues['NAME'], str):
                attrWithValues['SLUG'] = Item.createItemSlug(attrWithValues['NAME'], self.pk)


        queries = []
        bulkInsert = []
        notBulk = []
        attributes = copy(attrWithValues).keys()
        uniqDict = {}

        #get all passed attributes
        existsAttributes = Attribute.objects.filter(title__in=attributes)

        if len(existsAttributes) != len(attrWithValues):
            raise ValueError("Attribute does not exists")

        for attr in attributes:
            attributeObj = existsAttributes.get(title=attr)
            dictID = attributeObj.dict_id
            values = attrWithValues[attr]

            #value should be a list of values
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

                        if attributeObj.type == 'Str':
                            notBulk.append(Value(item=self, attr=attributeObj, **value))
                        else:
                            bulkInsert.append(Value(item=self, attr=attributeObj, **value))
                    else:
                        if attributeObj.type == 'Str':
                            notBulk.append(Value(title=value, item=self, attr=attributeObj,
                                                create_user=user, sha1_code=createHash(value)))
                        else:
                            bulkInsert.append(Value(title=value, item=self, attr=attributeObj,
                                                create_user=user, sha1_code=createHash(value)))
                #Dictionary value
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
            bulkInsert += self._setAttrDictValues(attrWithValues, existsAttributes, queries, uniqDict, user)

        try:
            with transaction.atomic():
                Value.objects.filter(attr__title__in=attributes, item=self.id).delete()
                Value.objects.bulk_create(bulkInsert)

                #TODO: Artur fix it
                #workaround of some bug with oracle + bulk_insert
                # django ticket #22144
                for instanceToSave in notBulk:
                    instanceToSave.save()

        except IntegrityError as e:
            raise e


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
        ('relation', 'Relation'),
        ('hierarchy', 'Hierarchy'),
        ('dependence', 'Depended relation'),
        ('friend', 'Friend relation'),
    )

    type = models.CharField(max_length=10, choices=TYPE_OF_RELATIONSHIP, null=False, blank=False)

    is_admin = models.BooleanField(default=False)
    qty = models.FloatField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("parent", "child")

    def __str__(self):
        return self.title

    @staticmethod
    def setRelRelationship(parent, child, user, type="relation", **additionParams):
        '''
            Setting relationship and setting end_date and start_date to the relation depended on parent

            Item parent - Item instance to set as a parent
            Item child - Item instance to set as a child
            Str type - Relationship type

            kwargs additionParams - addition pareters ( end_date , start_date etc..)
        '''

        if not isinstance(parent, Item):
            raise ValueError('Parent should be an Item instance')

        if not isinstance(child, Item):
            raise ValueError('Child should be an Item instance')

        #if parent.__class__.__name__ == 'Item' or child.__class__.__name__ == 'Item':
        #    raise ValueError('Child and Parent should be subclass of Item')

        params = {
            'parent': parent,
            'child': child,
            'create_user': user,
            'type': type
        }

        params.update(additionParams)

        if type == 'dependence' and ('end_date' not in params or 'start_date' not in params):
            #set activation date for dependence relation

            try:#Getting parent start date and end date
                parentRel = Relationship.objects.get(child=parent.pk, type='dependence')
                parentRelEnd = parentRel.end_date
                parendStart = parentRel.start_date
            except ObjectDoesNotExist:
                parentRelEnd = None
                parendStart = None

            if 'end_date' not in params: #Getting proper end date
                if not parent.end_date and parentRelEnd:
                    params['end_date'] = parentRelEnd
                elif not parentRelEnd and parent.end_date:
                    params['end_date'] = parent.end_date
                elif parentRelEnd and parent.end_date:

                    if parentRelEnd > parent.end_date:
                        params['end_date'] = parent.end_date
                    else:
                        params['end_date'] = parentRelEnd

            if 'start_date' not in params: #Getting proper start date

                if not parendStart and parent.start_date:
                    params['start_date'] = parent.start_date

                elif parendStart and parent.start_date:

                    if parendStart > parent.start_date:
                        params['start_date'] = parendStart
                    else:
                        params['start_date'] = parent.start_date

        Relationship.objects.create(**params)

#----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
#----------------------------------------------------------------------------------------------------------
class Value(models.Model):
    title = models.TextField()
    attr = models.ForeignKey(Attribute, related_name='attr2value')
    item = models.ForeignKey(Item, related_name='item2value')
    #The length of SHA-1 code is always 20x2 (2 bytes for symbol in Unicode)
    sha1_code = models.CharField(max_length=40, blank=True)

    start_date = models.DateTimeField(default=timezone.now)
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

    Item.objects.filter(c2p__parent_id=instance.pk, c2p__type="dependence").delete()
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

@receiver(pre_save, sender=Slot)
def slotUpdateAttr(instance, **kwargs):
    attrID = Attribute.objects.filter(dict=instance.dict).values_list('pk')
    attrID = [id[0] for id in attrID]

    try:
        if getattr(instance, 'pk', None):

            old = Slot.objects.get(pk=instance.pk)

            if old.title:
                key = 'title'

                valueFileds = {}

                #get value for all languages
                for lang in settings.LANGUAGES:
                    valueFileds.update({key + '_' + lang[0]: getattr(instance, key + '_' + lang[0], '')})

                Value.objects.filter(attr__in=attrID, title=old.title).update(**valueFileds)
    except Exception:
        return False

