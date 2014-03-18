from django.core.management.base import NoArgsCommand
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            For users which were reloaded from prepared CSV file named users_legacy.csv
            send e-mail with url for password change notification.
        '''
        time1 = datetime.datetime.now()
        # Move users from buffer table into original tables
        print('Sending notifications to users about password changing.')
        qty = L_User.objects.filter(completed=True, email_sent=True).count()
        print('Already was sent: ', qty)
        user_list = L_User.objects.filter(completed=True, email_sent=False).all()
        if len(user_list):
            for usr in user_list:
                form = PasswordResetForm({'email': usr.email})
                form.is_valid()
                form.save(from_email=settings.DEFAULT_FROM_EMAIL, email_template_name='legacy_data/password_reset_email.html')
                usr.email_sent = True
                usr.save()
        else:
            print('Nothing to send!')

        print('Done. Notifications to users were sent!')
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)

        print('Migrated users were notified by e-mail!')
