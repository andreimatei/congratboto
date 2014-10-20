#!/usr/bin/python

import argparse
import logging
import random
import sys

from adaptors import facebook_page
from adaptors import facebook_graph
from plugins.eliza import ElizaPlugin
from plugins.congratboto import CongratBoto
from plugins.score_keeper import ScoreKeeper

parser = argparse.ArgumentParser()
parser.add_argument('--access_token', required = True)
parser.add_argument('--bot_email', required = True)
parser.add_argument('--bot_pwd', required = True)
parser.add_argument('--log_dir', default='/tmp/congratboto-%s' % logs.timestamp_for_file())
FLAGS = parser.parse_args()

logger = logging.getLogger()

POLL_PERIOD_SEC = 30


def PollConversations(bot_user, all_plugins):
  try:
    logger.debug("Getting Inbox")
    conversations = bot_user.GetConversations()
    logger.debug("Found %d conversations" % len(conversations))
    for conversation in conversations.values():
      logger.debug("Processing thread thread_id=%s", conversation.Id())
      for plugin in all_plugins:
        plugin.HandleMessages(conversation)
  except Exception:
    logger.exception('Error while polling. Will continue polling.')

  # Schedule the next poll.
  # The wait time is somewhere between 0.9 and 1.1 of POLL_PERIOD_SEC.
  wait_time = (0.9 + 0.2 * random.random()) * POLL_PERIOD_SEC
  timer = threading.Timer(wait_time, lambda : PollConversations(bot_user, all_plugins))
  timer.daemon = True
  timer.start()


def main():
  logger.info('CongratBoto starting')
  write_session = facebook_page.FacebookSession('Turma Bot', FLAGS.bot_email, FLAGS.bot_pwd)
  auth_user = facebook_graph.AuthenticatedUser(FLAGS.access_token)
  all_plugins = [CongratBoto(write_session), ElizaPlugin(write_session), ScoreKeeper(write_session)]
  PollConversations(auth_user, all_plugins)
  
  while True:
    command = raw_input('Enter command: ')
    if command == 'quit':
      print 'Quitting!'
      return 0
    elif command == 'post':
      message = raw_input('Enter message: ')
      write_session.PostMessage(FLAGS.thread_id, message)
      logger.info('Posted: %s', message)


if __name__ == '__main__':
  sys.exit(main())
