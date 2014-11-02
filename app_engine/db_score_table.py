from operator import attrgetter

from google.appengine.ext import db
from plugins import score_keeper

class DbMember(db.Model):
  """Models an individual conversation member, with her score."""
  @classmethod
  def _get_kind(cls):
    # TODO(fortuna): Rename Participant to Member.
    return 'Participant'
  thread_id = db.StringProperty(indexed=True)
  name = db.StringProperty(indexed=False)
  score = db.IntegerProperty(default=0, indexed=False)


class DbScoreTable(object):
  def IncrementMemberScore(self, thread_id, member_name, increment):
    member_key = DbScoreTable._GenerateKey(thread_id, member_name)
    member = DbMember.get_or_insert(member_key, thread_id=thread_id, score=0)
    if not member.name:
      is_new_member = True
      member.name = member_name
    else:
      is_new_member = False
    member.score += increment
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
