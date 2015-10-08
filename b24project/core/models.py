from collections import OrderedDict
from random import randint
import warnings
import datetime
import hashlib

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
from guardian.shortcuts import get_objects_for_user
from unidecode import unidecode

from django.core.cache import cache

from core.hierarchy import hierarchyManager
from tpp.SiteUrlMiddleWare import get_request


def createHash(string):
    return hashlib.sha1(str(string).encode()).hexdigest()


# ----------------------------------------------------------------------------------------------------------
#             Class UserManager defines manager for user
# ----------------------------------------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        request = get_request()

        if request:
            try:
                real_ip = request.META['HTTP_X_FORWARDED_FOR']
                real_ip = real_ip.split(",")[0]
                request.META['REMOTE_ADDR'] = real_ip
            except:
                pass

            ip = request.META['REMOTE_ADDR']
        else:  # for data migration as batch process generate random IP address 0.rand().rand().rand() for avoiding bot checking
            ip = '0.' + str(randint(0, 255)) + '.' + str(randint(0, 255)) + '.' + str(randint(0, 255))

        time = now() - datetime.timedelta(minutes=1)
        users = User.objects.filter(ip=ip, date_joined__gt=time)

        if users:
            raise ValueError("Bot")
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email).lower()
        user = self.model(email=email, ip=ip)

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


