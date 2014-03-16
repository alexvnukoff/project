from django.core.management.base import NoArgsCommand
from core.models import User, Relationship
from appl.models import AdditionalPages, Company
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload Company Additional Pages from buffer DB table LEGACY_DATA_L_PAGES2COMP into TPP DB
        '''
        time1 = datetime.datetime.now()
        print('Loading Company additional pages from buffer DB into TPP DB...')
        qty = L_Pages2Comp.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        i = 0
        pgs_lst = L_Pages2Comp.objects.filter(completed=False).all()
        create_usr = User.objects.get(pk=1)
        for leg_pgs in pgs_lst:
            try:
                leg_comp = L_Company.objects.get(btx_id=leg_pgs.btx_id)
                comp = Company.objects.get(pk=leg_comp.tpp_id)
            except:
                print('Could not find Company for this Additional Page. Company btx_id:', leg_pgs.btx_id)
                i += 1
                continue

            try:
                page = AdditionalPages.objects.create(title='ADD_PAGE_COMPANY_ID:'+str(comp.pk), create_user=create_usr)
            except:
                print(leg_pgs.btx_id, '##', leg_pgs.page_name, '##', ' Count: ', i)
                i += 1
                continue

            attr = {
                    'NAME': leg_pgs.page_name,
                    'DETAIL_TEXT': leg_pgs.page_text,
                    }

            trans_real.activate('ru') #activate russian locale
            res = page.setAttributeValue(attr, create_usr)
            trans_real.deactivate() #deactivate russian locale
            if res:
                leg_pgs.completed = True
                leg_pgs.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # create relationship type=Dependence with business entity
            try:
                Relationship.objects.create(parent=comp, type='dependence', child=page, create_user=create_usr)
            except:
                print('Can not create relationship for additional page. Page will delete.')
                page.delete()
                i += 1
                continue

            i += 1
            print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Company additional pages were migrated from buffer DB into TPP DB!')
