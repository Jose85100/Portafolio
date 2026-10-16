import random
import unittest
from src.engine import PATHS, REGIMES, activity_set, alignment, direct_follows, sample, score

class TestConformance(unittest.TestCase):
    def test_approved(self):
        for t in PATHS:
            self.assertEqual(alignment(t)[0],0)
            self.assertTrue(direct_follows(t))
    def test_hybrid(self):
        t=("intake","validate","manual_review","approve","notify","archive")
        self.assertTrue(activity_set(t))
        self.assertTrue(direct_follows(t))
        self.assertEqual(alignment(t)[0],1)
    def test_missing(self):
        t=list(PATHS[0]);t.remove("validate")
        self.assertEqual(alignment(t)[0],1)
    def test_duplicate(self):
        t=list(PATHS[0]);t.insert(2,"validate")
        self.assertTrue(activity_set(t))
        self.assertFalse(direct_follows(t))
        self.assertEqual(alignment(t)[0],1)
    def test_unknown(self):
        t=list(PATHS[0]);t.insert(2,"unknown")
        self.assertFalse(activity_set(t))
        self.assertFalse(direct_follows(t))
        self.assertEqual(alignment(t)[0],1)
    def test_invalid(self):
        with self.assertRaises(ValueError):alignment([])
        with self.assertRaises(ValueError):direct_follows([" "])
    def test_tie(self):
        t=("intake","validate","manual_review","approve","archive")
        self.assertEqual(alignment(t),alignment(t))
    def test_seed(self):
        self.assertEqual(sample(1,30),sample(1,30))
        self.assertNotEqual(sample(1,30),sample(2,30))
    def test_label_oracle(self):
        for seed in range(40):
            for h in REGIMES.values():
                rows=sample(seed,h)
                self.assertEqual(len(rows),120)
                self.assertEqual(sum(y for _,y,_ in rows),60)
                for t,y,_ in rows:
                    self.assertEqual(y,int(t not in PATHS))
                    self.assertEqual(y,int(alignment(t)[0]>0))
    def test_metrics(self):
        self.assertEqual(score([0,1],[0,1])["f1"],1.0)
        self.assertEqual(score([0,1],[0,0])["recall"],0)
    def test_random_edit(self):
        r=random.Random(42)
        for _ in range(200):
            t=list(r.choice(PATHS))
            t.insert(r.randrange(len(t)+1),"unknown")
            self.assertEqual(alignment(t)[0],1)

if __name__=="__main__":unittest.main()
