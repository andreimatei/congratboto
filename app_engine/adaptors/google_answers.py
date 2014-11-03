'''
Adaptor to get answers from Google Search
'''

import cookielib
import logging
import re
import urllib2

logger = logging.getLogger('google_answers')


def GetAnswer(question):
  cookies = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
  opener.addheaders = [('User-agent',
      'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')]
  try:
    response = opener.open("http://www.google.com/search?ie=UTF-8&q=" + urllib2.quote(question))
    page_html = response.read().decode("utf-8")
  except urllib2.HTTPError as e:
    logging.error("Could not fetch Google Search Results page: %s", e)
    return None
  return ExtractAnswer(page_html)


ANSWER_RE = re.compile(ur'<div class="_eF">(.*?)</div>', re.UNICODE)

def ExtractAnswer(page_html):
  match = ANSWER_RE.search(page_html)
  if match:
    return match.group(1)
  return None

  
def main():
  print GetAnswer("What's the capital of Brazil?")


if __name__ == "__main__":
  main()