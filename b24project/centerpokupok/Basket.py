# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.timezone import now
from centerpokupok.models import UserBasket, BasketItem
from django.contrib.sites.shortcuts import get_current_site


class ItemAlreadyExists(Exception):
    pass

class ItemDoesNotExist(Exception):
    pass

class Basket:
    def __init__(self, request):

        self.basket_id = request.session.get('uuid_hash', False)

        if self.basket_id:
            try:
                basket = UserBasket.objects.get(user_uuid=self.basket_id, site_id=get_current_site(request).id, checked_out=False)
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
        basket.site_id = get_current_site(request).id
        basket.save()
        return basket

    def add(self, product, quantity=1):
        try:
            item = BasketItem.objects.get(basket=self.basket, product=product)
        except BasketItem.DoesNotExist:
            item = BasketItem()
            item.basket = self.basket
            item.product_id = product
            item.quantity = quantity
            item.save()
        else: #ItemAlreadyExists
            item.quantity = int(quantity)
            item.save()

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

    def clear(self):
        for item in self.basket.items.all():
            item.delete()

