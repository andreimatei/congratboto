from third_party import eliza
import logging

logger = logging.getLogger('eliza_plugin')

BOT_ID = "100007101244912"

class ElizaPlugin(object):
  def __init__(self):
    self.therapist = eliza.eliza()

  def HandleMessages(self, conversation):
    if len(conversation.Members()) > 2: return
    if not conversation.Messages(): return
    last_message = conversation.Messages()[-1]
    if last_message.user is not None and last_message.user.uid == BOT_ID:
      return
    if not last_message.text:
      # This happens if the message is special, like an emoticon.
      return
    conversation.PostMessage(self.therapist.respond(last_message.text))
