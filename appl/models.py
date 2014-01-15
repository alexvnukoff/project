from django.db import models
from core.models import Item, State
from django.contrib.auth.models import Group, Permission
from random import randint
from core.hierarchy import hierarchyManager
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent_id=parent, c2p__type="rel")


def getSpecificParent(cls, child):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(p2c__child_id=child, c2p__type="rel")

def createItemSlug(string):
    nonDig = ''.join([i for i in string if not i.isdigit()])

    if not nonDig:
        return False

    slug = slugify(nonDig)

    if not slug:
        return False

    return slugify(string)

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
        return ''

class Company(Organization):
    name = models.CharField(max_length=128, null=True, blank=True)


class Company(Item):

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
        return self.getName()
    #TODO: Jenya change attr titles to NAME and DETAIL_TEXT
    def getName(self):
        name = self.getAttributeValues('NAME')
        return name[0] if name else '{EMPTY}'

    def getDescription(self):
        desc = self.getAttributeValues('DETAIL_TEXT')
        return desc[0] if desc else ''

    def getCountry(self):
        return 100

    def getBranches(self):
        return getSpecificChildren("Branch", self.pk)

    def getCountry(self):
        return 1

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
        return ''


class Branch(Item):

    def __str__(self):
        return ''


class Category(Item):

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Department State')

    def __str__(self):
        return self.title

class Product(Item):

    def __str__(self):
        return ''

class License(Item):

    def __str__(self):
        return ''

class Service(Item):

    def __str__(self):
        return ''


class Invoice(Item):

    def __str__(self):
        return ''


class News(Item):

    def __str__(self):
        return ''


class Article(Item):

    def __str__(self):
        return ''


class Announce(Item):

    def __str__(self):
        return ''


class Review(Item):

    def __str__(self):
        return ''


class Rating(Item):

    def __str__(self):
        return ''


class Payment(Item):

    def __str__(self):
        return ''


class Shipment(Item):

    def __str__(self):
        return ''


class Tender(Item):

    def __str__(self):
        return ''


class Advertising(Item):

    def __str__(self):
        return ''


class Rate(Item):

    def __str__(self):
        return ''

class Order(Item):

    def __str__(self):
        return ''


class Basket(Item):

    def __str__(self):
        return ''


class Cabinet(Item):

    def __str__(self):
        return ''


class Document(Item):

    def __str__(self):
        return ''


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
