import cookielib
import datetime
import logging
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

  def GetCsrfToken(self, thread_id):
    try:
      logging.debug("FacebookSession.GetCsrfToken(%s)", thread_id)
      # curl -X GET 'https://m.facebook.com/messages/read/?tid=mid.1384722860563%3A3932eedf826bf6c982' --verbose --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES > out.html
      response = self._GetOpener().open("https://m.facebook.com/messages/read/?tid=%s" % urllib2.quote(thread_id))
      return ExtractCsrfTokenFromThreadPage(response.read())
    except Exception as e:
      raise Exception("GetCsrfToken() failed", e)

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
        self.csrf_token = self.GetCsrfToken(thread_id)
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


def ExtractCsrfTokenFromThreadPage(html_doc):
  try:
    soup = bs4.BeautifulSoup(html_doc)
    return soup.select('input[name="fb_dtsg"]')[0]['value']
  except Exception as e:
    logger.debug(html_doc)
    raise e

      