import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import credentials_repository
import db_score_table
from adaptors import facebook_page
from adaptors import facebook_graph
from plugins.eliza import ElizaPlugin
from plugins.congratboto import CongratBoto
from plugins.score_keeper import ScoreKeeper
from plugins.answers import AnswersPlugin

logger = logging.getLogger('page_handler')

class MainPage(webapp.RequestHandler):
  def get(self):
    pass


# The identifier of the Bot user on Facebook.
BOT_ID = '100007101244912'
BOT_NAME = 'Turma Bot'

class PollPage(webapp.RequestHandler):
  def get(self):
    credentials = credentials_repository.GetCredentials()
    logger.info('Request: bot email: %s password: %s access_token: %s' % (
        credentials.email, credentials.password, credentials.access_token))

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Running Congratboto')

    write_session = facebook_page.FacebookSession(BOT_NAME, credentials.email, credentials.password)
    boto_user = facebook_graph.AuthenticatedUser(write_session, credentials.access_token)
    all_plugins = [CongratBoto(), ElizaPlugin(), ScoreKeeper(db_score_table.DbScoreTable()),
                   AnswersPlugin()]
    try:
      logger.debug("Getting Inbox")
      conversations = boto_user.GetConversations()
      logger.debug("Found %d conversations" % len(conversations))
      for conversation in conversations.values():
        logger.debug("Processing thread thread_id=%s", conversation.Id())
        new_messages = []
        for message in conversation.Messages():
          if message.user and message.user.uid == BOT_ID:
            new_messages = []
          else:
            new_messages.append(message)
        if not new_messages:
          continue
        for plugin in all_plugins:
          plugin.HandleMessages(conversation, new_messages)
    except Exception:
      logger.exception('Error while polling')



def main():
  application = webapp.WSGIApplication([('/', MainPage), ('/poll.html', PollPage)], debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  #set the format on the root logger
  if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
    log_format = '[%(asctime)s %(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
  else:
    log_format = '[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
  fmt = logging.Formatter(log_format)
  logging.getLogger().handlers[0].setFormatter(fmt)
  logger.info('CongratBoto starting')
  main()
