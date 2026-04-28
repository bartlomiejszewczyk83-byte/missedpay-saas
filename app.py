Dane

import streamlit as st
import sqlite3
import re
import pandas as pd
from datetime import datetime

# =========================
# 📱 UI
# =========================
st.set_page_config(page_title="Gmina Analyzer MVP", layout="wide")

st.title("📱🏛️ System analizy gmin (MVP)")
st.caption("Wklej tekst z maila → analiza → ranking")

# =========================
# 🗄️ BAZA
# =========================
conn = sqlite3.connect("gminy_mvp.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS gminy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa TEXT,
    wojewodztwo TEXT,
    typ TEXT,
    pracownicy INTEGER,
    jednostki INTEGER,
    struktura TEXT,
    obszary TEXT,
    podlegle INTEGER,
    ezd INTEGER,
    euslugi INTEGER,
    score REAL,
    raw TEXT,
    created TEXT
)
""")
conn.commit()

# =========================
# 🧠 PARSER
# =========================
def extract_number(pattern, text):
    m = re.search(pattern, text.lower())
    return int(m.group(1)) if m else 0

def parse(text):

    t = text.lower()

    nazwa = re.search(r"gmina ([a-ząćęłńóśźż \-]+)", t)
    nazwa = nazwa.group(1).title() if nazwa else "Nieznana"

    woj = re.search(r"województwo.*?(\d+)", t)
    woj = woj.group(1) if woj else "?"

    typ = "gmina"

    pracownicy = extract_number(r"(\d+)\s*pracown")
    jednostki = extract_number(r"(\d+)\s*jednost")
    struktura = extract_number(r"(\d+)\s*referat")
    podlegle = extract_number(r"(\d+)\s*jednostk.*podleg")

    ezd = 1 if "ezd" in t else 0
    euslugi = 1 if "e-usług" in t or "eusług" in t else 0

    obszary = len(re.findall(r"finans|inwestyc|it|edukac|środow|społec", t))

    return {
        "nazwa": nazwa,
        "wojewodztwo": woj,
        "typ": typ,
        "pracownicy": pracownicy,
        "jednostki": jednostki,
        "struktura": struktura,
        "obszary": obszary,
        "podlegle": podlegle,
        "ezd": ezd,
        "euslugi": euslugi
    }

# =========================
# 📊 SCORE (ranking)
# =========================
def score(d):

    s = 0

    s += d["pracownicy"] * 0.2
    s += d["jednostki"] * 1.0
    s += d["struktura"] * 1.5
    s += d["obszary"] * 2.0
    s += d["podlegle"] * 1.2

    # cyfryzacja
    if d["ezd"] == 0:
        s += 40
    if d["euslugi"] == 0:
        s += 25

    return round(s, 1)

# =========================
# 💾 SAVE
# =========================
def save(d, raw):

    c.execute("""
    INSERT INTO gminy (
        nazwa, wojewodztwo, typ,
        pracownicy, jednostki, struktura,
        obszary, podlegle,
        ezd, euslugi,
        score, raw, created
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        d["nazwa"],
        d["wojewodztwo"],
        d["typ"],
        d["pracownicy"],
        d["jednostki"],
        d["struktura"],
        d["obszary"],
        d["podlegle"],
        d["ezd"],
        d["euslugi"],
        score(d),
        raw,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()

# =========================
# 📥 INPUT
# =========================
text = st.text_area("📄 Wklej odpowiedź z gminy", height=250)

if st.button("🔍 Analizuj"):

    if text.strip():

        d = parse(text)
        s = score(d)

        save(d, text)

        st.success("Zapisano i przeanalizowano")

        col1, col2, col3 = st.columns(3)

        col1.metric("🏛️ Gmina", d["nazwa"])
        col2.metric("📊 Score", s)
        col3.metric("💻 EZD", d["ezd"])

# =========================
# 🏆 RANKING
# =========================
st.divider()
st.subheader("🏆 Ranking gmin")

df = pd.read_sql("SELECT * FROM gminy ORDER BY score DESC", conn)

st.dataframe(df)

if not df.empty:
    st.bar_chart(df.set_index("nazwa")["score"])

# =========================
# 📊 STATYSTYKI
# =========================
if not df.empty:

    st.subheader("📊 Statystyki")

    st.metric("Liczba gmin", len(df))
    st.metric("Średni score", round(df["score"].mean(), 1))
    st.metric("Najlepsza gmina", df.iloc[0]["nazwa"])
