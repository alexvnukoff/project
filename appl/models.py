from django.db import models
from django.db.models.query import QuerySet
from core.models import Item, State, Relationship
from core.hierarchy import hierarchyManager
from core.models import User, ItemManager
from django.db.models import Q
from django.utils.timezone import now
import datetime
from django.db.models import Count, ObjectDoesNotExist
from django.db.models.signals import post_save
from django.utils.translation import trans_real
from tpp.SiteUrlMiddleWare import get_request
from django.dispatch import receiver

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

    def parentTppCommunityName(self):
        return Organization.objects.filter(p2c__child=self.pk).values_list('community__name', flat=True)


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
        desc = self.getAttributeValues('TEXT_DETAIL')
        return desc[0] if desc else ''

    def getTpp(self):
        try:
            return Tpp.objects.filter(p2c__child=self.pk, p2c__type="relation")
        except ObjectDoesNotExist:
            return None

    def getCountry(self):
            return Country.objects.get(p2c__child=self.pk, p2c__type="dependence")

    def getBranches(self):
        try:
            return Branch.objects.filter(p2c__child=self.pk, p2c__type="relation")
        except ObjectDoesNotExist:
            return None

    def reindexItem(self):
        super(Company, self).reindexItem()

        classes = [Product, News, Tender, InnovationProject, BusinessProposal, Exhibition]

        for klass in classes:
            objects = klass.objects.filter(c2p__parent_id=self.pk)

            for obj in objects:
                obj.reindexItem()

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

class AdvOrder(Item):

    def __str__(self):
        return ''

class Requirement(Item):

    active = ItemManager()
    objects = models.Manager()


    def __str__(self):
        return self.getName()


class AdvBannerType(Item):

    active = ItemManager()
    objects = models.Manager()

    enableBranch = models.BooleanField(default=False)
    enableTpp = models.BooleanField(default=False)
    enableCountry = models.BooleanField(default=True)

    def __str__(self):
        return self.getName()


class AdvertisementItem(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

class AdvTop(AdvertisementItem):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()

class AdvBanner(AdvertisementItem):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class NewsCategories(Item):

    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()

    def __str__(self):
        return self.getName()

class UserSites(Item):

    active = ItemManager()
    objects = models.Manager()

    organization = models.ForeignKey(Organization, null=True, blank=True)


class TppTV(Item):

    active = ItemManager()
    objects = models.Manager()
    hierarchy = hierarchyManager()
    class Meta:
        permissions = (
            ("read_tpptv", "Can read tpptv"),
        )

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

class ExternalSiteTemplate(Item):
    objects = models.Manager()
    active = ItemManager()

    def __str__(self):
        return self.getName()


class Notification(Item):
    user = models.ForeignKey(User, related_name="user2notif")
    message = models.ForeignKey(SystemMessages, related_name="mess2notif")
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.getName()


class Category(Item):
    objects = models.Manager()
    hierarchy = hierarchyManager()
    #active = ItemManager()


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

class Resume(Item):

    active = ItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.getName()


class Article(Item):

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

      def getTitle(self):
        title = self.getAttributeValues('NAME')
        return title[0] if title else self.title

      def getContent(self):
        content = self.getAttributeValues('DETAIL_TEXT')
        return content[0] if content else self.content


class Exhibition(Item):
    active = ItemManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ("read_exhibition", "Can read exhibition"),

        )

    def __str__(self):
        return self.getName()

# do not move this import from here
from core.amazonMethods import addFile as uploadFile
class Messages(Item):
    text = models.CharField(max_length=1024, null=False, default='EMPTY')
    file = models.FileField(upload_to=uploadFile, null=True, max_length=255)
    was_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Vacancy(Item):
    active = ItemManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ("read_vacancy", "Can read vacancy"),
        )

    def __str__(self):
        return self.getName()

