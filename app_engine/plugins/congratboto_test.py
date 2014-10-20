import unittest

import congratboto
from conversation import (SimpleUserConversation, Message, User)


class CongratBotoTest(unittest.TestCase):
  def testPost(self):
    conversation = SimpleUserConversation()
    new_messages = [
      Message(mid="m0", user=User(uid="u2", name="<author1>"), text="Foo"),
      Message(mid="m1", user=User(uid="u2", name="<author1>"), text="+congratboto Man"),
    ]
    boto = congratboto.CongratBoto()
    boto.HandleMessages(conversation, new_messages)
    print conversation.GetPostedMessages()
    self.assertEquals(1, len(conversation.GetPostedMessages()))
    self.assertNotEquals(-1, conversation.GetPostedMessages()[0].find("Man"))


if __name__ == "__main__":
  unittest.main()