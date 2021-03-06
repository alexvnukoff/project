# -*- coding: utf-8 -*-

import logging
from django.utils.timezone import now

from centerpokupok.models import UserBasket, BasketItem
from tpp.DynamicSiteMiddleware import get_current_site

logger = logging.getLogger(__name__)


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class Basket:
    def __init__(self, request):

        self.basket_id = request.session.get('uuid_hash', False)

        if self.basket_id:
            try:
                basket = UserBasket.objects.get(user_uuid=self.basket_id, site_id=get_current_site().id, checked_out=False)
            except UserBasket.DoesNotExist:
                basket = self.new(request)
        else:
            basket = self.new(request)
        self.basket = basket

        if request.session.get('company_paypal', False) and request.session.get('basket_currency', False):

            if not self.basket.currency and not self.basket.paypal:
                self.basket.currency = request.session.get('basket_currency')
                self.basket.paypal = request.session.get('company_paypal')
                self.basket.save()


    def __iter__(self):
        for item in self.basket.items.all():
            yield item

    def new(self, request):
        basket = UserBasket(created=now())
        basket.user_uuid = request.session.get('uuid_hash')
        basket.site_id = get_current_site().id
        basket.save()
        return basket

    def add(self, product, quantity=1, extra_params={}):
        try:
            if extra_params:
                raise RuntimeError()
            item = BasketItem.objects.get(basket=self.basket, product=product)
        except (BasketItem.DoesNotExist, RuntimeError):
            item = BasketItem()
            item.basket = self.basket
            item.product_id = product
            item.quantity = quantity
            if extra_params:
                item.extra_params = extra_params
            item.save()
        else: #ItemAlreadyExists
            if item.quantity:
                item.quantity += int(quantity)
            else:
                item.quantity = int(quantity)
            item.save()
        return item

    def remove(self, product):
        try:
            item = BasketItem.objects.get(basket=self.basket, product=product)
        except BasketItem.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delete()

    def update(self, product, quantity):
        try:
            item = BasketItem.objects.get(basket=self.basket, product=product)
        except BasketItem.DoesNotExist:
            raise ItemDoesNotExist
        else: #ItemAlreadyExists
            if quantity == 0:
                item.delete()
            else:
                item.quantity = int(quantity)
                item.save()

    def count(self):
        result = 0
        for item in self.basket.items.all().select_related('product'):
            result += item.quantity
        return result

    def currency(self):
        if not self.basket.currency:
            return False
        return self.basket.currency

    def paypal(self):
        if not self.basket.paypal:
            return False
        return self.basket.paypal

    def summary(self):
        result = 0
        for item in self.basket.items.all().select_related('product'):
            result += item.product.get_discount_price() * item.quantity
        return result

    def currency(self):
        """
        Return Basket's first product currentcy.
        """
        first_item = self.basket.items.select_related('product').first()
        return first_item.product.currency if first_item else None

    def clear(self):
        for item in self.basket.items.all():
            item.delete()

