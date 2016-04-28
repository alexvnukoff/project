#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Unittests for :app:`usersites` application.
"""

import os
import sys

sys.path += ['.', '..']
os.environ['DJANGO_SETTINGS_MODULE'] = 'tpp._usersites_settings'

import django

django.setup()

import json
import unittest

from django.conf import settings
from django.utils.translation import ugettext as _

from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.reverse import reverse

# Models
from b24online.models import User

EXTRA_HEADERS = {
    'HTTP_HOST': 'ru.mcs.org.il',
}

# Admin user info
ADMIN_USER_DATA = {
    'email': 'admin@example.b24online.com',
    'password': 'admin',
    'is_staff': True,
    'is_active': True,
    'is_superuser': True,
    'is_commando': True,
}

# Ordinary user data
NEW_USER_DATA = {
    'email': 'tester@example.b24online.com',
    'password': 'tester',
    'is_active': True,
    'is_staff': False,
    'is_superuser': True,
    'is_commando': True,
}


class TestQuestionnaire(unittest.TestCase):

    def setUp(self):
        # Tests client
        self.client = APIClient()

        # Users
        try:
            self.admin = User.objects.get(email=ADMIN_USER_DATA['email'])
        except User.DoesNotExist:
            self.admin = User(**ADMIN_USER_DATA)
            self.admin.set_password(ADMIN_USER_DATA['password'])
            self.admin.save()

        try:
            self.user = User.objects.get(email=NEW_USER_DATA['email'])
        except User.DoesNotExist:
            self.user = User(**NEW_USER_DATA)
            self.user.set_password(NEW_USER_DATA['password'])
            self.user.save()

        self.client.login(
            email=ADMIN_USER_DATA['email'],
            password=ADMIN_USER_DATA['password']
        )

    def getQuestionnaires(self):
        url = reverse('api:questionnaire-list')
        response = self.client.get(url, format='json', **EXTRA_HEADERS)
        return json.loads(response.content.decode('utf-8'))

    def testQuestionnaireList(self):
        """
        Test the tester user login.
        """
        try:
            self._questionnaires = self.getQuestionnaires()
        except ValueError:
            raise AssertionError(
                _(u'Invalid response content format, not a JSON'))

    def testQuestionnaireDetail(self):
        """
        Test the Questionnaires list.
        """
        self._questionnaries = self.getQuestionnaires()
        print(self._questionnaries)
                                                                                                           

if __name__ == '__main__':
    unittest.main()
