from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet
from core.models import Item, State, Relationship
from core.hierarchy import hierarchyManager
from core.models import User, ItemManager
from django.utils.timezone import now
import datetime
from time import mktime, strptime
from django.db.models import Count, ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from urllib.parse import urlencode
from urllib.request import Request, urlopen


#----------------------------------------------------------------------------------------------------------
#             Model Functions
#----------------------------------------------------------------------------------------------------------
def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent=parent, c2p__type="relation")


def getSpecificParent(cls, child):
    '''
        Returns not hierarchical parents of specific type
            Example: getSpecificParent("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(p2c__child=child, c2p__type="relation")


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
    paid_till_date = models.DateField(null=True)

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

        classes = [Product, News, Tender, InnovationProject, BusinessProposal, Exhibition, Department]

        for klass in classes:
            objects = klass.objects.filter(c2p__parent=self.pk)

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

    SITES = (
        ('usersites', 'User Sites'),
        ('b2c', 'B2C'),
        ('b2b', 'B2B'),
    )

    site_type = models.CharField(max_length=200, choices=SITES)

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

class BpCategories(Item):


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
        comments = Comment.objects.filter(create_user=user, c2p__parent=parent_id, create_date__gt=time)
        if len(comments) > 0:
            return True


    @staticmethod
    def getCommentOfItem(parent_id):
        """
        Return QuerySet of comments that related to item
        """
        return Comment.objects.filter(c2p__parent=parent_id, c2p__type="relation")

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
         return self.getName()

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

class PayPalPayment(Payment):
    """
    Defines entity for PayPal payments
    """
    address_city = models.CharField(blank=True, null=True, max_length=1024)
    address_country = models.CharField(blank=True, null=True, max_length=1024)
    address_country_code = models.CharField(blank=True, null=True, max_length=1024)
    address_name = models.CharField(blank=True, null=True, max_length=1024)
    address_state = models.CharField(blank=True, null=True, max_length=1024)
    address_status = models.CharField(blank=True, null=True, max_length=1024)
    address_street = models.CharField(blank=True, null=True, max_length=1024)
    address_zip = models.CharField(blank=True, null=True, max_length=32)
    business = models.CharField(blank=True, null=True, max_length=255)          # receiver's business account e-mail
    charset = models.CharField(blank=True, null=True, max_length=32)            # receiver's charset
    custom = models.CharField(blank=True, null=True, max_length=1024)           # custom field for our purpose
    first_name = models.CharField(blank=True, null=True, max_length=128)        # first name of payer
    last_name = models.CharField(blank=True, null=True, max_length=128)         # last name of payer
    handling_amount = models.CharField(blank=True, null=True, max_length=32)    # payer's account amount
    ipn_track_id = models.CharField(blank=True, null=True, max_length=64)       # instant payment notification id
    item_name = models.CharField(blank=True, null=True, max_length=1024)        # payment purpose
    item_number = models.CharField(blank=True, null=True, max_length=1024)      # payment subject
    mc_currency = models.CharField(blank=True, null=True, max_length=4)         # payment currency
    mc_fee = models.CharField(blank=True, null=True, max_length=16)             # payment fee
    mc_gross = models.CharField(blank=True, null=True, max_length=32)           # payment sum
    notify_version = models.CharField(blank=True, null=True, max_length=16)
    payer_business_name = models.CharField(blank=True, null=True, max_length=1024)
    payer_email = models.CharField(blank=True, null=True, max_length=255)
    payer_id = models.CharField(blank=True, null=True, max_length=255)
    payer_status = models.CharField(blank=True, null=True, max_length=32)
    payment_date = models.DateTimeField(blank=True, null=True)                  # payment date in PDT (Pacific Daylight Time)
    payment_fee = models.CharField(blank=True, null=True, max_length=16)        # payment transaction fee
    payment_gross = models.CharField(blank=True, null=True, max_length=32)      # payment sum
    payment_status = models.CharField(blank=True, null=True, max_length=32)
    payment_type = models.CharField(blank=True, null=True, max_length=32)
    pending_reason = models.CharField(blank=True, null=True, max_length=255)
    protection_eligibility = models.CharField(blank=True, null=True, max_length=32)
    quantity = models.CharField(blank=True, null=True, max_length=16)           # purchase q-ty
    receiver_email = models.CharField(blank=True, null=True, max_length=255)
    receiver_id = models.CharField(blank=True, null=True, max_length=255)
    residence_country = models.CharField(blank=True, null=True, max_length=1024)
    shipping = models.CharField(blank=True, null=True, max_length=32)           # cost of shipping
    tax = models.CharField(blank=True, null=True, max_length=32)                # tax for shipping
    test_ipn = models.CharField(blank=True, null=True, max_length=4)            # ipn from sandbox
    transaction_subject = models.CharField(blank=True, null=True, max_length=1024)
    txn_id = models.CharField(unique=True, max_length=128)
    txn_type = models.CharField(blank=True, null=True, max_length=255)
    verify_sign = models.CharField(blank=True, null=True, max_length=1024)


    class Meta:
        permissions = (
            ("read_paypalpayment", "Can read paypalpayment"),
        )


    def __str__(self):
        return 'tx-id: ' + self.txn_id


    def verifyAndSave(self, request, pay_env=0):
        """
        Verify notification from PayPal and save all attributes.
        Pay_env = 0 if this is a test environment
        """
        if request.method == 'POST':
            # SEND POSTBACK FOR PAYMENT VALIDATION
            # prepares provided data set to inform PayPal we wish to validate the response
            params = urlencode('').encode('utf-8')
            if pay_env != 0:
                req = Request('https://www.paypal.com/cgi-bin/webscr/', params)
            else:
                req = Request('https://www.sandbox.paypal.com/cgi-bin/webscr/', params)
            # send empty POST 200 response to PayPal
            response = urlopen(req)
#
            # sends the data and request to the PayPal
            data = request.POST.copy()
            data['cmd'] = "_notify-validate"
            params = urlencode(data).encode('utf-8')
            if pay_env != 0:
                req = Request('https://www.paypal.com/cgi-bin/webscr/', params)
            else:
                req = Request('https://www.sandbox.paypal.com/cgi-bin/webscr/', params)

            #reads the response back from PayPal
            response = urlopen(req)
            status = response.read()
            # If not verified
            if not status == b"VERIFIED":
                return False
#            else:
#                self.payment_status = 'VERIFIED'

            if not PayPalPayment.objects.filter(txn_id=request.POST.get('txn_id', '')).exists():
                self.txn_id = request.POST.get('txn_id', '')
                self.address_city = request.POST.get('address_city', '')
                self.address_country = request.POST.get('address_country', '')
                self.address_country_code = request.POST.get('address_country_code', '')
                self.address_name = request.POST.get('address_name', '')
                self.address_state = request.POST.get('address_state', '')
                self.address_status = request.POST.get('address_status', '')
                self.address_street = request.POST.get('address_street', '')
                self.address_zip = request.POST.get('address_zip', '')
                self.business = request.POST.get('business', '')
                self.charset = request.POST.get('charset', '')
                self.custom = request.POST.get('custom', '')
                self.first_name = request.POST.get('first_name', '')
                self.last_name = request.POST.get('last_name', '')
                self.handling_amount = request.POST.get('handling_amount', '')
                self.ipn_track_id = request.POST.get('ipn_track_id', '')
                self.item_name = request.POST.get('item_name', '')
                self.item_number = request.POST.get('item_number', '')
                self.mc_currency = request.POST.get('mc_currency', '')
                self.mc_fee = request.POST.get('mc_fee', '')
                self.mc_gross = request.POST.get('mc_gross', '')
                self.notify_version = request.POST.get('notify_version', '')
                self.payer_business_name = request.POST.get('payer_business_name', '')
                self.payer_email = request.POST.get('payer_email', '')
                self.payer_id = request.POST.get('payer_id', '')
                self.payer_status = request.POST.get('payer_status', '')

                # receive date in PDT bound
                from pytz import timezone
                ts = strptime(request.POST.get('payment_date', '00:00:00 1 Jan, 2014')[:-4], "%H:%M:%S %b %d, %Y")
                pd = datetime.datetime.fromtimestamp(mktime(ts))
                self.payment_date = pd.replace(tzinfo=timezone('US/Pacific'))

                self.payment_fee = request.POST.get('payment_fee', '')
                self.payment_gross = request.POST.get('payment_gross', '')
                self.payment_status = request.POST.get('payment_status', '')
                self.payment_type = request.POST.get('payment_type', '')
                self.pending_reason = request.POST.get('pending_reason', '')
                self.protection_eligibility = request.POST.get('protection_eligibility', '')
                self.quantity = request.POST.get('quantity', '')
                self.receiver_email = request.POST.get('receiver_email', '')
                self.receiver_id = request.POST.get('receiver_id', '')
                self.residence_country = request.POST.get('residence_country', '')
                self.shipping = request.POST.get('shipping', '')
                self.tax = request.POST.get('tax', '')
                self.test_ipn = request.POST.get('test_ipn', '')
                self.transaction_subject = request.POST.get('transaction_subject', '')
                self.txn_type = request.POST.get('txn_type', '')
                self.verify_sign = request.POST.get('verify_sign', '')
                self.create_user = User.objects.get(email='special@tppcenter.com')
                try:
                    self.save()
                except Exception as e:
                    pass
            else:
                pp_rec = PayPalPayment.objects.get(txn_id=request.POST.get('txn_id', ''))
                if pp_rec.payment_status != request.POST.get('payment_status', ''):
                    pp_rec.payment_status = request.POST.get('payment_status', '')
                    pp_rec.save()

            return True
        else:
            return False


    def getPaymentStatus(self):
        """
        Returns payment status
        """
        return self.payment_status


    def getPaymentDatePDT(self):
        """
        Returns payment date for PDT bound (original)
        """
        return self.payment_date


    def getPaymentDateUTC(self):
        """
        Returns payment date for UTC bound. Receive date in PDT format (UTC = PDT + 7 hours)
        """
        return self.payment_date + datetime.timedelta(hours=7)


    def getAllAttributes(self):
        """
        Returns all payment attributes as dictionary
        """
        return {}


    def getSender(self):
        """
        Return payment sender instance
        """
        return ''


    def getPaymentReceiver_s(self):
        """
        Return list of payment receiver(s)
        """
        return self.receiver_email


    def getPaymentAmount(self):
        """
        Return payment sum and currency
        """
        return self.mc_gross

    def getPaymentCurrency(self):
        return self.mc_currency

    def getItemNumber(self):
        return self.item_number

    def getItemQty(self):
        return self.quantity

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

    payed = models.BooleanField(default=False)
    payDate = models.DateTimeField(blank=True, null=True)

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


class Vacancy(Item):
    active = ItemManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ("read_vacancy", "Can read vacancy"),
        )

    def __str__(self):
        return self.getName()

class staticPages(Item):

    PAGE_TYPES = (
        ('about', 'About'),
        ('advices', 'Advices'),
        ('contacts', 'Contacts'),
    )

    onTop = models.BooleanField(default=False)
    pageType = models.CharField(max_length=200, choices=PAGE_TYPES)

    def __str__(self):
        return self.getName()


class topTypes(Item):
    modelType = models.OneToOneField(ContentType, related_name="top")


from core.amazonMethods import addFile as uploadFile

class Messages(Item):
    text = models.CharField(max_length=1024, null=False, default='EMPTY')
    file = models.FileField(upload_to=uploadFile, null=True, max_length=255)
    was_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Signal receivers
#----------------------------------------------------------------------------------------------------------
@receiver(pre_save)
def itemInstanceType(instance, **kwargs):

    if not issubclass(instance.__class__, Item):
        return

    if not getattr(instance, "contentType", None) or instance.contentType == '':
        object = ContentType.objects.get(model=str(instance.__class__.__name__).lower())
        instance.contentType = object


#----------------debug site deletion--------------------------------------------------------------------
from django.contrib.sites.models import Site
from tpp.SiteUrlMiddleWare import get_request
from django.core.mail import EmailMessage

@receiver(pre_delete, sender=Site)
def delSiteMonitor(instance, **kwargs):
    '''
       Create default Department if Company hasn't it.
    '''
    request = get_request()
    subject = str(instance.name) + ' ' + str(request.user) + ' ' + str(datetime.datetime.now())
    mail = EmailMessage(subject, '', 'noreply@tppcenter.com', ['afend69@gmail.com', 'jenyapri@tppcenter.com'])
    mail.send()
#-------------------------------------------------------------------------------------------------------


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
