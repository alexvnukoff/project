# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user
from b24online.models import Branch, Organization, LeadsStore
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
        email = kwargs['email']

        try:
            company_id = kwargs['company_id']
        except:
            company_id = False

        try:
            message = kwargs['message']
        except:
            message = None

        if not self.org and company_id:
            try:
                self.org = Organization.objects.get(pk=company_id)
            except Organization.DoesNotExist:
                self.org = False

        # Collect form usersites form
        if self.org and realname and email:
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

