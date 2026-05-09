from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from flask_sqlalchemy import SQLAlchemy
from reportlab.platypus import Table
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import pandas as pd
import os

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from PyPDF2 import PdfReader

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

# =========================================
# APP CONFIG
# =========================================

app = Flask(__name__)

app.secret_key = "intellihire_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['UPLOAD_FOLDER'] = 'uploads'

# =========================================
# DATABASE
# =========================================

db = SQLAlchemy(app)

# =========================================
# LOGIN MANAGER
# =========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# =========================================
# FOLDERS
# =========================================

UPLOAD_FOLDER = "uploads"

CHART_FOLDER = "static/charts"

REPORT_FOLDER = "reports"

ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# =========================================
# FILE VALIDATION
# =========================================

def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================================
# DATASET
# =========================================

df = pd.read_csv("Resume.csv")

# =========================================
# DATABASE MODELS
# =========================================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    profile_image = db.Column(
        db.String(200),
        default="default.png"
    )


class Screening(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    candidate_name = db.Column(
        db.String(200)
    )

    ats_score = db.Column(
        db.Float
    )

    status = db.Column(
        db.String(100)
    )

# =========================================
# USER LOADER
# =========================================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))

# =========================================
# PDF EXTRACTION
# =========================================

def extract_resume_text(filepath):

    text = ""

    try:

        reader = PdfReader(filepath)

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

    except Exception as e:

        print(e)

        text = ""

    return text

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return render_template("home.html")

# =========================================
# REGISTER
# =========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already exists")

            return redirect(url_for("register"))

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)

        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("login"))

    return render_template("register.html")

# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(url_for("dashboard"))

        else:

            flash("Invalid Email or Password")

    return render_template("login.html")

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))

# =========================================
# DASHBOARD
# =========================================

@app.route("/dashboard")
@login_required
def dashboard():

    total = len(df)

    categories = df['Category'].nunique()

    avg_words = int(
        df['Resume_str']
        .apply(lambda x: len(str(x).split()))
        .mean()
    )

    screenings = Screening.query.count()

    leaderboard = Screening.query.order_by(
        Screening.ats_score.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        total=total,
        categories=categories,
        avg_words=avg_words,
        screenings=screenings,
        leaderboard=leaderboard
    )

# =========================================
# SCREENING
# =========================================

@app.route("/screening", methods=["GET", "POST"])
@login_required
def screening():

    results = []

    if request.method == "POST":

        job_desc = request.form["jobdesc"]

        files = request.files.getlist("resume")

        for file in files:

            if not allowed_file(file.filename):

                flash("Only PDF resumes allowed")

                continue

            filename = secure_filename(
                file.filename
            )

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            file.save(filepath)

            text = extract_resume_text(filepath)

            tfidf = TfidfVectorizer(
                stop_words='english'
            )

            combined_text = text.lower() * 2

            vectors = tfidf.fit_transform([
                combined_text,
                job_desc.lower()
            ])

            similarity = cosine_similarity(
                vectors[0],
                vectors[1]
            )[0][0]

            score = round((similarity * 100) + 45, 2)

            if score > 100:
                score = 100

            if score >= 60:

                status = "Selected ✅"

            elif score >= 35:

                status = "Moderate Match ⚠️"

            else:

                status = "Rejected ❌"

            skills = [
                "python",
                "machine learning",
                "sql",
                "flask",
                "nlp",
                "docker",
                "aws",
                "java",
                "html",
                "css",
                "javascript"
            ]

            resume_skills = []

            for skill in skills:

                if skill.lower() in text.lower():

                    resume_skills.append(skill)

            missing_skills = []

            for skill in skills:

                if skill.lower() not in text.lower():

                    missing_skills.append(skill)

            suggestions = []

            if score < 40:

                suggestions.append(
                    "Resume ATS compatibility is low"
                )

            elif score < 70:

                suggestions.append(
                    "Resume partially matches role"
                )

            else:

                suggestions.append(
                    "Resume strongly matches role"
                )

            suggestions.append(
                "Use ATS friendly formatting"
            )

            questions = []

            if "python" in resume_skills:

                questions.append(
                    "Explain Python decorators."
                )

            if "sql" in resume_skills:

                questions.append(
                    "Explain SQL joins."
                )

            if not questions:

                questions.append(
                    "Tell me about yourself."
                )

            summary = (
                f"Candidate has ATS score "
                f"of {score}%"
            )

            screening_data = Screening(
                candidate_name=filename,
                ats_score=score,
                status=status
            )

            db.session.add(screening_data)

            db.session.commit()

            results.append({

                "name": filename,
                "score": score,
                "status": status,
                "skills": resume_skills,
                "missing": missing_skills[:5],
                "suggestions": suggestions,
                "questions": questions,
                "summary": summary
            })

        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

    return render_template(
        "screening.html",
        results=results
    )

# =========================================
# ANALYTICS
# =========================================

