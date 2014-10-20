import logging
import random
import threading

logger = logging.getLogger()

POLL_PERIOD_SEC = 30


def PollConversations(bot_user, all_plugins, periodic):
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

  if periodic:
    # Schedule the next poll.
    # The wait time is somewhere between 0.9 and 1.1 of POLL_PERIOD_SEC.
    wait_time = (0.9 + 0.2 * random.random()) * POLL_PERIOD_SEC
    timer = threading.Timer(wait_time, lambda : PollConversations(bot_user, all_plugins))
    timer.daemon = True
    timer.start()