#----------------------------------------------------------------------------------------------------------
#             Signal receivers
#----------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=Company)
def companyCommunity(instance, **kwargs):
    '''
       Create default Department if Company hasn't it.

    if not Department.objects.filter(c2p__parent=instance.pk).exists():
        request = get_request()
        if request:
            usr = request.user
        else:
            usr = User.objects.get(pk=1)

        try:
            dep = Department.objects.create(title='DEPARTMENT_FOR_COMPANY_ID:'+str(instance.pk), create_user=usr)
            trans_real.activate('ru') #activate russian locale
            res = dep.setAttributeValue({'NAME':'Администрация'}, usr)
            trans_real.deactivate() #deactivate russian locale

            if not res:
                dep.delete()
                return False
            try:
                Relationship.objects.create(parent=instance, child=dep, type='hierarchy', create_user=usr)
                dep.reindexItem()
            except:
                print('Can not create Relationship between Department ID' + dep.pk + ' and Company ID' + instance.pk)
                dep.delete()
        except Exception as e:
            print('Can not create Department for Company ID', instance.pk)
            pass

        if not Vacancy.objects.filter(c2p__parent=dep.pk).exists():
            try:
                vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:'+str(dep.pk), create_user=usr)
                trans_real.activate('ru') #activate russian locale
                res = vac.setAttributeValue({'NAME':'Работник(ца)'}, usr)
                trans_real.deactivate() #deactivate russian locale

                if not res:
                    vac.delete()
                    return False
                try:
                    Relationship.objects.create(parent=dep, child=vac, type='hierarchy', create_user=usr)
                    vac.reindexItem()
                    #add current user to default Vacancy
                except Exception as e:
                    print('Can not create Relationship between Vacancy ID:' + str(vac.pk) + 'and Department ID:'+
                          str(dep.pk) + '. The reason is:' + str(e))
                    vac.delete()
            except Exception as e:
                print('Can not create Vacancy for Department ID:' + str(dep.pk) + '. The reason is:' + str(e))
                pass
    '''

@receiver(post_save, sender=Tpp)
def tppCommunity(instance, **kwargs):
    '''
       Create default Department if Tpp hasn't it.

    if not Department.objects.filter(c2p__parent=instance.pk).exists():
        request = get_request()
        if request:
            usr = request.user
        else:
            usr = User.objects.get(pk=1)

        try:
            dep = Department.objects.create(title='DEPARTMENT_FOR_TPP_ID:'+str(instance.pk), create_user=usr)
            trans_real.activate('ru') #activate russian locale
            res = dep.setAttributeValue({'NAME':'Администрация'}, usr)
            trans_real.deactivate() #deactivate russian locale

            if not res:
                dep.delete()
                return False
            try:
                Relationship.objects.create(parent=instance, child=dep, type='hierarchy', create_user=usr)
                dep.reindexItem()
            except:
                dep.delete()
                print('Can not create Relationship between Department ID'+dep.pk+' and TPP ID'+instance.pk)
                raise Exception('Can not create Relationship between Department ID' +str(dep.pk)+ ' and TPP ID'+ instance.pk)

        except Exception as e:
            print('Can not create Department for TPP ID', instance.pk)
            raise Exception('Can not create Department for TPP ID: %s' % instance.pk)
            pass

        if not Vacancy.objects.filter(c2p__parent=dep.pk).exists():
            try:
                vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:'+str(dep.pk), create_user=usr)
                trans_real.activate('ru') #activate russian locale
                res = vac.setAttributeValue({'NAME':'Работник(ца)'}, usr)
                trans_real.deactivate() #deactivate russian locale

                if not res:
                    vac.delete()
                    return False
                try:
                    Relationship.objects.create(parent=dep, child=vac, type='hierarchy', create_user=usr)
                    vac.reindexItem()
                    #add current user to default Vacancy
                except Exception as e:
                    print('Can not create Relationship between Vacancy ID:' + str(vac.pk) + 'and Department ID:'+
                          str(dep.pk) + '. The reason is:' + str(e))
                    vac.delete()
            except Exception as e:
                print('Can not create Vacancy for Department ID:' + str(dep.pk) + '. The reason is:' + str(e))
    '''
