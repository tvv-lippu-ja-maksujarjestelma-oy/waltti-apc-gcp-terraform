import unittest
from observe import gate,assess
class GateTest(unittest.TestCase):
 def samples(self):return [{'time':i,'errors':[]} for i in range(0,86401,300)]
 def test_wait_full_day(self):self.assertFalse(gate(self.samples(),0,86399)[0])
 def test_clean_day(self):self.assertTrue(gate(self.samples(),0,86400)[0])
 def test_sleep_gap(self):self.assertFalse(gate([s for s in self.samples() if not 3600<s['time']<7200],0,86400)[0])
 def test_failed_sample_latches(self):
  s=self.samples();s[50]['errors']=['API unavailable'];self.assertFalse(gate(s,0,86400)[0])
 def test_stale_last_sample(self):self.assertFalse(gate(self.samples()[:-3],0,86400)[0])
 def test_missing_baseline_coverage(self):self.assertFalse(gate(self.samples()[3:],0,86400)[0])
 def test_new_oom_blocks(self):
  b={'environments':{'dev':{'workloads':{},'pods':{},'topics':{}}}}
  c={'errors':[],'environments':{'dev':{'workloads':{},'pods':{'x':{'phase':'Running','name':'foo','oom':True,'restarts':1}},'topics':{}}}}
  self.assertTrue(assess(c,b,0))

class PromotionTest(unittest.TestCase):
 def test_changed_pr_head_blocks(self):
  from promote import approved_pr
  with self.assertRaises(RuntimeError):approved_pr({'head':'reviewed','url':'example'}, {'headRefOid':'changed','state':'OPEN','mergeable':'MERGEABLE','statusCheckRollup':[]})
 def test_pending_ci_blocks(self):
  from promote import approved_pr
  with self.assertRaises(RuntimeError):approved_pr({'head':'same','url':'example'}, {'headRefOid':'same','state':'OPEN','mergeable':'MERGEABLE','statusCheckRollup':[{'status':'IN_PROGRESS'}]})
 def test_rollback_removes_new_cpu_limit(self):
  from promote import rollback_patch
  p={'kind':'StatefulSet','patch':{'spec':{'template':{'spec':{'initContainers':[{'name':'init','resources':{'requests':{'cpu':'500m'},'limits':{'cpu':'1'}}}]}}}}}
  b={'kind':'StatefulSet','spec':{'template':{'spec':{'initContainers':[{'name':'init','resources':{'requests':{'cpu':'1'},'limits':{'memory':'2Gi'}}}]}}}}
  r=rollback_patch(p,b)['spec']['template']['spec']['initContainers'][0]['resources']
  self.assertEqual(r,{'requests':{'cpu':'1'},'limits':{'cpu':None}})

if __name__=='__main__':unittest.main()
