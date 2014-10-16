import collections
import json
import urllib2
import urllib

class AuthenticatedUser(object):
  def __init__(self, write_session, access_token):
    self._write_session = write_session
    self._access_token = access_token

  def GetConversations(self):
    inbox_str = urllib2.urlopen("https://graph.facebook.com/me/inbox?" +
                                urllib.urlencode({"access_token": self._access_token})).read()
    return ExtractConversations(self._write_session, inbox_str)


class UserConversation(object):
  def __init__(self, write_session, tid, members, messages):
    self._tid = tid
    self._write_session = write_session
    self._members = members
    self._messages = messages

  def GetMembers(self):
    return self._members

  def GetMessages(self):
    return self._messages

  def GetThreadId(self):
    return self._tid

  def PostMessage(self, message):
    self._write_session.PostMessage(self._tid, message)


User = collections.namedtuple("User", ["uid", "name"])
Message = collections.namedtuple("Message", ["mid", "user", "text"])  # TODO: add timestamp
Conversation = collections.namedtuple("Conversation", ["cid", "members", "messages"])

def UserFromJson(user_json):
  if user_json is None: return None
  return User(user_json["id"], user_json["name"])


def MessageFromJson(msg_json):
  return Message(msg_json["id"], UserFromJson(msg_json.get("from")), msg_json.get("message"))


# This map knows how to go from the Graph conversation id, to the scrape id for posting.
READ_TO_WRITE_MAP = {
   # Turma                  
  "669740653053963": "id.669740653053963",
  # Vini
  "387408068058873": "mid.1384790752857:7f74c5cd85790a7b22",
  # Andrei
  "1422830054600298": "mid.1384722860563:3932eedf826bf6c982",
  # Temp Turma
  "620590488002789": "id.566416863439275",
  # Lorena
  "1378876915695040": "mid.1386221476449:ecba88a4313984db59"
}


def ExtractConversations(write_session, inbox_str):
  inbox_json = json.loads(inbox_str)
  conversations = {}
  for cj in inbox_json["data"]:
    cid = cj["id"]
    members = [UserFromJson(u) for u in cj["to"]["data"]]
    messages = []
    if "comments" in cj:
      messages = [MessageFromJson(m) for m in cj["comments"]["data"]]
    # TODO(fortuna): Make this work for all threads. I can't figure out a way of mapping the
    # conversation.cid to the id the write_session needs, or how to post using the graph API.
    # Apparently there's no API to send messages from an app:
    # https://developers.facebook.com/docs/reference/dialogs/send/
    if len(members) > 2:
      # for group chats, you get the thread id by prepending "id."
      thread_id = "id.%s" % cid
    else:
      thread_id = READ_TO_WRITE_MAP.get(cid)
      if not thread_id: continue
    conversations[cid] = UserConversation(write_session, thread_id, members, messages)    
  return conversations


