import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gmina Analyzer V1", layout="wide")

st.title("📊 Gmina Analyzer V1 (stable MVP)")
st.caption("Wklej odpowiedź z gminy → analiza → ranking")

# =========================
# MEMORY
# =========================
if "data" not in st.session_state:
    st.session_state.data = []

    # =========================
    # ANALIZA
    # =========================
    def analyze(text: str):

        t = text.lower()
            score = 0

                # cyfryzacja (braki = gorzej)
                    if "ezd" not in t:
                            score += 40
                                if "e-usług" not in t and "eusług" not in t:
                                        score += 25

                                            # struktura urzędu
                                                score += t.count("wydział") * 5
                                                    score += t.count("referat") * 3
                                                        score += t.count("biuro") * 2

                                                            # obszary działania
                                                                keywords = ["finans", "inwestyc", "it", "edukac", "środow", "społ"]
                                                                    areas = sum(1 for k in keywords if k in t)

                                                                        score += areas * 10

                                                                            return {
                                                                                    "score": round(score, 1),
                                                                                            "areas": areas
                                                                                                }

                                                                                                # =========================
                                                                                                # INPUT
                                                                                                # =========================
                                                                                                text = st.text_area("📄 Wklej odpowiedź z gminy", height=250)

                                                                                                if st.button("🔍 Analizuj"):

                                                                                                    if text.strip():

                                                                                                            result = analyze(text)

                                                                                                                    st.session_state.data.append({
                                                                                                                                "czas": datetime.now().strftime("%H:%M:%S"),
                                                                                                                                            "score": result["score"],
                                                                                                                                                        "obszary": result["areas"],
                                                                                                                                                                    "fragment": text[:120]
                                                                                                                                                                            })

                                                                                                                                                                                    st.success("✔ Dodano analizę")

                                                                                                                                                                                            st.metric("Score", result["score"])
                                                                                                                                                                                                    st.metric("Obszary", result["areas"])

                                                                                                                                                                                                    # =========================
                                                                                                                                                                                                    # RANKING
                                                                                                                                                                                                    # =========================
                                                                                                                                                                                                    st.divider()
                                                                                                                                                                                                    st.subheader("🏆 Ranking gmin")

                                                                                                                                                                                                    if st.session_state.data:

                                                                                                                                                                                                        df = pd.DataFrame(st.session_state.data)
                                                                                                                                                                                                            df = df.sort_values("score", ascending=False)

                                                                                                                                                                                                                st.dataframe(df)
                                                                                                                                                                                                                    st.bar_chart(df.set_index("czas")["score"])

                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                        st.info("Brak danych — wklej pierwszy tekst i kliknij Analizuj")