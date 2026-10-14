"""Create a separate synthetic preview database. Never used by the real collector."""
import os
os.environ["TRANSIT_DEMO"] = "1"
import time
import db
import config
con = db.connect()
if con.execute("SELECT count(*) FROM posts").fetchone()[0]:
    raise SystemExit("Demo already exists. Run dashboard in demo mode.")
examples = [
 ("I felt scared waiting at the train station alone.", "negative", .85,.1,.05),
 ("The new lighting at the metro station makes me feel safe.", "positive", .05,.15,.8),
 ("A security office is next to the train station entrance.", "neutral", .1,.8,.1)]
now=int(time.time())
for i in range(36):
    text,label,neg,neu,pos=examples[i%3]
    db.save(con,dict(uri="demo://%d"%i,text="SYNTHETIC: "+text,permalink="",
      created_utc=now-(35-i)*3600,collected_utc=now,label=label,p_neg=neg,p_neu=neu,p_pos=pos,score=pos-neg))
con.close()
print("Separate demo database created. Preview with:")
print("TRANSIT_DEMO=1 python -m streamlit run dashboard.py")
