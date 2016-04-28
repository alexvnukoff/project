# -*- encoding: utf-8 -*-

"""
The tool to taste the :app:`Questionnaires` application.
"""

import json
import logging 

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext as _

from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.reverse import reverse

# Models
from b24online.models import User

logger = logging.getLogger('debug')

EXTRA_HEADERS = {
    'HTTP_HOST': 'ru.mcs.org.il',
}

# Shortcuts
def _g(items, attr_name='name'):
    return [item.get(attr_name) for item in items]
    

class Command(BaseCommand):
    """
    Check how the application works by means of API.
    """ 
    
    def add_arguments(self, parser):
        """
        Add the extra args.
        """
        parser.add_argument('--site-id', type=int, action='store',
                            required=False, help=u'Site ID')
        parser.add_argument('--qid', type=int, action='store',
                            required=False, help=u'Selected Questionnaire ID')

    def handle(self, *args, **options):
        """
        Try to answer the Questionnaire's questions.
        
        Steps:
            * initialize;
            * select the `Questionnaire`;
            * select the instance's questions;
            * answer the questions and invite the second participant;
            * answer by second participant and recieve the recommendations;
            * get the results.
        """
        self._init(*args, **options)
        self._select_questionnaire()        
        self._check_questionnaire()
        self._get_questions()
        
    def _init(self, *args, **options):
        """
        Init the processing: select site, initialize client and necessary urls.
        """    
        cls = type(self)
        
        # Selected Site
        site_id = options.get('site_id')
        if site_id:
            try:
                self._site = Site.objects.get(pk=site_id)
            except Site.DoesNotExist:
                raise CommandError(
                    'Site with ID="%d" does not exist' % site_id
                )
        else:
            self._site = get_current_site(None)
        cls.log(self._site.domain, prompt='Selected site: %s')    

        # API client
        self._client = APIClient()
        
        # Quest. ID
        self._quest_id = options.get('qid')
        self._quest = None
        
    @classmethod
    def log(cls, msg, prompt='', *args):
        logger.debug(prompt + msg, *args)
        
    @classmethod
    def log_list(cls, items, prompt=''):
        cls.log(prompt)
        for item in items:
            cls.log(str(item), prompt=' * ')    
        
    def get_response(self, url):
        return self._client.get(url, format='json', **EXTRA_HEADERS)
        
    @classmethod
    def get_response_content(cls, response):
        """
        Deserialize the JSON content.
        """
        try:
            return json.loads(response.content.decode('utf-8'))
        except ValueError:
            raise CommandError(
                'There is an error within json deserioalization'
            )
        
    def _select_questionnaire(self):
        """
        Select the `Questionnaire`.
        """
        cls = type(self)

        # Get all quest-s for site company.
        self._quests = cls.get_response_content(
            self.get_response(reverse('api:questionnaire-list'))
        )
        if self._quests:
            cls.log_list(_g(self._quests), prompt='The site company quests:')
            q_data = dict([item.get('id'), item] for item in self._quests)
            if self._quest_id:
                self._quest = q_data.get(self._quest_id)
            else:
                self._quest = self._quests[0]
                self._quest_id = self._quest.get('id')
        
        if not self._quest:
            raise CommandError('There are no any quests for site')
        cls.log(self._quest.get('name'), prompt='Selected questionnaire: ')    
            
    def _check_questionnaire(self):
        """
        Return the 'detail' content.
        """
        cls = type(self)

        url = reverse('api:questionnaire-detail', args=[self._quest_id])
        quest_data = cls.get_response_content(self.get_response(url))
        cls.log(quest_data.get('name'), prompt='Check once more: ')        
            
    def _get_questions(self):
        """
        Return the selected quest. questions.        
        """
        cls = type(self)
        
        url = reverse('api:questionnaire-questions', args=[self._quest_id])
        self._questions = cls.get_response_content(self.get_response(url))
        cls.log_list(_g(self._questions, 'question_text'), 
                     prompt='Questions list')        
        