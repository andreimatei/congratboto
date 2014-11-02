'''
Tests for db_score_table
'''

import sys
import unittest

# Workaround for not finding the yaml module error.
import dev_appserver
sys.path = dev_appserver.EXTRA_PATHS + sys.path 

from google.appengine.ext import testbed
import db_score_table

class DbScoreTableTest(unittest.TestCase):
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()
  
  def testEmptyTable(self):
    score_table = db_score_table.DbScoreTable()
    scores = score_table.Scores("tid")
    self.assertEquals(0, len(scores))

  def testIncrementsTable(self):
    score_table = db_score_table.DbScoreTable()
    score_table.IncrementMemberScore("tid", "m1", 2)
    score_table.IncrementMemberScore("tid", "m2", 3)
    score_table.IncrementMemberScore("tid", "m1", -1)
    score_table.IncrementMemberScore("tid", "m3", -4)
    scores = score_table.Scores("tid")
    print scores
    self.assertEquals(3, len(scores))
    self.assertEquals("m2", scores[0].name)
    self.assertEquals(3, scores[0].score)
    self.assertEquals("m1", scores[1].name)
    self.assertEquals(1, scores[1].score)
    self.assertEquals("m3", scores[2].name)
    self.assertEquals(-4, scores[2].score)

if __name__ == "__main__":
  unittest.main()
