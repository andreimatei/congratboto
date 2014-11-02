import abc
import collections

class UserConversation(object):
  __metaclass__ = abc.ABCMeta

  # This is used to store per conversation state by ScoreKeeper.
  @abc.abstractmethod
  def Id(self):
    """Returns the unique id for this conversation."""
    pass

  # This is used by Eliza to know whether this is an individual or group conversation.
  @abc.abstractmethod
  def Members(self):
    """Returns the list of User members for this conversation."""
    pass

  # Not used by any plugin. This is only called in the page handler.
  # Maybe we can remove it from here.
  @abc.abstractmethod
  def Messages(self):
    """Returns a list of Messages for this conversation."""
    pass

  # Used by all the plugins to post messages to a Conversation.
  @abc.abstractmethod
  def PostMessage(self, message):
    """Posts a message to this conversation"""
    pass


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

