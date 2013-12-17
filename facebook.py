import cookielib
import datetime
import logging
import re
import urllib
import urllib2

import bs4

logger = logging.getLogger()


OPENER_TTS_SEC = 29 * 60

class FacebookSession(object):
  def __init__(self, user_name, user_email, user_password):
    # User information for login. The name is only used to validate the login page.
    # TODO(fortuna): Don't require name and use the email instead.
    self.user_name = user_name
    self.user_email = user_email
    self.user_password = user_password
    # Used for posting messages. Extracted from the thread page.
    self.csrf_token = None
    # Used to fetch pages from the Facebook site.
    self.opener = None
    # When the opener was created. It expires after some time.
    self.opener_timestamp = None

  def _GetOpener(self):
    logger.debug("FacebookSession._GetOpener()")
    try:
      current_time = datetime.datetime.now()
      if (not self.opener or
          current_time > self.opener_timestamp + datetime.timedelta(seconds=OPENER_TTS_SEC)):
        self.opener = CreateFacebookOpener(self.user_name, self.user_email, self.user_password)
        self.opener_timestamp = current_time
        self.csrf_token = None
      return self.opener
    except Exception as e:
      raise Exception("FacebookSession._GetOpener() failed", e)

  def GetConversationThread(self, thread_id):
    try:
      logging.debug("FacebookSession.GetConversationThread(%s)", thread_id)
      # curl -X GET 'https://m.facebook.com/messages/read/?tid=mid.1384722860563%3A3932eedf826bf6c982' --verbose --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES > out.html
      response = self._GetOpener().open("https://m.facebook.com/messages/read/?tid=%s" % urllib2.quote(thread_id))
      parsed_page = ParseThreadPage(response.read())
      self.csrf_token = parsed_page.csrf_token
      return parsed_page
    except Exception as e:
      raise Exception("GetConversationThread() failed", e)

  def PostMessage(self, thread_id, message):
    """
      curl \
      -F 'fb_dtsg=AQBRa6P3' \
      -F 'body=cel' \
      -F 'tids=mid.1384722860563:3932eedf826bf6c982' \
      -X POST 'https://m.facebook.com//messages/send/?icm=1&refid=12' --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES --location
    """
    try:
      if not self.csrf_token:
        self.GetConversationThread(thread_id)
      formdata = { 'fb_dtsg' : self.csrf_token, 'body' : message, 'tids' : thread_id }
      data_encoded = urllib.urlencode(formdata)
      # TODO(fortuna): Check the response to confirm the post.
      self._GetOpener().open("https://m.facebook.com//messages/send/?icm=1&refid=12", data_encoded)
    except Exception as e:
      raise Exception("PostMessage failed", e) 


def CreateFacebookOpener(user_name, user_email, user_password):
  logger.debug("CreateFacebookOpener(%s, %s, ..)", user_name, user_email)
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]

  # curl -X POST 'https://m.facebook.com/login.php' --verbose --user-agent $USER_AGENT --data-urlencode "email=${EMAIL}" --data-urlencode "pass=${PASS}" --cookie $COOKIES --cookie-jar $COOKIES > /dev/null
  formdata = {"email" : user_email, "pass": user_password}
  data_encoded = urllib.urlencode(formdata)
  response = opener.open("https://m.facebook.com/login.php", data_encoded)
  html_doc = response.read()
  soup = bs4.BeautifulSoup(html_doc)
  if user_name in soup.get_text():
    return opener
  else:
    logger.debug(html_doc)
    raise Exception("Did not find user %s on output page" % user_name)


class MessageGroup:
  def __init__(self):
    self.author = None
    self.messages = []

class PageProperties:
  def __init__(self):
    self.csrf_token = None
    self.lowest_message_id = None
    self.page_size = None
    self.message_groups = []

def has_sigil(tag):
  return tag.has_attr('data-sigil') and tag['data-sigil'] == 'message-text'

def ParseThreadPage(html_doc):
  try:
    soup = bs4.BeautifulSoup(html_doc)
    tag = soup.select('#messages_read_view_form')
    if not tag:
      if "You must log in first" in soup.get_text():
        logger.error("Error fetching thread. Login expired.")
      else:
        raise Exception("Did not find a match for #messages_read_view_form.")
      return None

    prop = PageProperties()
    # look for the form
    r = re.compile('.*start=(\d*).*page_size=(\d*).*')
    match = r.match(tag[0]['action'])
    if not match:
      raise Exception("Did not find the form.")
      return None
    prop.lowest_message_id = int(match.group(1))
    prop.page_size = int(match.group(2))
    csrf_input = soup.select('input[name="fb_dtsg"]')
    prop.csrf_token = csrf_input[0]['value']
    logger.debug("Found lowest id: %d and page size: %d. CSRF token: %s"
                % (prop.lowest_message_id, prop.page_size, prop.csrf_token))

    # read the messages
    groups = soup.select('div.msg')
    for group in groups:
      msg_group = MessageGroup()
      prop.message_groups.append(msg_group)
      msg_group.author = group.strong.get_text()
      message_tags = group.find_all(has_sigil)
      for x in message_tags:
        msg_group.messages.append(x.span.get_text())
      logger.debug('Author: %s. Found %d messages.' % (msg_group.author, len(msg_group.messages)))
    return prop

  except Exception as e:
    logger.debug(html_doc)
    raise e

      