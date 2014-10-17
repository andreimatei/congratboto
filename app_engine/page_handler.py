import sys
sys.path.insert(0, 'libs')

import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import bot_driver_util
import facebook
import facebook_graph
from plugins.eliza_plugin import ElizaPlugin
from plugins.congratboto import CongratBoto
from plugins.score_keeper_plugin import ScoreKeeper


logger = logging.getLogger('page_handler')

class MainPage(webapp.RequestHandler):
  def get(self):
    pass
 
class PollPage(webapp.RequestHandler):
  def get(self):
    bot_email = self.request.get('bot_email')
    bot_pwd = self.request.get('bot_pwd')
    access_token = self.request.get('access_token')
    logger.info('Request: bot email: %s password: %s access_token: %s' % (bot_email, bot_pwd, access_token))

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Running Congratboto')

    write_session = facebook.FacebookSession('Turma Bot', bot_email, bot_pwd)
    boto_user = facebook_graph.AuthenticatedUser(write_session, access_token)
    all_plugins = [CongratBoto(), ElizaPlugin(), ScoreKeeper()]
    bot_driver_util.PollConversations(boto_user, all_plugins, False)


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
