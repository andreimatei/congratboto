# -*- coding: utf-8 -*-
'''
Tests for google_answers
'''
import os
import unittest

import google_answers

class TestParseResponse(unittest.TestCase):
  def testExtractAnswer(self):
    page_html = open(os.path.join(os.path.dirname(__file__), "test_data", "paris.html"))\
        .read().decode('utf-8')
    self.assertEquals(u"Paris", google_answers.ExtractAnswer(page_html))

  def testExtractAnswerUnicode(self):
    page_html = open(os.path.join(os.path.dirname(__file__), "test_data", "brasilia.html"))\
        .read().decode('utf-8')
    self.assertEquals(u"Bras\u00EDlia", google_answers.ExtractAnswer(page_html))

  def testExtractHoliday(self):
    page_html = open(os.path.join(os.path.dirname(__file__), "test_data", "thanksgiving.html"))\
        .read().decode('utf-8')
    self.assertEquals(u"Thursday, November 27", google_answers.ExtractAnswer(page_html))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()