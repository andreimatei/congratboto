import unittest

import congratboto

class MessageGroup(object):
  def __init__(self, author, messages):
    self.author = author
    self.messages = messages

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
    boto.HandleMessages(thread_id, [
      MessageGroup("Turma Bot", ["+congratboto Man"]),
      MessageGroup("<author1>", ["+congratboto Man"]),
    ])
    print session.messages
    self.assertEquals(1, len(session.messages))
    self.assertEqual("<tid>", session.messages[0][0])
    self.assertNotEquals(-1, session.messages[0][1].find("Man"))


if __name__ == "__main__":
  unittest.main()