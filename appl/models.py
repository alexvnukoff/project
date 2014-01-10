from django.db import models
from core.models import Item
from core.hierarchy import hierarchyManager

class Tpp(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Company(Item):
    name = models.CharField(max_length=128, unique=True)

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.name

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
    name = models.CharField(max_length=128)

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

