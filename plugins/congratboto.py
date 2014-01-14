import logging
import random
import re

logger = logging.getLogger('congratboto')
random.seed()


def generate_message(adresee):
  messages = [('Woop woop!', '%s, woop woop!'),
              ('You are the shit! Nay, THE shit!', '%s, you are the shit! Nay, THE shit!'),
              ('Fucking awesome!', 'Fucking awesome, %s!'),
              ('This is just outstanding!', '%s -> outstanding!'),
              ('My own son could not have done it better!', 'My own son could not have done it better, %s!'),
              ('Amazeballs!', '%s -> amazeballs!'),
              ('Dude, if you were binary, you\'d be all 1s, no 0s.', '%s, if you were binary, you\'d be all 1s, no 0s.'),
              ('Now that\'s a true Turmano!', '%s is again a true Turmano!'),
              ('Take it from me, Congratboto, I have not seen anything like this before!'),
              ('Now this guy deserves a parteeeeeeeeeeeeeeeey!', '%s deserves a parteeeeeeeeeeeeeeeey!'),
              ('From boto a mano, you simply rule!', 'From boto a mano, you simply rule, %s!'),
              ('It\'s like you\'re a damn robot! But in a good way.', '%s, it\'s like you\'re a damn robot! But in a good way.'),
              ('Boy, did you just swish past Usain Bolt just now?', '%s, did you just swish past Usain Bolt just now?'),
              ('You\'re classy. You\'re so classy that you spell "balls" as "bowles".', 'You\'re classy, %s. You\'re so classy that you spell "balls" as "bowles".'),
             ]
  tup = random.choice(messages)
  if isinstance(tup, tuple) and len(tup) == 2:
    if adresee:
      return tup[1] % adresee
    else:
      return tup[0]
  else:
    return tup

BOT_ID = "100007101244912"

#TODO(burbelica): only trigger on "awesome" if it's before a separator, not in the middle of a random phrase 
TRIGGER = re.compile('.*((\+congratboto?|congratulations|(good|awesome|great) job)(\s([a-zA-Z0-9]+).*)?|awesome|amazeballs).*', re.IGNORECASE)

class CongratBoto(object):
  def __init__(self, write_session):
    self.write_session = write_session

  def HandleMessages(self, thread_id, conversation):
    messages = conversation.messages
    congrat_needed = False
    to_congrat = []
    for message in messages:
      if not message.text: continue
      if message.user and message.user.uid == BOT_ID:
        # clear everything from before
        congrat_needed = False
        del to_congrat[:]
        continue
      match = TRIGGER.match(message.text)
      if match:
        congrat_needed = True
        if match.groups()[4]:
          to_congrat.append(match.groups()[4])
    # post replies, if need
    if not congrat_needed:
      return
    if to_congrat:
      for name in to_congrat:
        self.write_session.PostMessage(thread_id, generate_message(name))
    else:
      self.write_session.PostMessage(thread_id, generate_message(None))
