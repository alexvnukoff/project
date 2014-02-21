from django.db import models
from django.db.models.query import QuerySet
from core.models import Item, State, Relationship, User
from django.contrib.auth.models import Group, Permission
from random import randint
from core.hierarchy import hierarchyManager
from core.models import User, ItemManager
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import datetime
from django.db.models import Count, F
from django.db.models.signals import pre_save
from django.dispatch import receiver
from itertools import chain




#----------------------------------------------------------------------------------------------------------
#             Model Functions
#----------------------------------------------------------------------------------------------------------
def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent_id=parent, c2p__type="relation")


def getSpecificParent(cls, child):
    '''
        Returns not hierarchical parents of specific type
            Example: getSpecificParent("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(p2c__child_id=child, c2p__type="relation")

class Organization (Item):
    active = ItemManager()
    objects = models.Manager()

    def addWorker(self, user):
        '''
            Adds User into organization's community Group
        '''
        pass

    class Meta:
        permissions = (
            ("read_organization", "Can read organization"),
        )

    def __str__(self):
        return self.getName()


class Tpp(Organization):
    active = ItemManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ("read_tpp", "Can read tpp"),
        )

    def __init__(self, *args, **kwargs):
        super(Tpp, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default TPP State')


    def __str__(self):
        return self.getName()

class Company(Organization):

    class Meta:
        permissions = (
            ("read_company", "Can read Company"),
        )
    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.status = State.objects.get(title='Default Company State')

    def __str__(self):
        return self.getName()


    def getDescription(self):
        desc = self.getAttributeValues('DETAIL_TEXT')
        return desc[0] if desc else ''

    def getCountry(self):
        return 100

    def getBranches(self):
        return 1

    def reindexItem(self):
        super(Company, self).reindexItem()

        classes = [Product]

        for klass in classes:
            objects = klass.objects.filter(c2p__parent_id=self.pk)

            for obj in objects:
                obj.reindexItem()

    @staticmethod
    def isCompany(instance):
        from django.core.exceptions import ObjectDoesNotExist

        if isinstance(instance, Company):
            return True
        #or
        try:
            if hasattr(instance.organization, 'company'):
                return True
        except ObjectDoesNotExist:
            return False

        return False

    def getDepartments(self):
        '''
            Get dict of departments only for this Company
            this method returns a dictionary that contains a level , id and parent of each member
             as well as the result dictionary stores the tree structure

             Example: Company(pk=1).getDepartments()
        '''
        childs = Department.hierarchy.getChild(self.pk).values('pk')
        childs = [x['pk'] for x in childs]
        return Department.hierarchy.getDescedantsForList(childs)

    def getStoreCategories(self, products=None):

        if products is None:
            products = Product.objects.all()

        return Category.objects.filter(p2c__child__c2p__parent=self.pk, p2c__child__in=products)\
            .values('pk').annotate(childCount=Count('pk'))

class Department(Organization):

    active = ItemManager()
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
        return self.getName()

class Branch(Item):

    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.getName()

class NewsCategories(Item):

    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.getName()

class Country(Item):

    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.getName()


class InnovationProject(Item):

    active = ItemManager()
    objects = models.Manager()


    def __str__(self):
        return self.getName()


class Comment(Item):
    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.title

    @staticmethod
    def spamCheck(user=None, parent_id=None):
        '''
        Method check if current user, sent comment less than one minute ago
        user = request.user
        parent_id = id , of Item element that related to comment(News for example)
        '''
        time = now() - datetime.timedelta(minutes=1)
        comments = Comment.objects.filter(create_user=user, c2p__parent_id=parent_id, create_date__gt=time)
        if len(comments) > 0:
            return True


    @staticmethod
    def getCommentOfItem(parent_id):
        """
        Return QuerySet of comments that related to item
        """
        return Comment.objects.filter(c2p__parent_id=parent_id, c2p__type="relation")

class SystemMessages(Item):
     MESSAGE_TYPE = (
        ('item_creating', 'Creating item in process'),
        ('item_updating', 'Update item in process'),
        ('item_created', 'Item created'),
        ('item_updated', 'Item Updated'),
        ("error_creating", "Error in creating"))
     type = models.CharField(max_length=200, choices=MESSAGE_TYPE)

     def __str__(self):
        return self.getName()



class Notification(Item):
    user = models.ForeignKey(User, related_name="user2notif")
    message = models.ForeignKey(SystemMessages, related_name="mess2notif")
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.getName()


class Category(Item):
    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()


    def __str__(self):
        return self.title

class Product(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

    @staticmethod
    def getCoupons(querySet=False):

        timeNow = now()

        if querySet is not False:
            return querySet.filter(item2value__attr__title="COUPON_DISCOUNT", item2value__title__gt=0,
                                   item2value__end_date__gt=now, item2value__start_date__lte=timeNow)
        else:
            return Product.active.get_active_related().filter(item2value__attr__title="COUPON_DISCOUNT", item2value__title__gt=0,
                                          item2value__end_date__gt=now, item2value__start_date__lte=timeNow)

    @staticmethod
    def getCategoryOfPRoducts(productQuerySet, attr):
        if isinstance(productQuerySet, QuerySet):
              products_id = [product.pk for product in productQuerySet]
        else:
              products_id = productQuerySet
        categories = Category.objects.filter(p2c__child_id__in=products_id).values("id", "p2c__child_id")
        categories_id = [category['id'] for category in categories]
        products = Item.getItemsAttributesValues(attr, products_id)
        category = Item.getItemsAttributesValues(("NAME",), categories_id)
        cat = {}
        for item in categories:
            cat[item['p2c__child_id']] = item['id']

        for key, product in products.items():
            cat_name = category[cat[key]]['NAME'][0] if cat.get(key, "") else ""

            product.update({"CATEGORY_NAME": cat_name})
            product.update({"CATEGORY_ID": cat.get(key, "")})

        return products

    def getProdWithDiscount(querySet=False):

        timeNow = now()

        if querySet is not False:
            return querySet.filter(item2value__attr__title="DISCOUNT", item2value__title__gt=0,
                                   item2value__end_date__isnull=True, item2value__start_date__lte=timeNow)
        else:
            return Product.active.get_active_related().filter(item2value__attr__title="DISCOUNT", item2value__title__gt=0,
                                          item2value__end_date__isnull=True, item2value__start_date__lte=timeNow)

    @staticmethod
    def getNew(productQuery=False):
        if not productQuery and not isinstance(productQuery, QuerySet):
            return Product.active.get_active_related().order_by('-pk')
        else:
            return productQuery.order_by('-pk')

    @staticmethod
    def getTopSales(productQuery=False):

        extra = '''nvl((SELECT COUNT({prodTable}.{prodPK})
                FROM {relTable}
                INNER JOIN {orderTable} ON ({orderTable}.{orderPK} = {relTable}.parent_id)
                WHERE {relTable}.child_id = {prodTable}.{prodPK}
                GROUP BY {relTable}.child_id), 0)'''.format(orderTable=Order._meta.db_table,
                                                                   orderPK=Order._meta.pk.column,
                                                                   prodTable=Product._meta.db_table,
                                                                   prodPK=Product._meta.pk.column,
                                                                   relTable=Relationship._meta.db_table)

        if not productQuery and not isinstance(productQuery, QuerySet):
            return Product.active.get_active_related().extra(select={'popular': extra}).order_by('-popular')
        else:
            return productQuery.extra(select={'popular': extra}).order_by('-popular')

class License(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

class Greeting(Item):
    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Service(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

class Favorite(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

class Invoice(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class News(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Article(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Announce(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Review(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Rating(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''


class Payment(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''


class Shipment(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''


class Tender(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Advertising(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''


class Rate(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''

class Order(Item):

    active = ItemManager()
    objects = models.Manager()


    def __str__(self):
        return ''


class Basket(Item):
    active = ItemManager()
    objects = models.Manager()
    class Meta:
        permissions = (
            ("read_basket", "Can read basket"),
        )

    def __str__(self):
        return ''


class Cabinet(Item):
    active = ItemManager()
    objects = models.Manager()
    user = models.ForeignKey(User, related_name="cabinet")

    def __str__(self):
        return self.title + '-' + self.user.username


class Document(Item):
    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return ''

class BusinessProposal(Item):
    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()




class Gallery(Item):
      active = ItemManager()
      objects = models.Manager()
      photo = models.ImageField(verbose_name='Avatar',  upload_to='gallery/', blank=True, null=True)

      def __str__(self):
          return str(self.photo)



class AdditionalPages(Item):
      active = ItemManager()
      objects = models.Manager()
      content = models.TextField(null=True)

      def __str__(self):
          return str(self.title)


class Exhibition(Item):
    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


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
