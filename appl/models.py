from django.db import models
from core.models import Item
from core.hierarchy import hierarchyManager
from django.template.defaultfilters import slugify

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

class Tpp(Item):

    def __str__(self):
        return ''


class Company(Item):

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.getName()
    #TODO: Jenya change attr titles to NAME and DETAIL_TEXT
    def getName(self):
        name = self.getAttributeValues('NAME')
        return name[0] if name else '{EMPTY}'

    def getDescription(self):
        desc = self.getAttributeValues('DETAIL_TEXT')
        return desc[0] if desc else ''

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


class Department(Item):

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return ''


class Branch(Item):

    def __str__(self):
        return ''


class Category(Item):

    objects = models.Manager()
    hierarchy = hierarchyManager()

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
