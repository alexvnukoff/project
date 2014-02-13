#!/usr/bin/python
import getopt
import sys
import gdata.analytics.client
from gdata.sample_util import CLIENT_LOGIN, SettingsUtil

gdata_client = gdata.analytics.client.AnalyticsClient(source='ExpertCenter')
  
def _login():  
      
    settings_util = SettingsUtil(prefs={  
        "email": 'artur@tppcenter.com',
        "password": 'qwe123321',
    })  
    settings_util.authorize_client(  
        gdata_client,  
        service=gdata_client.auth_service,  
        auth_type=CLIENT_LOGIN,  
        source='ExpertCenter',
        scopes=['https://www.google.com/analytics/feeds/']  
        )  
          
def get_views(filter):
      
    _login()          
    data_query = gdata.analytics.client.DataFeedQuery({  
        'ids': 'ga:75260634',
        'start-date': '2013-01-01',
        'end-date': '2050-01-01',
        'metrics': 'ga:visitors',
        'filters': str(filter),
        'max-results': "10000"  
        })  
          
    return gdata_client.GetDataFeed(data_query)

def main():
  """Demonstrates use of the Docs extension using the DocsSample object."""
  # Parse command line options

  print get_views(sys.argv[1])

  #print(feed.entries[0]['ns1_metric']['value'])



if __name__ == '__main__':
  main()


