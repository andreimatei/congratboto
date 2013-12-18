#!/usr/bin/python

import argparse
import logging
import random
import os
import sys
import threading

import facebook
import facebook_graph
import logs
from plugins.eliza_plugin import ElizaPlugin
from plugins.congratboto import CongratBoto

POLL_PERIOD_SEC = 30

parser = argparse.ArgumentParser()
parser.add_argument('--access_token', required = True)
parser.add_argument('--bot_email', required = True)
parser.add_argument('--bot_pwd', required = True)
parser.add_argument('--log_dir', default='/tmp/congratboto-%s' % logs.timestamp_for_file())
FLAGS = parser.parse_args()

logger = logs.CreateLogger(logging.DEBUG, os.path.join(FLAGS.log_dir, "log"))

# This map knows how to go from the Graph conversation id, to the scrape id for posting.
READ_TO_WRITE_MAP = {
   # Turma                  
  "669740653053963": "id.669740653053963",
  # Vini
  "387408068058873": "mid.1384790752857:7f74c5cd85790a7b22",
  # Andrei
  "1422830054600298": "mid.1384722860563:3932eedf826bf6c982",
  # Temp Turma
  "620590488002789": "id.566416863439275",
  # Lorena
  "1378876915695040": "mid.1386221476449:ecba88a4313984db59"
}

def PollConversation(read_session, all_plugins):
  try:
    logging.debug("Getting Inbox")
    inbox = read_session.GetInbox()
    logging.debug("Found %d conversations" % len(inbox.conversations))
    for conversation in inbox.conversations.values():
      if not conversation.messages: continue
      # TODO(fortuna): Make this work for all threads. I can't figure out a way of mapping the
      # conversation.cid to the id the write_session needs, or how to post using the graph API.
      # Apparently there's no API to send messages from an app:
      # https://developers.facebook.com/docs/reference/dialogs/send/
      thread_id = READ_TO_WRITE_MAP.get(conversation.cid)
      if not thread_id: continue
      logging.debug("Processing thread cid=%s, thread_id=%s", conversation.cid, thread_id)
      for plugin in all_plugins:
        plugin.HandleMessages(thread_id, conversation)
  except Exception:
    logger.exception('Error while polling. Will continue polling.')

  # Schedule the next poll.
  # The wait time is somewhere between 0.9 and 1.1 of POLL_PERIOD_SEC.
  wait_time = (0.9 + 0.2 * random.random()) * POLL_PERIOD_SEC
  timer = threading.Timer(wait_time, lambda : PollConversation(read_session, all_plugins))
  timer.daemon = True
  timer.start()


def main():
  logger.info('CongratBoto starting')
  write_session = facebook.FacebookSession('Turma Bot', FLAGS.bot_email, FLAGS.bot_pwd)
  read_session = facebook_graph.FacebookGraphSession(FLAGS.access_token)
  all_plugins = [CongratBoto(write_session), ElizaPlugin(write_session)]
  PollConversation(read_session, all_plugins)
  
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
