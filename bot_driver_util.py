import logging
import random
import threading

logger = logging.getLogger()

POLL_PERIOD_SEC = 30

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


def PollConversation(read_session, all_plugins, periodic):
  try:
    logger.debug("Getting Inbox")
    inbox = read_session.GetInbox()
    logger.debug("Found %d conversations" % len(inbox.conversations))
    for conversation in inbox.conversations.values():
      if not conversation.messages: continue
      # TODO(fortuna): Make this work for all threads. I can't figure out a way of mapping the
      # conversation.cid to the id the write_session needs, or how to post using the graph API.
      # Apparently there's no API to send messages from an app:
      # https://developers.facebook.com/docs/reference/dialogs/send/
      if len(conversation.members) > 2:
        # for group chats, you get the thread id by prepending "id."
        thread_id = "id.%s" % conversation.cid
      else:
        thread_id = READ_TO_WRITE_MAP.get(conversation.cid)
      if not thread_id: continue
      logger.debug("Processing thread cid=%s, thread_id=%s", conversation.cid, thread_id)
      for plugin in all_plugins:
        plugin.HandleMessages(thread_id, conversation)
  except Exception:
    logger.exception('Error while polling. Will continue polling.')

  if periodic:
    # Schedule the next poll.
    # The wait time is somewhere between 0.9 and 1.1 of POLL_PERIOD_SEC.
    wait_time = (0.9 + 0.2 * random.random()) * POLL_PERIOD_SEC
    timer = threading.Timer(wait_time, lambda : PollConversation(read_session, all_plugins))
    timer.daemon = True
    timer.start()