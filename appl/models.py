from django.db import models
from core.models import Item


class Tpp(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def getItemList(self, cls=None):
        i = self.c2p
        if cls:
            return globals()[cls].objects.filter(c2p__parent_id=self.pk) #TODO fix hiearchy
        else:
            return Item.objects.filter(c2p__parent_id=self.pk)


class Company(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def getItemList(self, cls=None):
        if cls:
            return globals()[cls].objects.filter(c2p__parent_id=self.pk) #TODO fix hiearchy
        else:
            return Item.objects.filter(c2p__parent_id=self.pk)


class Department(Item):
    name = models.CharField(max_length=128)

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

