from operator import attrgetter

from google.appengine.ext import db
from plugins import score_keeper_plugin

class DbParticipant(db.Model):
  """Models an individual chat participant, with her score."""
  thread_id = db.StringProperty(indexed=True)
  name = db.StringProperty(indexed=False)
  score = db.IntegerProperty(indexed=False)


class DbScoreTable(object):
  def IncrementParticipantScore(self, thread_id, member_name, increment):
    participant_key = DbScoreTable._GenerateKey(thread_id, member_name)
    participant = db.get(db.Key.from_path('Participant', participant_key))
    is_new_participant = True if participant else False
    if is_new_participant:
      participant = DbParticipant(key_name = participant_key)
      participant.name = member_name
      participant.score = 0
      participant.thread_id = thread_id
    participant.put()
    return participant.score, is_new_participant

  def Scores(self, thread_id):
    q = DbParticipant.all()
    q.filter("thread_id =", thread_id)
    participants = q.run()
    participants = sorted(participants, key=attrgetter('score'), reverse=True)
    return [score_keeper_plugin.ParticipantScore(p.name, p.score) for p in participants]

  @staticmethod
  def _GenerateKey(thread_id, name):
    normalized_name = name.capitalize()
    return "%s-%s" % (thread_id, normalized_name)
