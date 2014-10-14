import unittest

import congratboto

from facebook_graph import Conversation, Message, User

class FakeSession(object):
  def __init__(self):
    self.messages = []

  def PostMessage(self, thread_id, message):
    self.messages.append((thread_id, message))


class CongratBotoTest(unittest.TestCase):
  def testPost(self):
    session = FakeSession()
    thread_id = "<tid>"
    boto = congratboto.CongratBoto(session)
    boto_user = User(uid=congratboto.BOT_ID, name="Turma Bot")
    boto.HandleMessages(thread_id, Conversation(cid="c0", members=[], messages=[
      Message(mid="m0", user=boto_user, text="+congratboto Man"),
      Message(mid="m1", user=User(uid="u2", name="<author1>"), text="+congratboto Man"),
    ]))
    print session.messages
    self.assertEquals(1, len(session.messages))
    self.assertEqual("<tid>", session.messages[0][0])
    self.assertNotEquals(-1, session.messages[0][1].find("Man"))


if __name__ == "__main__":
  unittest.main()