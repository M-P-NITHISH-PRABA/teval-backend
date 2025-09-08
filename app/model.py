from typing import Dict
from collections import Counter

_POS = {"good","great","excellent","clear","helpful","understand","easy","engaging"}
_NEG = {"bad","poor","confusing","difficult","boring","slow","too fast","rushed"}

def _rule_sentiment(text: str):
    t = text.lower()
    pos = sum(t.count(w) for w in _POS)
    neg = sum(t.count(w) for w in _NEG)
    score = 0.5
    if pos+neg > 0:
        score = pos / (pos+neg)
    label = "NEUTRAL"
    if score > 0.6: label = "POSITIVE"
    elif score < 0.4: label = "NEGATIVE"
    return {"label": label, "score": float(score)}

def _keywords(text: str, top_k=8):
    words = [w.strip(".,!?;:").lower() for w in text.split()]
    words = [w for w in words if len(w)>3]
    ctr = Counter(words)
    return [w for w,_ in ctr.most_common(top_k)]

try:
    from transformers import pipeline
    SENT = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    SUMM = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
except:
    SENT, SUMM = None, None

def analyze_text(text: str) -> Dict:
    if SENT:
        try:
            res = SENT(text[:512])
            s_label = res[0]["label"]
            s_score = float(res[0]["score"])
        except:
            r = _rule_sentiment(text); s_label, s_score = r["label"], r["score"]
    else:
        r = _rule_sentiment(text); s_label, s_score = r["label"], r["score"]
    if SUMM:
        try:
            s = SUMM(text, max_length=60, min_length=15, do_sample=False)
            summary = s[0]["summary_text"]
        except:
            summary = text[:150]
    else:
        summary = text[:150]
    kws = _keywords(text)
    base = s_score if s_label=="POSITIVE" else (1-s_score)
    length_factor = min(len(text)/500, 1.0)
    score = round((40*base + 40*length_factor), 2)
    return {
        "sentiment_label": s_label,
        "sentiment_score": s_score,
        "summary": summary,
        "keywords": kws,
        "score": score
    }
