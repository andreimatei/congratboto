import json
import urllib2
import urllib

from plugins import conversation

class AuthenticatedUser(object):
  def __init__(self, write_session, access_token):
    self._write_session = write_session
    self._access_token = access_token

  def GetConversations(self):
    inbox_str = urllib2.urlopen("https://graph.facebook.com/me/inbox?" +
                                urllib.urlencode({"access_token": self._access_token})).read()
    return ExtractConversations(self._write_session, inbox_str)


class UserConversation(conversation.UserConversation):
  def __init__(self, write_session, tid, members, messages):
    self._tid = tid
    self._write_session = write_session
    self._members = members
    self._messages = messages

  def Members(self):
    return self._members

  def Messages(self):
    return self._messages

  def Id(self):
    return self._tid

  def PostMessage(self, message):
    self._write_session.PostMessage(self._tid, message)


def UserFromJson(user_json):
  if user_json is None: return None
  return conversation.User(user_json["id"], user_json["name"])


def MessageFromJson(msg_json):
  return conversation.Message(
      msg_json["id"], UserFromJson(msg_json.get("from")), msg_json.get("message"))


# This map knows how to go from the Graph conversation id, to the scrape thread id for posting.
CONVERSATION_TO_THREAD_IDS = {
  # Vini
  "387408068058873": "mid.1384790752857:7f74c5cd85790a7b22",
  # Andrei
  "1422830054600298": "mid.1384722860563:3932eedf826bf6c982",
  # Lorena
  "1378876915695040": "mid.1386221476449:ecba88a4313984db59",
  # Robert
  "628569283851237": "mid.1386221488851:82b0f36e2860e00244"
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
      thread_id = CONVERSATION_TO_THREAD_IDS.get(cid)
      if not thread_id: continue
    conversations[cid] = UserConversation(write_session, thread_id, members, messages)    
  return conversations