@app.route("/analytics")
@login_required
def analytics():

    top_categories = df['Category'].value_counts().head(10)

    plt.figure(figsize=(10,5))

    sns.barplot(
        x=top_categories.index,
        y=top_categories.values
    )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("static/charts/univariate.png")

    plt.close()

    df['Resume_Length'] = df['Resume_str'].apply(
        lambda x: len(str(x).split())
    )

    plt.figure(figsize=(10,5))

    sns.histplot(
        df['Resume_Length'],
        bins=30
    )

    plt.tight_layout()

    plt.savefig("static/charts/resume_length.png")

    plt.close()

    text = " ".join(df['Resume_str'].astype(str))

    wordcloud = WordCloud(
        width=1000,
        height=500,
        background_color='white'
    ).generate(text)

    plt.figure(figsize=(12,6))

    plt.imshow(wordcloud)

    plt.axis("off")

    plt.tight_layout()

    plt.savefig("static/charts/wordcloud.png")

    plt.close()

    total_resumes = len(df)

    total_categories = df['Category'].nunique()

    avg_resume_length = int(
        df['Resume_Length'].mean()
    )

    top_category = df['Category'].value_counts().idxmax()

    missing_values = df.isnull().sum().sum()

    return render_template(
        "analytics.html",
        total_resumes=total_resumes,
        total_categories=total_categories,
        avg_resume_length=avg_resume_length,
        top_category=top_category,
        missing_values=missing_values
    )

# =========================================
# INTELLIGENCE
# =========================================

@app.route("/intelligence")
@login_required
def intelligence():

    insights = [
        "Python developers are highly demanded",
        "Cloud skills improve ATS scores",
        "Recruiters prefer ATS friendly resumes"
    ]

    recommendations = [
        "Add certifications",
        "Improve keyword optimization",
        "Add projects"
    ]

    technologies = [
        "TF-IDF",
        "Cosine Similarity",
        "Flask",
        "SQLite"
    ]

    return render_template(
        "intelligence.html",
        insights=insights,
        recommendations=recommendations,
        technologies=technologies
    )

# =========================================
# LEADERBOARD
# =========================================

@app.route("/leaderboard")
@login_required
def leaderboard():

    screenings = Screening.query.order_by(
        Screening.ats_score.desc()
    ).all()

    return render_template(
        "leaderboard.html",
        screenings=screenings
    )

# =========================================
# PROFILE
# =========================================

@app.route("/profile")
@login_required
def profile():

    return render_template(
        "recruiter_profile.html"
    )

# =========================================
# ADMIN PANEL
# =========================================

@app.route("/admin")
@login_required
def admin():

    users = User.query.all()

    screenings = Screening.query.order_by(
        Screening.ats_score.desc()
    ).all()

    return render_template(
        "admin.html",
        users=users,
        screenings=screenings
    )

# =========================================
# PDF REPORT
# =========================================

@app.route("/report/<name>/<score>")
def generate_report(name, score):

    filepath = f"reports/{name}.pdf"

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "IntelliHire ATS Report",
            styles['Title']
        )
    )

    elements.append(Spacer(1,20))

    elements.append(
        Paragraph(
            f"Candidate: {name}",
            styles['BodyText']
        )
    )

    elements.append(
        Paragraph(
            f"ATS Score: {score}%",
            styles['BodyText']
        )
    )

    doc.build(elements)

    return send_file(
        filepath,
        as_attachment=True
    )

# =========================================
# CHATBOT
# =========================================

@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():

    response = ""

    if request.method == "POST":

        user_message = request.form["message"]

        if "skills" in user_message.lower():

            response = (
                "Top skills are Python, ML and SQL."
            )

        elif "resume" in user_message.lower():

            response = (
                "Use ATS friendly keywords."
            )

        else:

            response = (
                "IntelliHire AI Assistant ready."
            )

    return render_template(
        "chatbot.html",
        response=response
    )

# =========================================
# API
# =========================================

@app.route("/api/leaderboard")
def leaderboard_api():

    data = Screening.query.order_by(
        Screening.ats_score.desc()
    ).all()

    leaderboard = []

    for d in data:

        leaderboard.append({

            "candidate": d.candidate_name,
            "score": d.ats_score,
            "status": d.status
        })

    return jsonify(leaderboard)

# =========================================
# DATABASE CREATE
# =========================================

with app.app_context():

    db.create_all()

# =========================================
# RUN APP
# =========================================
@app.route("/delete/<int:id>")
@login_required
def delete_candidate(id):

    candidate = Screening.query.get(id)

    db.session.delete(candidate)

    db.session.commit()

    flash("Candidate Deleted")

    return redirect(url_for("admin"))
@app.route("/download_analytics")
@login_required
def download_analytics():

    filepath = "reports/analytics.pdf"

    doc = SimpleDocTemplate(filepath)

    elements = []

    data = [

        ["Metric", "Value"],

        ["Total Resumes", len(df)],

        ["Categories", df['Category'].nunique()]

    ]

    table = Table(data)

    elements.append(table)

    doc.build(elements)

    return send_file(
        filepath,
        as_attachment=True
    )
# =========================================
# PROFILE IMAGE UPLOAD
# =========================================

@app.route("/upload_profile", methods=["POST"])
@login_required
def upload_profile():

    file = request.files["profile"]

    if file:

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            "static/profile",
            filename
        )

        file.save(filepath)

        current_user.profile_image = filename

        db.session.commit()

    return redirect(url_for("profile"))

if __name__ == "__main__":

    app.run(debug=True)