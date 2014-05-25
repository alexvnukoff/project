from django.core.management.base import NoArgsCommand
from appl.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Clear all generated data in DB for ORG community migration process debugging
        '''
        print('Starting...')

        models = [Product, Department, Order, Country, Company, Tpp, TppTV, Branch, AdvOrder, Requirement, AdvTop,
                  AdvBannerType, AdvBanner, NewsCategories, UserSites, InnovationProject, BusinessProposal, Comment,
                   SystemMessages, ExternalSiteTemplate, Notification, Category, License, Greeting, Gallery, Service,
                   Favorite, Invoice, News, Resume, Article, Review, Rate, Rating, Payment, Shipment, Tender, Basket,
                   Cabinet, Document, AdditionalPages, Exhibition, Messages, Vacancy]
        try:
            for model in models:

                if model.objects.all().count() == 0:
                    print("Pass " + model.__name__)
                    continue

                for item in model.objects.filter(contentType__isnull=True):
                    item.save()

                    print(item.__class__.__name__ + ": " + str(item.pk))

            print('The End!')
        except:
            print('Except ' + model.__name__)
