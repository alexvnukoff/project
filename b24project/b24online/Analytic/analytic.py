from googleapiclient.discovery import build
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials


def initialize_service():
    json_data = {
      "private_key_id": "660eba9c05c95cb0b4841715c420710180e3a5b4",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDYo4ajdHzyYCyS\nOaKirPcb2binJR0CuvBbHjukq1u4oZeA0qVW0yI0mbT8dCaOrFHeZimaBN6Ei+4J\n5X869HZnW9Q4aM0brcyPFNuTJq522W2ZeF4A6oReITPkBAGveiqrw9h/sQUFH8Pi\n/+ow0+6KhR9AXcHJB0VVerAKqFNBPDPPUsg2OSXLXixckdLOVYhxGrXNkgsvB0KD\no7SasuQH2LoV/3YKu+kv/ybCCgz5TjfZoWsf/5slO85oQLFe0AM92KmxCGyEonxH\n3Lp1+nPL7fNfXc/qXWZcfMSakTfpYndk2ZW6NV+LY67I4NlW6LH2aeY2m8Vhwcjv\nQAwH7BSLAgMBAAECggEBAMCRQynibvpHsPbd0opFs3YHJ1Mz80CtCOAF1MCALYzF\n3tT86UlvbdVR2AYb/PYPiMpnB43HzEAH3jTf0iOGkAU6JD9sMP3slIuO38tCtAwj\nI4Aq9WxdCgJeAzEoupLPxkReVwDSSoMOhGIwV2zFxiFNScU+UfYux1u/LeKbUz4E\n8dvgk13ZNAtczSDjp/BfTOSgxiOj57dgT1ZFXqddFbM7tH9RuL87QnBaQOaYiib/\nCrL7KGBjWuG8jWMdfdakyF0bb5YtJ/1aM26UjmFxNxu4h1xRdiC7EezD9Rg+FmN+\nSW2ysjdcR+g5ma6Oy8XpnP8FDl4U2F2y8aOmdx7ZQnECgYEA7ei4KRY/YGf7QNok\nkKcwOMBEydXyBb0gow35h0OXR4UOsO10mVkYpmANQhIkHa4UpLuSx5WpAracBYLk\nmPMzN32EyWuLiRggSWT6e78hwG+ggAtIUuhBQAox04LFEyUZe4PgErkxHejNLrUb\ntABtgHXwjd14iQ6MOIP6X9bFiYkCgYEA6Ry/Epnalp2I5RPMAQW2KAWtQZ49xuEs\nVotCrudXCZxu/gXNnAQpWLmOcN32qCUdfI5byn/XTvBFunCIgZIZ1zDJl5asJnNV\nFgh6gTze8nhIo2DXhRfdukwY2GvoJrYABddVJ4mD+wXClygDagCzDUniuQ1nAVcM\nc83Tl9b97HMCgYBT/LQGzTPSdOLeIiSGbH85iaa/Gig2nm3HIkfU2KevN+nXy/w9\nppZtJbuId58IW0wuW4mVq9/edVjfGTZaSIDsNgOKl8zKuRmsz1keFntz0/R1P4Zo\nvlVKpk6wvJmWCKLWV9fixD3ysRy+QHFnOj9t+jTR4D2NJPWbffwFmWxjAQKBgBmd\nF/2SPCtqed051KOUHhS9svDP01fj6/xCZvxS3QRoVOXCe3oWFvjxwo3yRaTqFxhV\niA5zB5Rb4D2BGe6qv/4eFTh7zMSYzZOTMOq8Zn7b6pdRD71HBwzuSZiWGrcOLmh1\n5ZxnhsHxOxVixyVBmGrwYGIW7+d8yhh7WDGJ5PKzAoGAb4HepnuP0LRuDwhsgPZW\nNaBgySlzr9Vjr4FM3mjfWqMzPckoed81cffD1EWezliF1haJBh2sxvTAEvExEERy\nScIw83QRzSDAqc2lmhrd+qAIvzfZtEIS81Vvyr3xuwCwTRTgxKTp2KIhBZOso1ce\nEPwHcJywVKN3Pc5iRecKY6E\u003d\n-----END PRIVATE KEY-----\n",
      "client_email": "533813316318-b9qv4pjvkcagf438kaifkpmn17m149kd@developer.gserviceaccount.com",
      "client_id": "533813316318-b9qv4pjvkcagf438kaifkpmn17m149kd.apps.googleusercontent.com",
      "type": "service_account"
    }

    credentials = SignedJwtAssertionCredentials(json_data['client_email'], json_data['private_key'],
                                                'https://www.googleapis.com/auth/analytics.readonly')
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
