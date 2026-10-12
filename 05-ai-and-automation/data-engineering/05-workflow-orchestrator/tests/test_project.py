import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workflow_orchestrator import Workflow

class Tests(unittest.TestCase):
    def test_order_and_checkpoint(self):
        calls=[]
        w=Workflow()
        w.add("extract",lambda:calls.append("extract"))
        w.add("publish",lambda:calls.append("publish"),dependencies=("extract",))
        with tempfile.TemporaryDirectory() as tmp:
            cp=Path(tmp)/"state.json"
            self.assertEqual(w.run(cp,"daily"),["extract","publish"])
            self.assertEqual(w.run(cp,"daily"),["extract","publish"])
            self.assertEqual(calls,["extract","publish"])
    def test_cycle(self):
        w=Workflow()
        w.add("a",lambda:None,("b",))
        w.add("b",lambda:None,("a",))
        with self.assertRaises(ValueError): w.order()
if __name__=="__main__": unittest.main()
