import unittest

import congratboto

from adaptors.facebook_graph import Message, User

class UserConversation(object):
  def __init__(self, messages):
    self._initial_messages = messages
    self._posted_messages = []

  def Messages(self):
    return self._initial_messages

  def GetPostedMessages(self):
    return self._posted_messages

  def PostMessage(self, message):
    self._posted_messages.append(message)


class CongratBotoTest(unittest.TestCase):
  def testPost(self):
    boto_user = User(uid=congratboto.BOT_ID, name="Turma Bot")
    conversation = UserConversation([
      Message(mid="m0", user=boto_user, text="+congratboto Man"),
      Message(mid="m1", user=User(uid="u2", name="<author1>"), text="+congratboto Man"),
    ])
    boto = congratboto.CongratBoto()
    boto.HandleMessages(conversation)
    print conversation.GetPostedMessages()
    self.assertEquals(1, len(conversation.GetPostedMessages()))
    self.assertNotEquals(-1, conversation.GetPostedMessages()[0].find("Man"))


if __name__ == "__main__":
  unittest.main()