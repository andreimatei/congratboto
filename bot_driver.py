#!/usr/bin/python

import argparse
import logging
import os
import sys

from bot_driver_util import *
import facebook
import facebook_graph
import logs
from plugins.eliza_plugin import ElizaPlugin
from plugins.congratboto import CongratBoto

parser = argparse.ArgumentParser()
parser.add_argument('--access_token', required = True)
parser.add_argument('--bot_email', required = True)
parser.add_argument('--bot_pwd', required = True)
parser.add_argument('--log_dir', default='/tmp/congratboto-%s' % logs.timestamp_for_file())
FLAGS = parser.parse_args()

logger = logs.CreateLogger(logging.DEBUG, os.path.join(FLAGS.log_dir, "log"))

def main():
  logger.info('CongratBoto starting')
  write_session = facebook.FacebookSession('Turma Bot', FLAGS.bot_email, FLAGS.bot_pwd)
  read_session = facebook_graph.FacebookGraphSession(FLAGS.access_token)
  all_plugins = [CongratBoto(write_session), ElizaPlugin(write_session)]
  PollConversation(read_session, all_plugins, true)
  
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
