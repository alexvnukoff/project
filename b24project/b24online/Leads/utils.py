# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user
from b24online.models import Branch, Organization, LeadsStore
from tpp.DynamicSiteMiddleware import get_current_site
from django.core.cache import cache
from django.http import Http404


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


class SpamCheck:
    def __init__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            self.ip = x_forwarded_for.split(',')[0]
        else:
            self.ip = request.META.get('REMOTE_ADDR')

        self.params = {
            'obj_ip': self.ip,
            'obj_path': request.get_host()
        }

    def get_spam_check(self):
        if cache.get('oi:%(obj_ip)s:bad' % {'obj_ip': self.ip}):
            cache.incr('oi:%(obj_ip)s:bad' % {'obj_ip': self.ip})
            raise Http404

        try:
            obj = int(cache.get('oi:%(obj_ip)s:%(obj_path)s' % self.params))
        except:
            obj = None

        if obj:
            if obj < 3:
                cache.incr('oi:%(obj_ip)s:%(obj_path)s' % self.params)
            else:
                cache.set('oi:%(obj_ip)s:bad' % {'obj_ip': self.ip}, 1, 3600)
                return False
        else:
            cache.set('oi:%(obj_ip)s:%(obj_path)s' % self.params, 1, 604800)

        return True

