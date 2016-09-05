# -*- encoding: utf-8 -*-

import uuid
import logging

logger = logging.getLogger(__name__)


class Basket(object):
    def process_request(self, request):
        if not request.session.get('uuid_hash'):
            request.session['uuid_hash'] = str(uuid.uuid4())