import sqlite3, json
from datetime import datetime

DB_PATH = "teval.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, teacher_id TEXT, student_id TEXT,
        text TEXT, analysis_json TEXT, created_at TEXT
    )""")
    conn.commit(); conn.close()

def insert_feedback(session_id, teacher_id, student_id, text, analysis):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created = datetime.utcnow().isoformat()
    c.execute("INSERT INTO feedback (session_id, teacher_id, student_id, text, analysis_json, created_at) VALUES (?,?,?,?,?,?)",
              (session_id, teacher_id, student_id, text, json.dumps(analysis), created))
    fid = c.lastrowid
    conn.commit(); conn.close()
    return fid

def get_feedback(fid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,session_id,teacher_id,student_id,text,analysis_json,created_at FROM feedback WHERE id=?", (fid,))
    row = c.fetchone(); conn.close()
    if not row: return None
    return {"id":row[0],"session_id":row[1],"teacher_id":row[2],"student_id":row[3],
            "text":row[4],"analysis":json.loads(row[5]),"created_at":row[6]}

def get_session_analytics(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT analysis_json FROM feedback WHERE session_id=?", (session_id,))
    rows = c.fetchall(); conn.close()
    if not rows: return {"count":0,"avg_sentiment":None,"top_keywords":[]}
    import collections
    sentiments=[]; counter=collections.Counter()
    for (aj,) in rows:
        a=json.loads(aj); sentiments.append(a.get("sentiment_score",0))
        for k in a.get("keywords",[]): counter[k]+=1
    avg=sum(sentiments)/len(sentiments)
    return {"count":len(rows),"avg_sentiment":avg,"top_keywords":[k for k,_ in counter.most_common(5)]}
