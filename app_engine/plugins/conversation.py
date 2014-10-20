import abc
import collections

class UserConversation(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def Id(self): pass

  @abc.abstractmethod
  def Members(self): pass

  @abc.abstractmethod
  def Messages(self): pass

  @abc.abstractmethod
  def PostMessage(self, message): pass


User = collections.namedtuple("User", ["uid", "name"])
Message = collections.namedtuple("Message", ["mid", "user", "text"])  # TODO: add timestamp
Conversation = collections.namedtuple("Conversation", ["cid", "members", "messages"])


class SimpleUserConversation(UserConversation):
  """Implementation of UserConversation that is useful in tests"""
  def __init__(self, conversation_id="cid", messages=[], members=[]):
    self._id = conversation_id
    self._members = members
    self._initial_messages = messages
    self._posted_messages = []

  def Id(self):
    return self._id

  def Members(self):
    self._members

  def Messages(self):
    return self._initial_messages

  def GetPostedMessages(self):
    return self._posted_messages

  def PostMessage(self, message):
    self._posted_messages.append(message)

