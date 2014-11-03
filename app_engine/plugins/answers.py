'''
Plugin that answers questions from people
'''

from adaptors import google_answers

import logging

logger = logging.getLogger('answers')


class AnswersPlugin(object):
  def HandleMessages(self, conversation, new_messages):
    for message in new_messages:
      if not message.text or message.text.find('?') == -1:
        continue
      logging.info("Answering: %s", message.text)
      answer = google_answers.GetAnswer(message.text)
      conversation.PostMessage(answer)