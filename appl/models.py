from django.db import models
from core.models import Item, State
from django.contrib.auth.models import Group
from random import randint
from core.hierarchy import hierarchyManager
from django.contrib.auth.decorators import login_required
import datetime

def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent_id=parent, c2p__type="rel")

class Organization (Item):

    def __init__(self, *args, **kwargs):
        super(Organization, self).__init__(*args, **kwargs)
        self.community = Group.objects.create(name='ORG-' + str(randint(1000000, 9999999)))
        print('Constructor!')

class Tpp(Organization):
    name = models.CharField(max_length=128, unique=True)

    def __init__(self, *args, **kwargs):
        super(Tpp, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default TPP State')


    def __str__(self):
        return self.name

class Company(Organization):
    name = models.CharField(max_length=128, null=True, blank=True)

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

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Department State')


    def __str__(self):
        return self.name

class Country(Item):


    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.title


class Comment(Item):


    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.title

    @staticmethod
    def spamCheck(user=None, parent_id=None):
        time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        comments = Comment.objects.filter(create_user=user, c2p__parent_id=parent_id, create_date__gt=time)
        if len(comments) > 0:
            return True


    @staticmethod
    def getCommentOfItem(parent_id=None):
        return  Comment.objects.filter(c2p__parent_id=parent_id, c2p__type="rel")




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
