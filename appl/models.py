from django.db import models
from core.models import Item
from appl.func import *

def getHierarchyTree(cls):
    classObj = (globals()[cls])

    if not issubclass(classObj, Item) and classObj.__class__.__name__ is not "Item":
        raise Exception

    tableName = classObj._meta.db_table
    pkCol = classObj._meta.pk.column
    translation = {'LEVEL': 'level'}

    query = '''SELECT PARENT_ID, CHILD_ID, LEVEL, CONNECT_BY_ISLEAF as isLeaf, model.{0}, model.{0} as id
                        FROM
                        (
                            SELECT parent_id, child_id, type
                                FROM core_relationship
                            UNION
                                SELECT NULL, {0}, null
                                    FROM {1} i
                                    WHERE NOT EXISTS
                                    (
                                        SELECT *
                                            FROM core_relationship
                                            WHERE child_id = i.{0} AND type='hier'
                                    )
                        ) rel
                        INNER JOIN {1} model ON (rel.CHILD_ID = model.{0})
                        WHERE rel.type='hier' OR PARENT_ID is null
                        CONNECT BY PRIOR  rel.CHILD_ID = rel.PARENT_ID
                        START WITH rel.PARENT_ID is NULL ;'''.format(pkCol, tableName)

    return list(classObj.objects.raw(query, translations=translation))


def getDescedantsForList(startList, cls='Item'):


    classObj = (globals()[cls])

    if not issubclass(classObj, Item) and classObj.__class__.__name__ is not "Item":
        raise Exception

    tableName = classObj._meta.db_table
    pkCol = classObj._meta.pk.column

    translation = {'LEVEL': 'level'}

    if not isinstance(startList, list):
        startList = [startList]

    query = '''SELECT PARENT_ID, CHILD_ID, LEVEL, CONNECT_BY_ISLEAF as isLeaf, model.{0}, model.{0} as id
                        FROM
                        (
                            SELECT parent_id, child_id, type
                                FROM core_relationship
                            UNION
                                SELECT NULL, {0}, null
                                    FROM {1} i
                                    WHERE NOT EXISTS
                                    (
                                        SELECT *
                                            FROM core_relationship
                                            WHERE child_id = i.{0} AND type='hier'
                                    )
                        ) rel
                        INNER JOIN {1} model ON (rel.CHILD_ID = model.{0})
                        WHERE rel.type='hier' OR PARENT_ID is null
                        CONNECT BY PRIOR  rel.CHILD_ID = rel.PARENT_ID
                        START WITH rel.CHILD_ID IN ({2});'''\
        .format(pkCol, tableName, ','.join(["%s"]*len(startList)))

    return list(classObj.objects.raw(query, startList, translations=translation))


def getItemList(parent, cls="Item", relation="rel"):

    classObj = (globals()[cls])

    if not issubclass(classObj, Item) and classObj.__class__.__name__ is not "Item":
        raise Exception

    return classObj.objects.filter(c2p__parent_id=parent, c2p__type=relation)


def getHierarchyDescedants(parent, cls):

    classObj = Department

    if not issubclass(classObj, Item):
        raise Exception

    childs = getItemList(parent, cls, "hier").values('pk')
    childs = [x['pk'] for x in childs]

    return getDescedantsForList(childs, cls)

class Tpp(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Company(Item):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def getDepartments(self):
        '''
            Get departments only for this company
        '''
        return getHierarchyDescedants(self.pk, "Department")

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

