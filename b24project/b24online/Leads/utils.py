# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user
from b24online.models import Branch, Company, LeadsStore
from tpp.DynamicSiteMiddleware import get_current_site


class GetLead:
    def __init__(self, request):
        self.user = get_user(request)
        try:
            self.org = get_current_site().user_site.organization
        except:
            self.org = False

    def collect(self, **kwargs):
        url_path = kwargs['url']
        realname = kwargs['realname']
        phone = kwargs['phone']
        message = kwargs['message']
        email = kwargs['email']

        try:
            company_id = kwargs['company_id']
        except:
            company_id = False

        if not self.org and company_id:
            self.org = Company.objects.get(pk=company_id)

        # Collect form usersites form
        if self.org and realname and message and email:
            lead = LeadsStore(
                url_path=url_path,
                organization=self.org,
                realname=realname,
                phone=phone,
                email=email,
                message=message
                )

            if not self.user.is_anonymous():
                lead.username = self.user

            lead.save()

