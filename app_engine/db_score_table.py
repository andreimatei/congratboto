from operator import attrgetter

from google.appengine.ext import db
from plugins import score_keeper

class DbMember(db.Model):
  """Models an individual conversation member, with her score."""
  thread_id = db.StringProperty(indexed=True)
  name = db.StringProperty(indexed=False)
  score = db.IntegerProperty(indexed=False)


class DbScoreTable(object):
  def IncrementMemberScore(self, thread_id, member_name, increment):
    member_key = DbScoreTable._GenerateKey(thread_id, member_name)
    # TODO(fortuna): Rename Participant to Member.
    member = db.get(db.Key.from_path('Participant', member_key))
    is_new_member = True if member else False
    if is_new_member:
      member = DbMember(key_name = member_key)
      member.name = member_name
      member.score = 0
      member.thread_id = thread_id
    member.put()
    return member.score, is_new_member

  def Scores(self, thread_id):
    q = DbMember.all()
    q.filter("thread_id =", thread_id)
    members = q.run()
    members = sorted(members, key=attrgetter('score'), reverse=True)
    return [score_keeper.MemberScore(p.name, p.score) for p in members]

  @staticmethod
  def _GenerateKey(thread_id, name):
    normalized_name = name.capitalize()
    return "%s-%s" % (thread_id, normalized_name)
