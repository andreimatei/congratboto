import abc
import collections

class UserConversation(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def Members(self): pass

  @abc.abstractmethod
  def Messages(self): pass

  @abc.abstractmethod
  def Id(self): pass

  @abc.abstractmethod
  def PostMessage(self, message): pass

User = collections.namedtuple("User", ["uid", "name"])
Message = collections.namedtuple("Message", ["mid", "user", "text"])  # TODO: add timestamp
Conversation = collections.namedtuple("Conversation", ["cid", "members", "messages"])
