from third_party import eliza
import logging

logger = logging.getLogger('eliza_plugin')


class ElizaPlugin(object):
  def __init__(self):
    self.therapist = eliza.eliza()

  def HandleMessages(self, conversation, new_messages):
    if len(conversation.Members()) > 2: return
    last_message = new_messages[-1]
    if not last_message.text:
      # This happens if the message is special, like an emoticon.
      return
    conversation.PostMessage(self.therapist.respond(last_message.text))
