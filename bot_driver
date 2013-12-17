#!/usr/bin/python

import argparse
import logging
import random
import os
import sys
import threading

import facebook
import logs
from plugins.congratboto import CongratBoto

POLL_PERIOD_SEC = 30

parser = argparse.ArgumentParser()
parser.add_argument('--thread_id', required = True)
parser.add_argument('--bot_email', required = True)
parser.add_argument('--bot_pwd', required = True)
parser.add_argument('--log_dir', default='/tmp/congratboto-%s' % logs.timestamp_for_file())
FLAGS = parser.parse_args()

logger = logs.CreateLogger(logging.DEBUG, os.path.join(FLAGS.log_dir, "log"))


def PollConversation(session, thread_id, all_plugins):
  try:
    view = session.GetConversationThread(thread_id)
    if view:
      for plugin in all_plugins:
        plugin.HandleMessages(thread_id, view.message_groups)
  except Exception:
    logger.exception('Error while polling. Will continue polling.')

  # Schedule the next poll.
  # The wait time is somewhere between 0.9 and 1.1 of POLL_PERIOD_SEC.
  wait_time = (0.9 + 0.2 * random.random()) * POLL_PERIOD_SEC
  timer = threading.Timer(wait_time, lambda : PollConversation(session, thread_id, all_plugins))
  timer.daemon = True
  timer.start()


def main():
  logger.info('CongratBoto starting')
  session = facebook.FacebookSession('Turma Bot', FLAGS.bot_email, FLAGS.bot_pwd)
  all_plugins = [CongratBoto(session)]
  PollConversation(session, FLAGS.thread_id, all_plugins)
  
  while True:
    command = raw_input('Enter command: ')
    if command == 'quit':
      print 'Quitting!'
      return 0
    elif command == 'post':
      message = raw_input('Enter message: ')
      session.PostMessage(FLAGS.thread_id, message)
      logger.info('Posted: %s', message)


if __name__ == '__main__':
  sys.exit(main())
