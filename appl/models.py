from django.db import models
from core.models import Item, State
from django.contrib.auth.models import Group, Permission
from random import randint
from core.hierarchy import hierarchyManager
from django.db.models.signals import pre_save
from django.dispatch import receiver


def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent_id=parent, c2p__type="rel")

class Organization (Item):

    def addWorker(self, user):
        '''
            Adds User into organization's community Group
        '''
        pass

    class Meta:
        permissions = (
            ("read_organization", "Can read organization"),
        )

class Tpp(Organization):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        permissions = (
            ("read_tpp", "Can read tpp"),
        )

    def __init__(self, *args, **kwargs):
        super(Tpp, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default TPP State')


    def __str__(self):
        return self.name

class Company(Organization):
    name = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        permissions = (
            ("read_company", "Can read company"),
        )

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Company State')

    def __str__(self):
        return self.name

    def getName(self):
        return 'test1'

    def getDescription(self):
        return 'test2'

    def getCountry(self):
        return 100

    def getBranches(self):
        return getSpecificChildren("Branch", self.pk)

    def getDepartments(self):
        '''
            Get dict of departments only for this company
            this method returns a dictionary that contains a level , id and parent of each member
             as well as the result dictionary stores the tree structure

             Example: Company(pk=1).getDepartments()
        '''
        childs = Department.hierarchy.getChild(self.pk).values('pk')
        childs = [x['pk'] for x in childs]
        return Department.hierarchy.getDescedantsForList(childs)

class Department(Organization):
    name = models.CharField(max_length=128)

    objects = models.Manager()
    hierarchy = hierarchyManager()

    class Meta:
        permissions = (
            ("read_department", "Can read department"),
        )

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Department State')

    def __str__(self):
        return self.name

class Branch(Item):
    name = models.CharField(max_length=128, unique=True)

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.name

class Category(Item):
    name = models.CharField(max_length=128, unique=True)

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Department State')

    def __str__(self):
        return self.name

class Site(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Product(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class License(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Service(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Invoice(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class News(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Article(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Announce(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Review(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Rating(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Payment(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Shipment(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Tender(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Advertising(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Rate(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Forum(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class ForumThread(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class ForumPost(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Order(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Basket(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Cabinet(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Document(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Gallery(Item):
      photo = models.ImageField(verbose_name='Avatar',  upload_to='gallery/', blank=True, null=True)

      def __str__(self):
          return str(self.photo)

#----------------------------------------------------------------------------------------------------------
#             Signal receivers
#----------------------------------------------------------------------------------------------------------
@receiver(pre_save, sender=Company)
def companyCommunity(instance, **kwargs):
    '''
       Create community Group for given Company instance
    '''
    if not instance.community:
        instance.community = Group.objects.create(name='ORG-' + str(randint(1000000, 9999999)))

@receiver(pre_save, sender=Tpp)
def tppCommunity(instance, **kwargs):
    '''
       Create community Group for given TPP instance
    '''
    if not instance.community:
        instance.community = Group.objects.create(name='ORG-' + str(randint(1000000, 9999999)))

@receiver(pre_save, sender=Department)
def departmentCommunity(instance, **kwargs):
    '''
       Create community Group for given Department instance
    '''
    if not instance.community:
        instance.community = Group.objects.create(name='ORG-' + str(randint(1000000, 9999999)))

#----------------------------------------------------------------------------------------------------------
#             Database default objects generation
#----------------------------------------------------------------------------------------------------------
#Default Groups with Permissions
read_item = Permission.objects.get(codename='read_item')

read_tpp = Permission.objects.get(codename='read_tpp')
add_tpp = Permission.objects.get(codename='add_tpp')
change_tpp = Permission.objects.get(codename='change_tpp')
delete_tpp = Permission.objects.get(codename='delete_tpp')

read_company = Permission.objects.get(codename='read_company')
add_company = Permission.objects.get(codename='add_company')
change_company = Permission.objects.get(codename='change_company')
delete_company = Permission.objects.get(codename='delete_company')

read_department = Permission.objects.get(codename='read_department')
add_department = Permission.objects.get(codename='add_department')
change_department = Permission.objects.get(codename='change_department')
delete_department = Permission.objects.get(codename='delete_department')

gr1, created = Group.objects.get_or_create(name='Default TPP Permissions')
if created:
    gr1.permissions.add(read_tpp)

gr2, created = Group.objects.get_or_create(name='Default Company Permissions')
if created:
    gr2.permissions.add(read_company)

gr3, created = Group.objects.get_or_create(name='Default Department Permissions')
if created:
    gr3.permissions.add(read_department)

gr4, created = Group.objects.get_or_create(name='Company Creator')
if created:
    gr4.permissions.add(add_company, read_company)

gr5, created = Group.objects.get_or_create(name='Owner')
if created:
    gr5.permissions.add(read_company, change_company, delete_company,
                        read_department, change_department, delete_department)

gr6, created = Group.objects.get_or_create(name='Admin')
if created:
    gr6.permissions.add(read_company, change_company,
                        read_department, change_department)

gr7, created = Group.objects.get_or_create(name='Staff')
if created:
    gr7.permissions.add(read_company, read_department)

#Default States
st1, created=State.objects.get_or_create(title='Default TPP State', perm=gr1)
st2, created=State.objects.get_or_create(title='Default Company State', perm=gr2)
st3, created=State.objects.get_or_create(title='Default Department State')
