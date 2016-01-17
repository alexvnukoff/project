from appl.models import (Article, Basket, Company, Cabinet, Department, Document,
                         Invoice, News, Order, Payment, Product, Tpp, Tender,
                         Rate, Rating, Review, Service, Shipment, Gallery, Category, Country, Comment, Favorite,
                         Greeting, Exhibition, SystemMessages, Notification, Branch, NewsCategories, InnovationProject,
                         BusinessProposal, AdditionalPages, Messages, AdvBanner, AdvBannerType, AdvOrder, AdvTop,
                         topTypes,
                         staticPages, Requirement, BpCategories, UserSites, ExternalSiteTemplate, Resume, Vacancy,
                         PayPalPayment)
from core.models import Relationship, Value
from django.contrib import admin


class ParentRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "parent"
    raw_id_fields = ("create_user", 'child')


class ChildtRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "child"
    raw_id_fields = ("create_user", 'parent')


class ValuesInline(admin.TabularInline):
    model = Value
    extra = 5
    raw_id_fields = ("create_user", 'attr')


class AdditionalAdmin(admin.ModelAdmin):
    inlines = [ParentRelationshipInLIne, ChildtRelationshipInLIne, ValuesInline]
    raw_id_fields = ("create_user", 'update_user', 'community')


admin.site.register(AdditionalPages, AdditionalAdmin)
admin.site.register(AdvBanner, AdditionalAdmin)
admin.site.register(AdvBannerType, AdditionalAdmin)
admin.site.register(AdvOrder, AdditionalAdmin)
admin.site.register(AdvTop, AdditionalAdmin)
admin.site.register(Article, AdditionalAdmin)

admin.site.register(Basket, AdditionalAdmin)
admin.site.register(BusinessProposal, AdditionalAdmin)
admin.site.register(BpCategories, AdditionalAdmin)
admin.site.register(Branch, AdditionalAdmin)

admin.site.register(Category, AdditionalAdmin)
admin.site.register(Country, AdditionalAdmin)
admin.site.register(Comment, AdditionalAdmin)
admin.site.register(Company, AdditionalAdmin)
admin.site.register(Cabinet, AdditionalAdmin)

admin.site.register(Department, AdditionalAdmin)
admin.site.register(Document, AdditionalAdmin)

admin.site.register(Exhibition, AdditionalAdmin)
admin.site.register(ExternalSiteTemplate, AdditionalAdmin)

admin.site.register(Favorite, AdditionalAdmin)

admin.site.register(Gallery, AdditionalAdmin)
admin.site.register(Greeting, AdditionalAdmin)

admin.site.register(Invoice, AdditionalAdmin)
admin.site.register(InnovationProject, AdditionalAdmin)

admin.site.register(Messages, AdditionalAdmin)

admin.site.register(News, AdditionalAdmin)
admin.site.register(NewsCategories, AdditionalAdmin)
admin.site.register(Notification, AdditionalAdmin)

admin.site.register(Order, AdditionalAdmin)

admin.site.register(Payment, AdditionalAdmin)
admin.site.register(Product, AdditionalAdmin)

admin.site.register(topTypes, AdditionalAdmin)
admin.site.register(Tpp, AdditionalAdmin)
admin.site.register(Tender, AdditionalAdmin)

admin.site.register(Rate, AdditionalAdmin)
admin.site.register(Rating, AdditionalAdmin)
admin.site.register(Resume, AdditionalAdmin)
admin.site.register(Review, AdditionalAdmin)
admin.site.register(Requirement, AdditionalAdmin)

admin.site.register(Service, AdditionalAdmin)
admin.site.register(Shipment, AdditionalAdmin)
admin.site.register(staticPages, AdditionalAdmin)
admin.site.register(SystemMessages, AdditionalAdmin)

admin.site.register(Vacancy, AdditionalAdmin)

admin.site.register(UserSites, AdditionalAdmin)
admin.site.register(PayPalPayment, AdditionalAdmin)
