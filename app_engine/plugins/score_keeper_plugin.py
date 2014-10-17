import re
from operator import attrgetter

from google.appengine.ext import db

BOT_ID = "100007101244912"


class Participant(db.Model):
  """Models an individual chat participant, with her score."""
  thread_id = db.StringProperty(indexed=True)
  name = db.StringProperty(indexed=False)
  score = db.IntegerProperty(indexed=False)


class DbParticipantRepository(object):
  @staticmethod
  def _GenerateKey(thread_id, name):
    normalized_name = name.capitalize()
    return "%s-%s" % (thread_id, normalized_name)

  def ParticipantByName(self, thread_id, name):
    participant_key = DbParticipantRepository._GenerateKey(thread_id, name)
    participant = db.get(db.Key.from_path('Participant', participant_key))
    if not participant:
      participant = Participant(key_name = participant_key)
      participant.name = name
      participant.score = 0
      participant.thread_id = thread_id
    return participant

  def ParticipantsForThread(self, thread_id):
    q = Participant.all()
    q.filter("thread_id =", thread_id)
    return q.run()
    

TRIGGER = re.compile('.*?([a-zA-Z0-9]*)((\\+\\+)|(--)).*', re.IGNORECASE)


class ScoreKeeper(object):
  def __init__(self):
    self._participant_repo = DbParticipantRepository()

  def IncrementScore(self, conversation, addressee, increment):
    participant = self._participant_repo.ParticipantByName(conversation.ThreadId(), addressee)
    participant.score += increment
    participant.put()
    conversation.PostMessage("%s, you're at %d." % (addressee, participant.score))
  
  def PrintScores(self, conversation):
    participants = self._participant_repo.ParticipantsForThread(conversation.ThreadId())
    participants = sorted(participants, key=attrgetter('score'), reverse=True)
    
    max_name_width = max([len(p.name) for p in participants])
    message = '==== LEADERBOARD ====\n'
    for p in participants:
      message += '%-*s -> %d\n' % (max_name_width + 1, p.name, p.score)
    conversation.PostMessage(message)      

  def HandleMessages(self, conversation):
    messages = conversation.Messages()
    to_score = []  # (name, increment)
    scores_needed = False
    for message in messages:
      if not message.text: continue
      if message.user and message.user.uid == BOT_ID:
        # clear everything from before
        del to_score[:]
        scores_needed = False
        continue
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
    