# ----------------------------------------------------------------------------------------------------------
#             Class User define a new user for Django system
# ----------------------------------------------------------------------------------------------------------
class SiteProfileNotAvailable(Exception):
    pass


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)  # for enterprise content management
    is_commando = models.BooleanField(default=False)  # for special purposes
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    ip = models.GenericIPAddressField(null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     return True

    # def has_perm(self, perm, obj=None):
    #     return True
    #
    # def has_perms(self, perm_list, obj):
    #     """
    #     Returns True if the User has all specified permissions perm_list for this object obj.
    #     """
    #
    #     if self.is_superuser or self.is_commando:
    #         return True
    #     else:
    #         if obj:
    #             p_list = obj.getItemInstPermList(self)
    #             for i in perm_list:
    #                 if i not in p_list:
    #                     return False
    #
    #             return True
    #
    #         else:
    #             return False

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

    def manageable_organizations(self):
        from b24online.models import Organization
        key = "user:%s:manageable_organizations" % self.pk
        organization_ids = cache.get(key)

        if organization_ids is None:
            organization_ids = [org.pk for org in
                                get_objects_for_user(self, 'b24online.manage_organization', Organization)]
            cache.set(key, organization_ids,  60 * 10)

        return organization_ids or []

# ----------------------------------------------------------------------------------------------------------
#             Class Dictionary defines dictionary for attributes in application
# ----------------------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------------
#             Class Slot defines row in dictionary for attributes in application
# ----------------------------------------------------------------------------------------------------------
class Slot(models.Model):
    title = models.CharField(max_length=128)
    dict = models.ForeignKey(Dictionary, related_name='slot')

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("title", "dict")


# ----------------------------------------------------------------------------------------------------------
#             Class Attribute defines attributes for Item in application
# ----------------------------------------------------------------------------------------------------------
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
    # f_order = models.BooleanField(default=False)# set in True if attribute participate in sort list of the fields in
    # setup view form in User's Cabinet
    # f_cache = models.BooleanField(default=False)# reserved field for fast access to item's main attributes
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    multilingual = models.BooleanField(default=True)

    class Meta:
        unique_together = ("title", "type")

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------------
#             Class AttrTemplate defines default attributes for specific Item class
# ----------------------------------------------------------------------------------------------------------
class AttrTemplate(models.Model):
    required = models.BooleanField(default=False)
    classId = models.ForeignKey(ContentType)
    attrId = models.ForeignKey(Attribute, related_name='attrTemplate')

    def __str__(self):
        return "Class Name:   " + self.classId.name + "    attribute: " + self.attrId.title

    class Meta:
        unique_together = ("classId", "attrId")


# ----------------------------------------------------------------------------------------------------------
#             Class State defines current state for particular item instance
# ----------------------------------------------------------------------------------------------------------
class State(models.Model):
    title = models.CharField(max_length=128, unique=True)
    perm = models.ForeignKey(Group, related_name='state', null=True)

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------------
#             Class Process defines process which is attached to particular Item
# ----------------------------------------------------------------------------------------------------------
class Process(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------------
#             Class Action defines member of the process, which is attached to particular Item
# ----------------------------------------------------------------------------------------------------------
class Action(models.Model):
    title = models.CharField(max_length=128, unique=True)
    papa = models.ForeignKey(Process, related_name='action')
    child_proc = models.ForeignKey(Process, related_name='start_node', default=0)  # handle to child process

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------------
#             Class ActionPath defines connection between two Actions in Process
# ----------------------------------------------------------------------------------------------------------
class ActionPath(models.Model):
    title = models.CharField(max_length=128, unique=True)
    source = models.ForeignKey(Action, related_name='act2path')
    target = models.ForeignKey(Action, related_name='path2act')

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------------
#             Class Item defines basic primitive for application objects
# ----------------------------------------------------------------------------------------------------------
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
        return self.filter(Q(Q(end_date__gt=timezone.now()) | Q(end_date__isnull=True)), start_date__lte=timezone.now()) \
            .exclude(Q(c2p__end_date__lte=timezone.now(), c2p__end_date__isnull=False) | Q(c2p__start_date__gt=now()),
                     c2p__type='dependence')


class Item(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    member = models.ManyToManyField('self', through='Relationship', symmetrical=False, null=True, blank=True)
    status = models.ForeignKey(State, null=True, blank=True)
    proc = models.ForeignKey(Process, null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name='item')
    community = models.ForeignKey(Group, null=True, blank=True)
    contentType = models.ForeignKey(ContentType, null=True, blank=True)

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

    # def __init__(self, name):
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

        # send signal to search frontend
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

        num = Item.objects.filter(~Q(c2p__parent_id=parent, c2p__type="hierarchy", p2c__child_id=parent),
                                  pk__in=child).count()

        if num != len(child):
            raise ValueError('Wrong child count')

        bulkInsert = []

        for item in child:
            title = [str(parent.pk), 'hierarchy', str(item)]
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
        is_commando = getattr(user, 'is_commando', False)  # Anonymous User has not attribute 'is_commando'

        if user.is_superuser or is_commando or self.create_user == user:
            group_list.append('Owner')
            group_list.append('Admin')
            group_list.append('Staff')
        else:
            # whether there is a User Cabinet
            cabinet = getattr(user, 'cabinet', False)  # Anonymous User has not attribute 'cabinet'
            if cabinet:
                # get Cabinet ID
                cab_pk = user.cabinet.filter(user=user).values('pk')
                # check is Cabinet belongs to any Organization
                if Item.objects.filter(c2p__parent__c2p__parent__organization__isnull=False, pk=cab_pk).exists():
                    # get Organization ID
                    org_lst = Item.objects.filter(p2c__child__p2c__child__p2c__child=cab_pk).values('pk')

                    for org_pk in org_lst:
                        # if object SELF belongs to the same Company or it is Company itself or belongs to User's TPP or to TPP's parent TPP...
                        if org_pk['pk'] == self.pk or \
                                Item.objects.filter(c2p__parent=org_pk['pk'], pk=self.pk).exists() or \
                                Item.objects.filter(c2p__parent__c2p__parent=org_pk['pk'], pk=self.pk).exists() or \
                                Item.objects.filter(c2p__parent__c2p__parent__c2p__parent=org_pk['pk'],
                                                    pk=self.pk).exists():

                            rs = Relationship.objects.filter(parent__c2p__parent__c2p__parent=org_pk['pk'], \
                                                             child=cab_pk, type='relation')
                            for r in rs:
                                if r.is_admin:
                                    group_list.append('Admin')
                                    group_list.append('Staff')
                                else:
                                    if self.status:
                                        if self.status.perm:  # is there permissions group for current object's state?
                                            group_list.append(self.status.perm.name)
                                        else:  # no permissions group for current state, attach Staff group
                                            group_list.append('Staff')

                        else:  # User and SELF belongs to different Organization without any correlation
                            pass

                else:  # Cabinet still do not attach to any Organization
                    pass
            else:  # if User without Cabinet (before first login or unregistered)
                pass

        # get all permissions from all related groups for current type of item
        group_list = list(set(group_list))  # remove duplicated keys in groups list
        perm_list = Group.objects.filter(name__in=group_list).values_list('permissions__codename', flat=True)

        perm_list = list(perm_list)

        # attach user's private permissions
        # perm_list += list(user.user_permissions.filter(codename__contains=obj_type).values_list('codename', flat=True))
        perm_list += list(user.user_permissions.all().values_list('codename', flat=True))
        perm_list = list(set(perm_list))  # remove duplicated keys in permissions list

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
                                         attr__title__in=attr, item__in=items) \
            .select_related('attr__title', 'item__create_date', 'item__title')

        valuesAttribute = {}

        for key in range(0, len(items)):
            if items[key] in valuesAttribute:
                continue

            # if item[key] not int, skip
            try:
                valuesAttribute[int(items[key])] = key
            except ValueError:
                continue

        if len(valuesObj) > 0:
            valuesAttribute = OrderedDict(sorted(((k, v) for k, v in valuesAttribute.items()), key=lambda i: i[1]))

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

        for id, item in valuesAttribute.items():
            if isinstance(item, int):
                valuesAttribute[id] = {}

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
                                      attr__title__in=attr, item=self.id) \
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

        if (len(attr) > 1):
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
        # nonDig = ''.join([i for i in string if not i.isdigit()])

        # slug = slugify(nonDig)
        slug = ''
        if slug == '':
            # TODO: Artur remove that hack
            if get_language() == 'ru' or True:
                string = unidecode(string)
            else:
                string = str(pk)

        return slugify(string) + '-' + str(pk)

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
                                'TELEPHONE': ['123456', '321456'],
                                'DISCOUNT': {'title': '50', end_date: '1/1/15'}
                                'DISCOUNT': [{'title': '50', end_date: '1/1/15'}, {'title': '30', end_date: '2/1/15'}]
                                'POSSIBLE_CURRENCY': {'title': 'RUB', 'UPDATE': 30}     # example for udpate
                                # attribute name     value_id:value1 value_id:value2
                            }
        '''

        # Check if valid dictionary given
        if not isinstance(attrWithValues, dict) or not attrWithValues:
            raise ValueError

        # Generate slug from NAME attribute
        if 'NAME' in attrWithValues:

            slugName = ''

            if isinstance(attrWithValues['NAME'], dict):
                slugName = attrWithValues['NAME'].get('title')

            elif isinstance(attrWithValues['NAME'], str):
                slugName = attrWithValues['NAME']

            attrWithValues['SLUG'] = Item.createItemSlug(slugName, self.pk)

        # Get all passed attributes
        existsAttributes = Attribute.objects.filter(title__in=attrWithValues.keys())

        if len(existsAttributes) != len(attrWithValues):
            raise ValueError("Attribute does not exists")

        itemExistsAttribute = {}

        # Select existing values for given attributes
        for value in Value.objects.filter(item=self, attr__in=existsAttributes).select_related('attr'):
            itemExistsAttribute[value.attr.title] = {
                value.pk: value
            }

        for attr in existsAttributes:  # keys from passed attribute dictionary {dict_keys} ['KEY1', 'KEY2',...]
            values = attrWithValues[attr.title]  # get value for attr key
            attribute = attr.title

            # Value should be a list of values
            if not isinstance(values, list):
                values = [values]

            for value in values:

                pk = False

                if isinstance(value, dict):

                    if value.get('title', False) is False:
                        continue

                    if attribute in itemExistsAttribute:
                        try:
                            pk = int(value['UPDATE'])
                            del value['UPDATE']
                        except (ValueError, KeyError):
                            pk = list(itemExistsAttribute[attribute])[0]

                elif attribute in itemExistsAttribute:
                    pk = list(itemExistsAttribute[attribute].keys())[0]

                Value.setValue(attr, self, user, value, pk)

        # For compatibility do not use it, should be surrounded with try-except
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


# ----------------------------------------------------------------------------------------------------------
#             Class Relationship defines relationships between two Items
# ----------------------------------------------------------------------------------------------------------
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

        # if parent.__class__.__name__ == 'Item' or child.__class__.__name__ == 'Item':
        #    raise ValueError('Child and Parent should be subclass of Item')

        params = {
            'parent': parent,
            'child': child,
            'create_user': user,
            'type': type
        }

        params.update(additionParams)

        if type == 'dependence' and ('end_date' not in params or 'start_date' not in params):
            # set activation date for dependence relation

            try:  # Getting parent start date and end date
                parentRel = Relationship.objects.get(child=parent.pk, type='dependence')
                parentRelEnd = parentRel.end_date
                parendStart = parentRel.start_date
            except ObjectDoesNotExist:
                parentRelEnd = None
                parendStart = None

            if 'end_date' not in params:  # Getting proper end date
                if not parent.end_date and parentRelEnd:
                    params['end_date'] = parentRelEnd
                elif not parentRelEnd and parent.end_date:
                    params['end_date'] = parent.end_date
                elif parentRelEnd and parent.end_date:

                    if parentRelEnd > parent.end_date:
                        params['end_date'] = parent.end_date
                    else:
                        params['end_date'] = parentRelEnd

            if 'start_date' not in params:  # Getting proper start date

                if not parendStart and parent.start_date:
                    params['start_date'] = parent.start_date

                elif parendStart and parent.start_date:

                    if parendStart > parent.start_date:
                        params['start_date'] = parendStart
                    else:
                        params['start_date'] = parent.start_date

        Relationship.objects.create(**params)


# ----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
# ----------------------------------------------------------------------------------------------------------
class Value(models.Model):
    title = models.TextField()
    attr = models.ForeignKey(Attribute, related_name='attr2value')
    item = models.ForeignKey(Item, related_name='item2value')
    # The length of SHA-1 code is always 20x2 (2 bytes for symbol in Unicode)
    # sha1_code = models.CharField(max_length=40, blank=True)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User, related_name='creator')

    # class Meta:
    # unique_together = ("sha1_code", "attr", "item")
    # db_tablespace = 'TPP_CORE_VALUES'

    def __str__(self):
        return self.title

    def get(self):
        return self.title

    @staticmethod
    def getDictVal(attributeObj, slot):

        slotValues = Slot.objects.get(dict=attributeObj.dict, pk=slot)

        newVals = {
            'title': slotValues.title
        }

        # Prepare fields for slot query to get all lang values
        for lang in settings.LANGUAGES:
            field = 'title_' + lang[0]
            newVals[field] = slotValues.__dict__[field]

        return newVals

    @staticmethod
    def setValue(attributeObj, itemObj, user, value, to_update=False):

        if not isinstance(value, dict):
            value = {'title': value}

        if attributeObj.dict:
            value = Value.getDictVal(attributeObj, value['title'])

        if to_update:
            if not attributeObj.multilingual:
                for lang in settings.LANGUAGES:
                    value['title_' + lang[0]] = value['title']

            Value.objects.filter(pk=to_update).update(**value)

        else:
            if attributeObj.multilingual:
                Value.objects.create(item=itemObj, attr=attributeObj, create_user=user, **value)
            else:
                Value.objects.populate(True).create(item=itemObj, attr=attributeObj, create_user=user, **value)

        return True


# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
#             Signal receivers
# ----------------------------------------------------------------------------------------------------------
@receiver(pre_delete, sender=Item)
def itemPreDelete(instance, **kwargs):
    Item.hierarchy.deleteTree(instance.pk)

    dependedChilds = Item.objects.filter(c2p__parent_id=instance.pk, c2p__type="dependence")

    for inst in dependedChilds:
        inst.delete()

    Relationship.objects.filter(Q(child=instance.pk) | Q(parent=instance.pk)).delete()
    Value.objects.filter(item=instance.pk).delete()


@receiver(post_delete, sender=Item)
def itemPostDelete(instance, **kwargs):
    if instance.community:
        Group.objects.get(pk=instance.community.pk).delete()


'''
@receiver(pre_save, sender=Value)
def valueSaveHashCode(instance, **kwargs):
    instance.sha1_code = createHash(instance.title)
