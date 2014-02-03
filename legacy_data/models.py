from django.db import models

class L_User(models.Model):
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
