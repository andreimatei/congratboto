import abc
import collections
import re


class ScoreTable(object):
  """Keeps track of user scores in a thread"""
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def IncrementMemberScore(self, thread_id, member_name, increment):
    pass

  @abc.abstractmethod
  def Scores(self, thread_id):
    """Returns a list of MemberScores"""
    pass

MemberScore = collections.namedtuple("MemberScore", ["name", "score"])


TRIGGER = re.compile('.*?([a-zA-Z0-9]*)((\\+\\+)|(--)).*', re.IGNORECASE)


class ScoreKeeper(object):
  def __init__(self, score_table):
    self._score_table = score_table

  def IncrementScore(self, conversation, addressee, increment):
    new_score, is_new = self._score_table.IncrementMemberScore(
        conversation.Id(), addressee, increment)
    if is_new:
      conversation.PostMessage("Hello %s. You start at %d." % (addressee, new_score))
    else:
      conversation.PostMessage("%s, you're at %d." % (addressee, new_score))
  
  def PrintScores(self, conversation):
    scores = self._score_table.Scores(conversation.Id())
    if not scores:
      conversation.PostMessage("No score point has been assigned")
      return
      
    max_name_width = max([len(ps.name) for ps in scores])
    message = '==== LEADERBOARD ====\n'
    for ps in scores:
      message += '%-*s -> %d\n' % (max_name_width + 1, ps.name, ps.score)
    conversation.PostMessage(message)      

  def HandleMessages(self, conversation, new_messages):
    to_score = []  # (name, increment)
    scores_needed = False
    for message in new_messages:
      if not message.text: continue
      match = TRIGGER.match(message.text)
      if match:
        if match.groups()[0]:
          to_score.append((match.groups()[0], 1 if match.groups()[1] == '++' else -1))
      if message.text.startswith("/score"):
        scores_needed = True
    # post replies, if need
    if to_score:
      for (name, increment) in to_score:
        self.IncrementScore(conversation, name, increment)
    if scores_needed:
      self.PrintScores(conversation)
    
