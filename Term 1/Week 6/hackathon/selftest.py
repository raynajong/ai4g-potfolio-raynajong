"""Offline tests with fake predictions: python selftest.py"""
import tempfile
import unittest
from pathlib import Path
import db
from filters import relevant
from collector import apply, timestamp

class Fake:
    def analyze(self, text):
        return dict(label="negative",p_neg=.8,p_neu=.1,p_pos=.1,score=-.7)

def event(op="create",text="I feel unsafe waiting at the train station",lang="en"):
    return dict(kind="commit", did="did:plc:test",time_us=1700000000000000,
      commit=dict(operation=op,collection="app.bsky.feed.post",rkey="abc",
      record=dict(text=text,langs=[lang],createdAt="2023-11-14T22:13:20Z")))

class Tests(unittest.TestCase):
    def test_filters(self):
        self.assertTrue(relevant(event()["commit"]["record"]))
        self.assertFalse(relevant(dict(text="Subway surfers is scary today",langs=["en"])))
        self.assertFalse(relevant(dict(text="A dangerous metropolis today",langs=["en"])))
        self.assertFalse(relevant(event(lang="nl")["commit"]["record"]))
        self.assertFalse(relevant(dict(text="unsafe train station without language")))
    def test_lifecycle(self):
        with tempfile.TemporaryDirectory() as d:
            con=db.connect(Path(d)/"test.db")
            self.assertTrue(apply(con,Fake(),event()))
            self.assertFalse(apply(con,Fake(),event()))
            self.assertEqual(con.execute("SELECT count(*) FROM posts").fetchone()[0],1)
            self.assertTrue(apply(con,Fake(),event("update", "I feel scared at the metro station today")))
            apply(con,Fake(),event("update","Lovely unrelated weather today"))
            self.assertEqual(con.execute("SELECT count(*) FROM posts").fetchone()[0],0)
            apply(con,Fake(),event());apply(con,Fake(),event("delete"))
            self.assertEqual(con.execute("SELECT count(*) FROM posts").fetchone()[0],0)
            db.checkpoint(con,12345)
            self.assertEqual(db.meta(con,"cursor"),"12345")
            con.close()
    def test_timestamp(self):
        self.assertEqual(timestamp("2023-11-14T22:13:20Z",1700000000),1700000000)
        self.assertEqual(timestamp("bad",1700000000),1700000000)
if __name__ == "__main__":
    unittest.main(verbosity=2)
