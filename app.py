import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="IntelliHire AI",
    page_icon="🚀",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

h1, h2, h3 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 15px;
}

.stDataFrame {
    background-color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect("intellihire.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    email TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()

# =========================================
# LOGIN SYSTEM
# =========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = ""

# =========================================
# SIDEBAR
# =========================================

st.sidebar.title("🚀 IntelliHire AI")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Login", "Dashboard"]
)

# =========================================
# LOGIN PAGE
# =========================================

if menu == "Login":

    st.title("🔐 Login / Register")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    col1, col2 = st.columns(2)

    # REGISTER

    if col1.button("Register"):

        c.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        if c.fetchone():

            st.error("User already exists")

        else:

            c.execute(
                "INSERT INTO users VALUES (?,?)",
                (email, password)
            )

            conn.commit()

            st.success("Registered Successfully")

    # LOGIN

    if col2.button("Login"):

        c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        data = c.fetchone()

        if data:

            st.session_state.logged_in = True
            st.session_state.email = email

            st.success("Login Successful")

        else:

            st.error("Invalid Credentials")

# =========================================
# DASHBOARD
# =========================================

elif menu == "Dashboard":

    if not st.session_state.logged_in:

        st.warning("Login First")

    else:

        st.title("🚀 IntelliHire AI Dashboard")

        st.markdown("""
### AI-Powered Recruitment Intelligence Platform
""")

        st.success(
            f"Logged in as {st.session_state.email}"
        )

        # =====================================
        # JOB DESCRIPTION
        # =====================================

        job_desc = st.text_area(
            "Paste Job Description"
        )

        uploaded_files = st.file_uploader(
            "Upload Resumes",
            accept_multiple_files=True,
            type=["txt"]
        )

        analyze = st.button("Analyze Candidates")

        # =====================================
        # SKILLS
        # =====================================

        skills_list = [
            "python",
            "java",
            "machine learning",
            "sql",
            "html",
            "css",
            "javascript",
            "pandas",
            "numpy",
            "nlp"
        ]

        # =====================================
        # ANALYSIS
        # =====================================

        if analyze:

            resumes = []
            names = []

            for file in uploaded_files:

                text = file.read().decode("utf-8")

                resumes.append(text)

                names.append(file.name)

            corpus = resumes + [job_desc]

            tfidf = TfidfVectorizer(
                stop_words='english'
            )

            vectors = tfidf.fit_transform(corpus)

            jd_vector = vectors[-1]

            resume_vectors = vectors[:-1]

            scores = cosine_similarity(
                resume_vectors,
                jd_vector
            )

            results = []

            selected = 0
            rejected = 0

            # =================================
            # PROCESS EACH RESUME
            # =================================

            for i, score in enumerate(scores):

                percent = round(score[0] * 100, 2)

                decision = (
                    "Selected"
                    if percent > 30
                    else "Rejected"
                )

                if decision == "Selected":
                    selected += 1
                else:
                    rejected += 1

                matched = []

                missing = []

                for skill in skills_list:

                    if (
                        skill in resumes[i].lower()
                        and
                        skill in job_desc.lower()
                    ):

                        matched.append(skill)

                    elif skill in job_desc.lower():

                        missing.append(skill)

                explanation = f"""
Strong skill alignment detected.

Matched Skills:
{', '.join(matched)}

Missing Skills:
{', '.join(missing)}
"""

                questions = [
                    f"Explain your experience in {s}"
                    for s in matched[:3]
                ]

                results.append({

                    "Candidate": names[i],

                    "Match %": percent,

                    "Decision": decision,

                    "Matched Skills":
                    ", ".join(matched),

                    "Explanation":
                    explanation,

                    "Interview Questions":
                    " | ".join(questions)
                })

            # =================================
            # DATAFRAME
            # =================================

            df = pd.DataFrame(results)

            df = df.sort_values(
                by="Match %",
                ascending=False
            )

            # =================================
            # KPI CARDS
            # =================================

            avg_score = round(
                df["Match %"].mean(),
                2
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total Resumes",
                len(df)
            )

            c2.metric(
                "Selected",
                selected
            )

            c3.metric(
                "Rejected",
                rejected
            )

            c4.metric(
                "Average Match %",
                avg_score
            )

            st.divider()

            # =================================
            # TABLE
            # =================================

            st.subheader(
                "🏆 Candidate Leaderboard"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            # =================================
            # BAR CHART
            # =================================

            st.subheader(
                "📊 Match Score Analytics"
            )

            fig = px.bar(
                df,
                x="Candidate",
                y="Match %",
                color="Decision",
                text="Match %"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================
            # PIE CHART
            # =================================

            st.subheader(
                "📈 Hiring Distribution"
            )

            pie = px.pie(
                names=["Selected", "Rejected"],
                values=[selected, rejected]
            )

            st.plotly_chart(
                pie,
                use_container_width=True
            )

            # =================================
            # AI INSIGHTS
            # =================================

            st.subheader(
                "🧠 AI Hiring Insights"
            )

            top = df.iloc[0]

            st.success(
                f"Top Candidate: {top['Candidate']}"
            )

            st.markdown(f"""
### Why Selected?

✔ High similarity score

✔ Strong technical skill match

✔ Relevant keywords detected

✔ Match Score: {top['Match %']}%
""")

            # =================================
            # DOWNLOAD REPORT
            # =================================

            csv = df.to_csv(
                index=False
            ).encode('utf-8')

            st.download_button(
                label="📥 Download Report",
                data=csv,
                file_name='hiring_report.csv',
                mime='text/csv'
            )