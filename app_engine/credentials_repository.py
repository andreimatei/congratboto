'''
Credentials Database model
'''

from collections import namedtuple

from google.appengine.ext import ndb

Credentials = namedtuple('Credentials', ['email', 'password', 'access_token'])


class _DbCredentials(ndb.Model):
  @classmethod
  def _get_kind(cls):
    return 'Credentials'
  email = ndb.StringProperty(indexed=False)
  password = ndb.StringProperty(indexed=False)
  access_token = ndb.StringProperty(indexed=False)


def _CredentialsKey():
  return ndb.Key(_DbCredentials, 'bot_user')


def GetCredentials():
  credentials = _CredentialsKey().get()
  if credentials is None:
    raise "No Facebook credentials found. Please go to /credentials to set them."
  return Credentials(email=credentials.email, password=credentials.password,
                     access_token=credentials.access_token)


def UpdateCredentials(email, password, access_token):
  credentials = _DbCredentials.get_or_insert(
      _CredentialsKey().string_id())
  if email: credentials.email = email
  if password: credentials.password = password
  if access_token: credentials.access_token = access_token
  credentials.put()
  return Credentials(email=credentials.email, password=credentials.password,
                     access_token=credentials.access_token)
