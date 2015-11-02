from googleapiclient.discovery import build
import httplib2
from oauth2client.client import GoogleCredentials


def initialize_service():
    credentials = GoogleCredentials.get_application_default()
    credentials = credentials.create_scoped('https://www.googleapis.com/auth/analytics.readonly')
    http_auth = credentials.authorize(httplib2.Http())

    # Construct and return the authorized Analytics Service Object
    return build('analytics', 'v3', http=http_auth)


def get_first_profile_id(service):
    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account
        firstAccountId = accounts.get('items')[0].get('id')

        # Get a list of all the Web Properties for the first account
        webproperties = service.management().webproperties().list(accountId=firstAccountId).execute()

        if webproperties.get('items'):
            # Get the first Web Property ID
            firstWebpropertyId = webproperties.get('items')[0].get('id')

            # Get a list of all Views (Profiles) for the first Web Property of the first Account
            profiles = service.management().profiles().list(
                accountId=firstAccountId,
                webPropertyId=firstWebpropertyId).execute()

            if profiles.get('items'):
                # return the first View (Profile) ID
                return profiles.get('items')[0].get('id')

    return None


def get_results(**kwargs):
    service = initialize_service()
    profile_id = get_first_profile_id(service)
    # Use the Analytics Service Object to query the Core Reporting API
    try:
        results = service.data().ga().get(ids='ga:' + profile_id, **kwargs).execute()
    except:
        return None

    return results.get('rows')