'''


@receiver(pre_save, sender=Relationship)
def generateTitleField(instance, **kwargs):
    assert instance.parent.pk != instance.child.pk, 'You cannot create an relationship for class instance with itself!'
    instance.title = 'RS_' + str(instance.type).upper() + '_PARENT:' + str(instance.parent.pk) + '_CHILD:' + str(
        instance.child.pk)


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

                # get value for all languages
                for lang in settings.LANGUAGES:
                    valueFileds.update({key + '_' + lang[0]: getattr(instance, key + '_' + lang[0], '')})

                Value.objects.filter(attr__in=attrID, title=old.title).update(**valueFileds)
    except Exception:
        return False


@receiver(pre_save, sender=Site)
def removeSiteCacheOnUpdate(instance, **kwargs):
    cache_name_pk = 'site_pk_%s' % instance.pk
    cache_name_domain = 'site_domain_%s' % instance.domain

    cache.delete(cache_name_pk)
    cache.delete(cache_name_domain)


@receiver(pre_delete, sender=Site)
def removeSiteCacheOnRemove(instance, **kwargs):
    cache_name_pk = 'site_pk_%s' % instance.pk
    cache_name_domain = 'site_domain_%s' % instance.domain

    cache.delete(cache_name_pk)
    cache.delete(cache_name_domain)