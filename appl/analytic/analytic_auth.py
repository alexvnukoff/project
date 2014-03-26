#!/usr/bin/python

import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import os

path = os.path.dirname(__file__).replace('\\', '/')

CLIENT_SECRETS = path + '/client_secret.json'
MISSING_CLIENT_SECRETS_MESSAGE = '%s is missing' % CLIENT_SECRETS

FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
  scope='https://www.googleapis.com/auth/analytics.readonly',
  message=MISSING_CLIENT_SECRETS_MESSAGE)

TOKEN_FILE_NAME = path + '/analytics.dat'

def prepare_credentials():
  storage = Storage(TOKEN_FILE_NAME)
  credentials = storage.get()

  return credentials

def initialize_service():
  http = httplib2.Http()

  #Get stored credentials or run the Auth Flow if none are found
  credentials = prepare_credentials()
  http = credentials.authorize(http)

  #Construct and return the authorized Analytics Service Object
  return build('analytics', 'v3', http=http)