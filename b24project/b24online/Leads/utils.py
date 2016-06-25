# -*- coding: utf-8 -*-
from django.conf import settings
from b24online.models import Branch, Organization, LeadsStore
from tpp.DynamicSiteMiddleware import get_current_site


class GetLead:
    def __init__(self, request):
        self.org = get_current_site().user_site.organization
        if not request.user or not request.user.is_authenticated() or request.user.is_anonymous():
            self.user = False
        else:
            self.user = request.user

    def collect(self, **kwargs):
        subject = kwargs['subject']
        message = kwargs['message']
        email = kwargs['email']
        phone = kwargs['phone']

        # Collect form usersites form
        if subject and message and email:
            lead = LeadsStore(
                    organization=self.org,
                    subject=subject,
                    email=email,
                    message=message)

            if self.user:
                lead.username = self.user

            lead.save()


