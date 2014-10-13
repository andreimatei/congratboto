import collections
import json
import urllib2
import urllib

class FacebookGraphSession(object):
  def __init__(self, access_token):
    self.access_token = access_token

  def GetInbox(self):
    inbox_str = urllib2.urlopen("https://graph.facebook.com/me/inbox?" +
                                urllib.urlencode({"access_token": self.access_token})).read()
    return ParseInbox(inbox_str)

User = collections.namedtuple("User", ["uid", "name"])
Message = collections.namedtuple("Message", ["mid", "user", "text"])  # TODO: add timestamp
Conversation = collections.namedtuple("Conversation", ["cid", "members", "messages"])

def UserFromJson(user_json):
  if user_json is None: return None
  return User(user_json["id"], user_json["name"])


def MessageFromJson(msg_json):
  return Message(msg_json["id"], UserFromJson(msg_json.get("from")), msg_json.get("message"))


def ParseInbox(inbox_str):
  inbox_json = json.loads(inbox_str)
  inbox = Inbox()
  for cj in inbox_json["data"]:
    cid = cj["id"]
    members = [UserFromJson(u) for u in cj["to"]["data"]]
    messages = []
    if "comments" in cj:
      messages = [MessageFromJson(m) for m in cj["comments"]["data"]]
    inbox.conversations[cid] = Conversation(cid, members, messages)    
  return inbox

class Inbox(object):
  def __init__(self):
    self.conversations = {}

