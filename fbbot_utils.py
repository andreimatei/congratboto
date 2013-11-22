import logging
import urllib2
import urllib
from yapsy.IPlugin import IPlugin

BOT_NAME = 'Turma Bot'

logger = logging.getLogger('fbbot_utils')

csrf_token = None
opener = None  # urllib opener configured with correct cookies

def post_message(thread_id, message):
  """
  curl \
  -F 'fb_dtsg=AQBRa6P3' \
  -F 'body=cel' \
  -F 'tids=mid.1384722860563:3932eedf826bf6c982' \
  -X POST 'https://m.facebook.com//messages/send/?icm=1&refid=12' --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES --location
  """
  formdata = { 'fb_dtsg' : csrf_token, 'body' : message, 'tids' : thread_id }
  data_encoded = urllib.urlencode(formdata)
  response = opener.open("https://m.facebook.com//messages/send/?icm=1&refid=12", data_encoded)

  logger.info('Posted: %s', message)


class MessageGroup:
  def __init__(self):
    self.author = None
    self.messages = []

class BotoPlugin(IPlugin):
  def get_name(self):
    return 'unnnamed. this should be overriden'

  # takes an iterable of MessageGroup
  def handle_messages(self, thread_id, groups):
    pass