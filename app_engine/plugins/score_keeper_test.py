import unittest

import score_keeper
from conversation import (SimpleUserConversation, Message, User)

class SimpleScoreTable(score_keeper.ScoreTable):
  def __init__(self):
    self._scores = {}

  def IncrementMemberScore(self, thread_id, member_name, increment):
    key = (thread_id, member_name)
    is_new = False if key in self._scores else True
    self._scores[key] = self._scores.get(key, 0) + increment
    return self._scores[key], is_new

  def Scores(self, thread_id):
    return sorted([score_keeper.MemberScore(e[0][1], e[1])
        for e in self._scores.iteritems() if e[0][0] == thread_id], key=lambda e: -e.score)


class ScoreKeeperTest(unittest.TestCase):
  def testPost(self):
    conversation = SimpleUserConversation(conversation_id="cid")
    sample_user = User(uid="uid", name="<user_name>")
    new_messages = [
      Message(mid="m1", user=sample_user, text="Vini++"),
      Message(mid="m2", user=sample_user, text="Foo--"),
      Message(mid="m3", user=sample_user, text="Vini++"),
      Message(mid="m4", user=sample_user, text="Vini--"),
      Message(mid="m5", user=sample_user, text="Vini++"),
    ]
    score_table = SimpleScoreTable()
    boto = score_keeper.ScoreKeeper(score_table)
    boto.HandleMessages(conversation, new_messages)

    print conversation.GetPostedMessages()
    self.assertEquals(5, len(conversation.GetPostedMessages()))
    self.assertEquals(2, len(score_table.Scores("cid")))
    self.assertEquals(2, score_table.Scores("cid")[0].score)
    self.assertEquals(-1, score_table.Scores("cid")[1].score)

  def testEmptyScoreCall(self):
    conversation = SimpleUserConversation(conversation_id="cid")
    sample_user = User(uid="uid", name="<user_name>")
    new_messages = [
      Message(mid="m1", user=sample_user, text="/score"),
    ]
    score_table = SimpleScoreTable()
    boto = score_keeper.ScoreKeeper(score_table)
    boto.HandleMessages(conversation, new_messages)

    print conversation.GetPostedMessages()
    self.assertEquals(1, len(conversation.GetPostedMessages()))
    self.assertEquals(0, len(score_table.Scores("cid")))

if __name__ == "__main__":
  unittest.main()