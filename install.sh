#!/bin/bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic
python3 manage.py compilemessages
python3 manage.py loaddata fixtures/b2b_categories.json
python3 manage.py loaddata fixtures/b2c_categories.json
python3 manage.py loaddata fixtures/baner_block.json
python3 manage.py loaddata fixtures/branch.json
python3 manage.py loaddata fixtures/business_proposal_category.json
python3 manage.py loaddata fixtures/countries.json
python3 manage.py loaddata fixtures/external_site_template.json
python3 manage.py loaddata fixtures/greetings.json
python3 manage.py loaddata fixtures/news_categories.json
python3 manage.py loaddata fixtures/PermissionsExtraGroup.json
python3 manage.py loaddata fixtures/RegisteredEventType.json
python3 manage.py loaddata fixtures/StaffGroup.json
python3 manage.py loaddata fixtures/static_pages.json
python3 manage.py loaddata fixtures/user_site_scheme_color.json
python3 manage.py loaddata fixtures/user_site_template.json