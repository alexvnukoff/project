from django.db import models

class L_User(models.Model):
    '''
        Defines buffer table for reloading users' data from CSV file
    '''
    username = models.CharField(max_length=1024, unique=True)
    is_active = models.BooleanField()
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    email = models.CharField(max_length=1024, unique=True)
    btx_id = models.CharField(max_length=10, unique=True)
    tpp_id = models.CharField(max_length=10, unique=True) #save generated id in TPP DB
    update_date = models.DateField(null=True, blank=True)
    last_visit_date = models.DateField(null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
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
    detail_picture = models.CharField(max_length=1024)
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
    tpp_id = models.CharField(max_length=10) #save generated id in TPP DB

    def __str__(self):
        return self.short_name+'|'+self.INN+'|'+self.KPP

