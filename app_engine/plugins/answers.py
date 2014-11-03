'''
Plugin that answers questions from people
'''

from adaptors import google_answers

import logging

logger = logging.getLogger('answers')

def GetFirstName(full_name):
  return full_name.split()[0]

def GetLastQuestion(messages):
  for message in reversed(messages):
    if not message.text:
      continue
    if message.text.find('?') != -1:
      return message
  return None

class AnswersPlugin(object):
  def HandleMessages(self, conversation, new_messages):
    last_question = GetLastQuestion(new_messages)
    if not last_question:
      return
    logging.info("Answering: %s", last_question.text)
    answer = google_answers.GetAnswer(last_question.text)
    if answer is not None:
      logging.info("Answering with %s", answer)
      reply = ""
      if last_question.user and last_question.user.name and len(conversation.Members()) > 2:
        reply = u"@%s: " % GetFirstName(last_question.user.name)
      reply += answer
      conversation.PostMessage(reply)
    else:
      logging.info("No answer found.")