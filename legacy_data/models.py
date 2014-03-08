from django.db import models

class L_User(models.Model):
    '''
        Defines buffer table for reloading users' data from CSV file
    '''
    username = models.CharField(max_length=1024)
    is_active = models.BooleanField()
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    email = models.CharField(max_length=1024)
    btx_id = models.CharField(max_length=10)
    update_date = models.DateField(null=True, blank=True)
    last_visit_date = models.DateField(null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=1024)
    personal_www = models.CharField(max_length=1024)
    icq = models.CharField(max_length=1024)
    gender = models.CharField(max_length=40)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.CharField(max_length=1024)
    phone = models.CharField(max_length=1024)
    fax = models.CharField(max_length=1024)
    cellular = models.CharField(max_length=1024)
    addr_street = models.CharField(max_length=1024)
    addr_city = models.CharField(max_length=1024)
    addr_state = models.CharField(max_length=1024)
    addr_zip = models.CharField(max_length=40)
    addr_country = models.CharField(max_length=1024)
    company = models.CharField(max_length=1024)
    department = models.CharField(max_length=1024)
    position = models.CharField(max_length=1024)
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    email_sent = models.BooleanField(default=False) #update in True if notification mail about password was sent

    def __str__(self):
        return self.username+'|'+self.first_name+'|'+self.last_name+'|'+self.email+'|'+str(self.is_active)+'|'+self.btx_id

class L_Company(models.Model):
    '''
        Defines buffer table for reloading companies' data from CSV file
    '''
    btx_id = models.CharField(max_length=10, unique=True)
    short_name = models.CharField(max_length=1024)
    detail_page_url = models.CharField(max_length=1024)
    preview_picture = models.CharField(max_length=1024)
    preview_text = models.TextField(max_length=4096)
    detail_picture = models.CharField(max_length=1024)
    detail_text = models.TextField(max_length=4096)
    create_date = models.DateField(null=True, blank=True)
    tpp_name = models.CharField(max_length=1024)
    moderator = models.CharField(max_length=1024)
    full_name = models.CharField(max_length=1024)
    ur_address = models.CharField(max_length=1024)
    fact_address = models.CharField(max_length=1024)
    tel = models.CharField(max_length=1024)
    fax = models.CharField(max_length=1024)
    email = models.CharField(max_length=1024)
    INN = models.CharField(max_length=40)
    KPP = models.CharField(max_length=40)
    OKVED = models.CharField(max_length=120)
    OKATO = models.CharField(max_length=120)
    OKPO = models.CharField(max_length=120)
    bank_account = models.CharField(max_length=120)
    bank_name = models.CharField(max_length=1024)
    director_name = models.CharField(max_length=1024)
    bux_name = models.CharField(max_length=1024)
    slogan = models.CharField(max_length=1024)
    is_active = models.BooleanField()
    branch = models.CharField(max_length=1024)
    experts = models.CharField(max_length=1024)
    map_id = models.CharField(max_length=1024)
    site = models.CharField(max_length=1024)
    country_name = models.CharField(max_length=1024)
    is_deleted = models.BooleanField()
    keywords = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    pic_completed = models.BooleanField(default=False) #update in True if pictures are reloaded from buffer DB into TPP DB
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.short_name+'|'+self.INN+'|'+self.KPP

class L_Product(models.Model):
    '''
        Defines buffer table for reloading products' data from CSV file
    '''
    btx_id = models.CharField(max_length=10, unique=True)
    prod_name = models.CharField(max_length=1024)
    detail_page_url = models.CharField(max_length=1024)
    preview_picture = models.CharField(max_length=1024)
    preview_text = models.TextField(max_length=4096)
    detail_picture = models.CharField(max_length=1024)
    detail_text = models.TextField(max_length=4096)
    create_date = models.DateField(null=True, blank=True)
    company_id = models.CharField(max_length=40)
    photos1 = models.CharField(max_length=1024)
    discount = models.CharField(max_length=40)
    add_pages = models.CharField(max_length=1024)
    tpp = models.CharField(max_length=40)
    direction = models.CharField(max_length=1024)
    is_deleted = models.BooleanField()
    photos2 = models.CharField(max_length=1024)
    file = models.CharField(max_length=1024)
    keywords = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.btx_id+'|'+self.prod_name

class L_TPP(models.Model):
    '''
        Defines buffer table for reloading TPPs' data from CSV file
    '''
    btx_id = models.CharField(max_length=10, unique=True)
    tpp_name = models.CharField(max_length=1024)
    detail_page_url = models.CharField(max_length=1024)
    preview_picture = models.CharField(max_length=1024)
    preview_text = models.TextField(max_length=4096)
    detail_picture = models.CharField(max_length=1024)
    detail_text = models.TextField(max_length=4096)
    create_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=40)
    moderator = models.CharField(max_length=1024)
    head_pic = models.CharField(max_length=1024)
    logo = models.CharField(max_length=1024)
    domain = models.CharField(max_length=1024)
    header_letter = models.CharField(max_length=1024)
    member_letter = models.CharField(max_length=1024)
    address = models.CharField(max_length=1024)
    email = models.CharField(max_length=1024)
    fax = models.CharField(max_length=1024)
    map = models.CharField(max_length=1024)
    tpp_parent = models.CharField(max_length=1024)
    phone = models.CharField(max_length=1024)
    extra = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    pic_completed = models.BooleanField(default=False) #update in True if pictures are reloaded from buffer DB into TPP DB
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.btx_id+'|'+self.tpp_name

class L_Pic2Org(models.Model):
    '''
        Defines buffer table for reloading relationships between pictures and organization from CSV file
    '''
    btx_id = models.CharField(max_length=10) # legacy company's id
    gallery_topic = models.CharField(max_length=1024)
    gallery = models.CharField(max_length=1024)
    pic_title = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.btx_id+'|'+self.org_name

class L_Pic2Prod(models.Model):
    '''
        Defines buffer table for reloading relationships between pictures and products from CSV file
    '''
    btx_id = models.CharField(max_length=10) #legacy product's id
    prod_name = models.CharField(max_length=1024)
    preview_picture = models.CharField(max_length=1024)
    detail_picture = models.CharField(max_length=1024)
    gallery = models.CharField(max_length=1024)
    completed = models.BooleanField(default=False) #update in True if is reloaded from buffer DB into TPP DB
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.btx_id+'|'+self.prod_name
