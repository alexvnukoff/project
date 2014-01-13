from django.db import models, transaction
from django.db.models.signals import pre_init
from django.dispatch import receiver
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.contrib.auth.models import Group, PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
import hashlib
from core.hierarchy import hierarchyManager
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
    perm = models.ForeignKey(Group, related_name='state')

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
    create_date = models.DateField(auto_now_add=True)
    update_user = models.ForeignKey(User, null=True, blank=True, related_name='user2item')
    update_date = models.DateField(null=True, blank=True)

    class Meta:
        permissions = (
            ("read_item", "Can read item"),
        )

    #def __init__(self, name):
    #   title = name

    def __str__(self):
        return self.title

    def getItemPermissionsList(self, user):
        '''
        Returns List of Permissions which define set of operations for given User under given Item's instance
        '''
        perm_list=[]
        if user == self.create_user or user == self.update_user:
            perm_list = user.get_group_permissions(self.status__perm)
        else:
            if user.group.get(name=self.community__name):
                perm_list = user.get_group_permissions(self.status__perm)
            else:
                perm_list = 0

        return perm_list

    @staticmethod
    def getItemsAttributesValues(attr, items):
        '''
           Return values of attribute list in items list
        '''
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

    def getAttributeValues(self, *attr):
        '''
           Return values of attribute list in specific Item
        '''

        values = Value.objects.filter(attr__title__in=attr, item=self.id)
        values = list(values.values("title", "attr__title", "item__title", "item"))


        valuesAttribute = {}

        for valuesDict in values:
            if valuesDict['item'] not in valuesAttribute:
                valuesAttribute[valuesDict['item']] = {'title': [valuesDict['item__title']]}

            if valuesDict['attr__title'] not in valuesAttribute[valuesDict['item']]:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']] = []

            valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(valuesDict['title'])

        return valuesAttribute

    @transaction.atomic
    def setAttributeValue(self, attrWithValues):
        '''
            Set values for attributes (mass)
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

        sid = transaction.savepoint()

        try:
            Value.objects.filter(attr__title__in=attributes, item=self.id).delete()
            Value.objects.bulk_create(bulkInsert)
        except Exception:
            transaction.savepoint_rollback(sid)

            raise Exception
        else:
            transaction.savepoint_commit(sid)

        return True

    def getSiblings(self):
        '''
            Get siblings in hierarchy
        '''
        parent = self.c2p.get(p2c__type="hier")

        return parent.getChildren()

    def getAncestors(self, includeSelf = False):
        '''
            Get list of ancestors in hierarchy
            List contains item objects
        '''
        translation = {'rev_level': 'level'}

        ancestors = Item.objects.raw('''SELECT PARENT_ID, MAX(LEVEL) OVER () + 1 - LEVEL AS rev_level , item.id as id
                                FROM
                              (
                                SELECT parent_id, child_id, type
                                  FROM core_relationship
                                UNION
                                SELECT NULL, id, null
                                  FROM core_item i
                                 WHERE NOT EXISTS
                                (
                                  SELECT *
                                    FROM core_relationship
                                   WHERE child_id = i.id AND type='hier'
                                )
                              ) rel
                            INNER JOIN core_item item ON (rel.CHILD_ID = item.ID)
                            WHERE rel.type='hier' OR PARENT_ID is null
                            CONNECT BY PRIOR  rel.PARENT_ID = rel.CHILD_ID
                            START WITH rel.CHILD_ID = %s
                            ORDER BY rev_level''', [self.id], translations=translation)

        ancestors = list(ancestors)

        if includeSelf is False:
            del ancestors[len(ancestors) - 1]

        return ancestors

    def getDescendants(self, includeSelf = False):
        '''
            Get descendants in hierarchy
        '''
        translation = {'LEVEL': 'level'}

        descendants = Item.objects.raw('''SELECT PARENT_ID, CHILD_ID, LEVEL, CONNECT_BY_ISLEAF as isLeaf, item.id as id
                                            FROM
                                          (
                                            SELECT parent_id, child_id, type
                                              FROM core_relationship
                                            UNION
                                            SELECT NULL, id, null
                                              FROM core_item i
                                             WHERE NOT EXISTS
                                            (
                                              SELECT *
                                                FROM core_relationship
                                               WHERE child_id = i.id AND type='hier'
                                            )
                                          ) rel
                                        INNER JOIN core_item item ON (rel.CHILD_ID = item.ID)
                                        WHERE rel.type='hier' OR PARENT_ID is null
                                        CONNECT BY PRIOR  rel.CHILD_ID = rel.PARENT_ID
                                        START WITH rel.CHILD_ID = %s
                                        ORDER BY LEVEL;''', [self.id], translations=translation)

        descendants = list(descendants)

        if includeSelf is False:
            del descendants[0]

        return descendants

    def getDescendantCount(self):
        '''
            Get count of descendants in hierarchy
        '''
        from django.db import connection

        cursor = connection.cursor()

        cursor.execute('''SELECT count(*) - 1
                            FROM
                            (
                                SELECT parent_id, child_id, type
                                    FROM core_relationship
                                UNION SELECT NULL, id, null
                                    FROM core_item i
                                    WHERE NOT EXISTS
                                    (
                                        SELECT *
                                            FROM core_relationship
                                            WHERE child_id = i.id AND type='hier'
                                    )
                            ) rel
                            INNER JOIN core_item item ON (rel.CHILD_ID = item.ID)
                            WHERE rel.type='hier' OR PARENT_ID is null
                            CONNECT BY PRIOR  rel.CHILD_ID = rel.PARENT_ID
                            START WITH rel.CHILD_ID = %s''', [self.pk])

        return cursor.fetchone()[0]

    def getChildren(self):
        '''
            Get children in hierarchy
        '''
        return Item.objects.filter(c2p__parent_id=self.pk, c2p__type="hier")

    @transaction.atomic
    def delete(self, using=None, **kwarg):
        '''
            Overwrite the delete method for trees structures

            if you are passing a parameter "cut" to the method
            it will delete object's descendants
                Example: Item(pk=1).delete(cut=True)
            otherwise it will squeeze the descendants of the object
            or will create new root parent/s
                Example: Item(pk=1).delete()
                if Item = 1 is root parent all his children will become root parents
                if Item = 1 is child of Item = 2 all his children will become a children of Item =2

            This method will delete all relations with this object
            from the relationship model
        '''
        descedantsIDs = []

        sid = transaction.savepoint()

        try:
            for child in self.getDescendants():
                descedantsIDs.append(child.pk)

            if len(descedantsIDs):
                if "cut" in kwarg and kwarg['cut'] is True:
                    Item.objects.filter(pk__in=descedantsIDs).delete()
                    descedantsIDs.append(self.pk)
                    Relationship.objects.filter(Q(child__in=descedantsIDs) | Q(parent__in=descedantsIDs)).delete()
                else:
                    try:
                        parentID = Item.objects.get(p2c__child_id=self.pk, p2c__type="hier")
                    except ObjectDoesNotExist:
                        Relationship.objects.filter(parent=self.pk).delete()
                    else:
                        Relationship.objects.filter(parent=self.pk).update(parent=parentID)
            else:
                Relationship.objects.filter(Q(child__in=descedantsIDs) | Q(parent__in=descedantsIDs)).delete()

            super(Item, self).delete(using)
        except Exception as e:
            transaction.savepoint_rollback(sid)

            raise e
        else:
            transaction.savepoint_commit(sid)


#----------------------------------------------------------------------------------------------------------
#             Class Relationship defines relationships between two Items
#----------------------------------------------------------------------------------------------------------
class Relationship(models.Model):
    title = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey(Item, related_name='p2c')
    child = models.ForeignKey(Item, related_name='c2p')
    TYPE_OF_RELATIONSHIP = (
        ('rel', 'String'),
        ('hier', 'Hierarchy'),)
    type = models.CharField(max_length=10, choices=TYPE_OF_RELATIONSHIP)

    qty = models.FloatField(null=True, blank=True)
    create_date = models.DateField(auto_now_add=True)
    create_user = models.ForeignKey(User)

    class Meta:
        unique_together = ("parent", "child")

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
#----------------------------------------------------------------------------------------------------------
class Value(models.Model):
    title = models.TextField()
    attr = models.ForeignKey(Attribute, related_name='attr2value')
    item = models.ForeignKey(Item, related_name='item2value')
    sha1_code = models.CharField(max_length=40) #The length of SHA-1 code is always 20x2 (2 bytes for symbol in Unicode)

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
