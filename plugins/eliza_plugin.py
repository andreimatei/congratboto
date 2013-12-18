import eliza

BOT_ID = "100007101244912"

class ElizaPlugin(object):
  def __init__(self, write_session):
    self.write_session = write_session
    self.therapist = eliza.eliza()

  def HandleMessages(self, thread_id, conversation):
    if len(conversation.members) > 2: return
    if not conversation.messages: return
    last_message = conversation.messages[-1]
    if last_message.user is not None and last_message.user.uid == BOT_ID:
      return
    self.write_session.PostMessage(thread_id, self.therapist.respond(last_message.text))
