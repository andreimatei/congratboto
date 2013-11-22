#!/usr/bin/python

import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re
import time
import threading
import urllib2
import urllib
import sys
import os
from cookielib import CookieJar
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin

import fbbot_utils


LOGIN_PERIOD_SEC = 29 * 60
FAILED_LOGIN_PERIOD_SEC = 1 * 60
POLL_PERIOD_SEC = 30

# PageProperties instance representing the last view of the thread page
view = None

def timestamp_for_file():
  return datetime.now().strftime('%y-%m-%d-%H:%M.%S')

parser = argparse.ArgumentParser()

parser.add_argument('--thread_id', required = True)
parser.add_argument('--bot_email', required = True)
parser.add_argument('--bot_pwd', required = True)

parser.add_argument('--log_file', default='/tmp/congratboto-%s/log' % timestamp_for_file())

flags = parser.parse_args()

thread_id = flags.thread_id
thread_id_encoded = urllib2.quote(thread_id)


def get_logs_dir():
  return os.path.dirname(flags.log_file)


cj = CookieJar()
fbbot_utils.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
fbbot_utils.opener.addheaders = [('User-agent', 'Mozilla/5.0')]


if not os.path.exists(get_logs_dir()):
  os.makedirs(get_logs_dir())

logging.basicConfig(level = logging.DEBUG,
                    datefmt='%m-%d %H:%M',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    filename=flags.log_file,
                    filemode='w')
logger = logging.getLogger('main')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

logger.warning("Logging to: %s", flags.log_file)

def login():
  login_period = FAILED_LOGIN_PERIOD_SEC
  logger.debug('Logging in...');
  # Clear the cookies, to get a new server-side session.
  # I don't know if this is necessary, but without it we've seen the bot get a page with an error
  # instead of the successful login page after several hours of functioning.
  # TODO(burbelica): add a lock protecting the cookies. Polling races with login().
  cj.clear()

  try:
    # curl -X POST 'https://m.facebook.com/login.php' --verbose --user-agent $USER_AGENT --data-urlencode "email=${EMAIL}" --data-urlencode "pass=${PASS}" --cookie $COOKIES --cookie-jar $COOKIES > /dev/null
    formdata = { "email" : flags.bot_email, "pass": flags.bot_pwd }
    data_encoded = urllib.urlencode(formdata)
    response = fbbot_utils.opener.open("https://m.facebook.com/login.php", data_encoded)
    html_doc = response.read()
    soup = BeautifulSoup(html_doc)
    if fbbot_utils.BOT_NAME in soup.get_text():
      login_period = LOGIN_PERIOD_SEC
      logger.debug('Login successful.')
    else:
      filename = os.path.join(get_logs_dir(),
                            'login-error-%s.html' % timestamp_for_file())
      out = open(filename, 'w')
      out.write(html_doc)
      out.close()
      logger.error("Login seems unsuccessful. "
                   "A copy of the retrieved page was saved at: %s" % filename)
  except Exception:
    logger.exception('Error logging in. Will retry.')

  # Schedule another login later, to refresh the cookies.
  timer = threading.Timer(login_period, login)
  timer.daemon = True
  timer.start()


def read_thread():
  # curl -X GET 'https://m.facebook.com/messages/read/?tid=mid.1384722860563%3A3932eedf826bf6c982' --verbose --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES > out.html
  response = fbbot_utils.opener.open("https://m.facebook.com/messages/read/?tid=%s" % thread_id_encoded)
  content = response.read()
  return content


class PageProperties:
  def __init__(self):
    self.csrf_token = None
    self.lowest_message_id = None
    self.page_size = None
    self.message_groups = []

def has_sigil(tag):
  return tag.has_attr('data-sigil') and tag['data-sigil'] == 'message-text'

def parse_page(html_doc):
  try:
    soup = BeautifulSoup(html_doc)
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
      msg_group = fbbot_utils.MessageGroup()
      prop.message_groups.append(msg_group)
      anchor = group.select('a.actor-link')
      msg_group.author = group.strong.get_text()
      message_tags = group.find_all(has_sigil)
      logger.debug('Author: %s. Found %d messages.' % (msg_group.author, len(message_tags)))
      for x in message_tags:
        msg_group.messages.append(x.span.get_text())
    return prop

  except Exception:
    filename = os.path.join(get_logs_dir(),
                           'thread-error-%s.html' % timestamp_for_file())
    out = open(filename, 'w')
    out.write(html_doc)
    out.close()
    logger.exception("Error parsing thread page."
                     "A copy of the retrieved page was saved at: %s" % filename)
    return None

def write_checkpoint(latest_message_id):
  out = open('checkpoint', 'w')
  out.write(latest_message_id)
  out.close()

def read_checkpoint():
  f = open('checkpoint', 'r')
  latest = int(f.read)
  f.close()
  return latest

def poll():
  global view
  try:
    page = read_thread()
    view = parse_page(page)

    if view:
      fbbot_utils.csrf_token = view.csrf_token
      for pluginInfo in simplePluginManager.getAllPlugins():
        pluginInfo.plugin_object.handle_messages(thread_id, view.message_groups)
  except Exception:
    logger.exception('Error while polling. Will continue polling.')

  # Schedule the next poll.
  timer = threading.Timer(POLL_PERIOD_SEC, poll)
  timer.daemon = True
  timer.start()

simplePluginManager = PluginManager()
cur_dir = os.path.dirname(__file__)
simplePluginManager.setPluginPlaces([os.path.join(cur_dir, 'plugins')])
# Load all plugins
simplePluginManager.collectPlugins()
for pluginInfo in simplePluginManager.getAllPlugins():
  simplePluginManager.activatePluginByName(pluginInfo.name)
  logger.info('Plugin detected: %s', pluginInfo.plugin_object.get_name())

logger.info('CongratBoto starting. Watching thread: %s', thread_id)
login()
poll()

#message = 'Turma Bot is in the house at %s' % datetime.datetime.now()
# post_message(message, view.csrf_token)

while True:
  command = raw_input('Enter command: ')
  if command == 'quit':
    print 'Quitting!'
    sys.exit(0)
  elif command == 'post':
    message = raw_input('Enter message: ')
    fbbot_utils.post_message(thread_id, message)
