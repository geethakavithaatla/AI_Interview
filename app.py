import re
import io
import streamlit as st
import pandas as pd

from pypdf import PdfReader
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Interview System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #1f2937, #374151);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #e5e7eb;
}

.metric-number {
    font-size: 30px;
    font-weight: bold;
}

.metric-label {
    color: #6b7280;
    font-size: 14px;
}

.question-card {
    background: white;
    padding: 28px;
    border-radius: 18px;
    border-left: 6px solid #4f46e5;
    box-shadow: 0 5px 18px rgba(0,0,0,0.07);
    margin: 20px 0;
}

.success-card {
    background: #ecfdf5;
    border-left: 5px solid #10b981;
    padding: 18px;
    border-radius: 12px;
}

.warning-card {
    background: #fff7ed;
    border-left: 5px solid #f97316;
    padding: 18px;
    border-radius: 12px;
}

.progress-text {
    text-align: center;
    color: #6b7280;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "stage": 1,
    "resume_text": "",
    "resume_name": "",
    "job_description": "",
    "role": "",
    "skills": [],
    "missing_skills": [],
    "match_score": 0,
    "interview_type": "Mixed",
    "difficulty": "Beginner",
    "questions": [],
    "answers": [],
    "scores": [],
    "feedback": [],
    "current_question": 0,
    "interview_completed": False,
    "analysis_completed": False
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# SKILL DATABASE
# =========================================================

SKILLS = [
    "python",
    "c",
    "c++",
    "java",
    "sql",
    "mysql",
    "mongodb",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "django",
    "flask",
    "streamlit",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "llm",
    "rag",
    "generative ai",
    "nlp",
    "git",
    "github",
    "docker",
    "aws",
    "communication",
    "leadership",
    "teamwork",
    "problem solving"
]


# =========================================================
# TEXT FUNCTIONS
# =========================================================

def clean_text(text):

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):

    text = clean_text(text)

    found = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):

            found.append(skill)

    return sorted(set(found))


# =========================================================
# RESUME EXTRACTION
# =========================================================

def extract_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text


def extract_docx(file):

    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text


def extract_resume(file):

    if file is None:

        return ""

    if file.name.lower().endswith(".pdf"):

        return extract_pdf(file)

    if file.name.lower().endswith(".docx"):

        return extract_docx(file)

    return ""


# =========================================================
# MATCHING
# =========================================================

def calculate_match(resume_text, job_description):

    if not resume_text or not job_description:

        return 0

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(
        [resume_text, job_description]
    )

    score = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(score * 100, 2)


def find_missing_skills(resume_skills, job_description):

    required = extract_skills(job_description)

    missing = [
        skill for skill in required
        if skill not in resume_skills
    ]

    return missing


# =========================================================
# QUESTION GENERATOR
# =========================================================

def generate_questions(role, interview_type, difficulty, skills):

    questions = []

    if interview_type in ["Technical", "Mixed"]:

        for skill in skills[:5]:

            questions.append(
                f"Explain your understanding of {skill} "
                f"and how you have used it in a project."
            )

        questions.extend([
            f"What are the important concepts you should know "
            f"for a {role} position?",
            
            "Explain one technical project you have worked on.",
            
            "How do you debug a program when it is not working?"
        ])

    if interview_type in ["HR", "Mixed"]:

        questions.extend([
            "Tell me about yourself.",
            "Why are you interested in this role?",
            "Why should we hire you?",
            "What are your strengths and weaknesses?"
        ])

    if interview_type in ["Behavioral", "Mixed"]:

        questions.extend([
            "Tell me about a difficult problem you solved.",
            "Describe a situation where you worked in a team.",
            "How do you handle deadlines and pressure?"
        ])

    return questions[:10]


# =========================================================
# ANSWER EVALUATION
# =========================================================

def evaluate_answer(answer):

    if not answer.strip():

        return 0, "No answer was provided."

    words = answer.split()

    score = min(100, len(words) * 2)

    if len(words) < 20:

        feedback = "Try to provide a more detailed answer with an example."

    elif len(words) < 50:

        feedback = "Good answer. Add more technical details or examples."

    else:

        feedback = "Strong and detailed answer."

    return score, feedback


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>🎯 AI Interview System</h1>

<p>
AI-powered resume analysis, skill matching and personalized mock interviews
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# PROGRESS
# =========================================================

stages = [
    "Resume Upload",
    "Resume Analysis",
    "Job Matching",
    "Interview Setup",
    "Mock Interview",
    "Final Report"
]

current_stage = min(
    st.session_state.stage,
    len(stages)
)

st.progress(
    current_stage / len(stages)
)

st.markdown(
    f"""
    <div class="progress-text">
    Step {current_stage} of {len(stages)}
    — {stages[current_stage - 1]}
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# STAGE 1 — RESUME UPLOAD
# =========================================================

if st.session_state.stage == 1:

    st.header("📄 Upload Your Resume")

    st.write(
        "Upload your resume to begin the AI interview process."
    )

    uploaded_file = st.file_uploader(
        "Choose Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file:

        with st.spinner("Analyzing your resume..."):

            resume_text = extract_resume(uploaded_file)
            st.write("File:", uploaded_file.name)
            st.write("Extracted characters:", len(resume_text))

        if resume_text.strip():

            st.session_state.resume_text = resume_text

            st.session_state.resume_name = uploaded_file.name
            st.success("✅ Resume text extracted successfully!")
            st.session_state.stage = 2

          

            st.rerun()

        else:
            st.error("❌ No text could be extracted from this resume.")
            st.info(
                "The PDF may be scanned/image-based, or OCR configuration may be missing."
                )


# =========================================================
# STAGE 2 — RESUME ANALYSIS
# =========================================================

elif st.session_state.stage == 2:

    st.header("🔍 Resume Analysis")

    resume_skills = extract_skills(
        st.session_state.resume_text
    )

    st.session_state.skills = resume_skills

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">
            {len(resume_skills)}
            </div>
            <div class="metric-label">
            Skills Detected
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">
            {len(st.session_state.resume_text.split())}
            </div>
            <div class="metric-label">
            Words
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">
            ✓
            </div>
            <div class="metric-label">
            Resume Processed
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("💡 Detected Skills")

    if resume_skills:

        st.success(
            ", ".join(resume_skills)
        )

    else:

        st.warning(
            "No predefined skills detected."
        )

    st.session_state.stage = 3

    st.rerun()


# =========================================================
# STAGE 3 — JOB MATCHING
# =========================================================

elif st.session_state.stage == 3:

    st.header("💼 Job & Career Matching")

    role = st.text_input(
        "Target Job Role",
        placeholder="Example: AI Intern"
    )

    job_description = st.text_area(
        "Job Description",
        height=220,
        placeholder="Paste the job description here..."
    )

    if st.button(
        "Analyze Job & Continue →",
        use_container_width=True
    ):

        if not role:

            st.error(
                "Please enter a target job role."
            )

        else:

            st.session_state.role = role

            st.session_state.job_description = job_description

            st.session_state.match_score = calculate_match(
                st.session_state.resume_text,
                job_description
            )

            st.session_state.missing_skills = find_missing_skills(
                st.session_state.skills,
                job_description
            )

            st.session_state.stage = 4

            st.rerun()


# =========================================================
# STAGE 4 — INTERVIEW SETUP
# =========================================================

elif st.session_state.stage == 4:

    st.header("⚙️ Interview Configuration")

    col1, col2 = st.columns(2)

    with col1:

        interview_type = st.selectbox(
            "Interview Type",
            [
                "Mixed",
                "Technical",
                "HR",
                "Behavioral"
            ]
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Beginner",
                "Intermediate",
                "Advanced"
            ]
        )

    st.info(
        f"Target Role: {st.session_state.role}"
    )

    if st.button(
        "🚀 Start AI Interview",
        use_container_width=True
    ):

        st.session_state.interview_type = interview_type

        st.session_state.difficulty = difficulty

        st.session_state.questions = generate_questions(
            st.session_state.role,
            interview_type,
            difficulty,
            st.session_state.skills
        )

        st.session_state.current_question = 0

        st.session_state.answers = []

        st.session_state.scores = []

        st.session_state.feedback = []

        st.session_state.stage = 5

        st.rerun()


# =========================================================
# STAGE 5 — MOCK INTERVIEW
# =========================================================

elif st.session_state.stage == 5:

    st.header("🎤 AI Mock Interview")

    total_questions = len(
        st.session_state.questions
    )

    current = st.session_state.current_question

    if current < total_questions:

        st.progress(
            (current + 1) / total_questions
        )

        st.markdown(
            f"""
            <div class="question-card">

            <h2>
            Question {current + 1} of {total_questions}
            </h2>

            <h3>
            {st.session_state.questions[current]}
            </h3>

            </div>
            """,
            unsafe_allow_html=True
        )

        answer = st.text_area(
            "Your Answer",
            height=180,
            key=f"answer_{current}"
        )

        if st.button(
            "Submit Answer & Next →",
            use_container_width=True
        ):

            if not answer.strip():

                st.warning(
                    "Please enter your answer."
                )

            else:

                score, feedback = evaluate_answer(
                    answer
                )

                st.session_state.answers.append(
                    answer
                )

                st.session_state.scores.append(
                    score
                )

                st.session_state.feedback.append(
                    feedback
                )

                st.session_state.current_question += 1

                # AUTOMATICALLY MOVE TO NEXT QUESTION

                if (
                    st.session_state.current_question
                    >= total_questions
                ):

                    st.session_state.interview_completed = True

                    st.session_state.stage = 6

                st.rerun()


# =========================================================
# STAGE 6 — FINAL REPORT
# =========================================================

elif st.session_state.stage == 6:

    st.header("📊 Final Interview Report")

    scores = st.session_state.scores

    if scores:

        overall_score = round(
            sum(scores) / len(scores),
            2
        )

    else:

        overall_score = 0

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Overall Score",
            f"{overall_score}%"
        )

    with col2:

        st.metric(
            "Questions",
            len(st.session_state.questions)
        )

    with col3:

        st.metric(
            "Skills Detected",
            len(st.session_state.skills)
        )

    st.divider()

    st.subheader("🎯 Performance")

    if overall_score >= 80:

        st.success(
            "Excellent performance! You are well prepared."
        )

    elif overall_score >= 60:

        st.info(
            "Good performance. Continue improving your answers."
        )

    else:

        st.warning(
            "More preparation is recommended before the interview."
        )

    st.subheader("💪 Strengths")

    st.write(
        "• Good participation in the interview"
    )

    st.write(
        "• Demonstrated knowledge of relevant concepts"
    )

    st.write(
        "• Completed all interview questions"
    )

    st.subheader("📚 Skills to Improve")

    if st.session_state.missing_skills:

        st.warning(
            ", ".join(
                st.session_state.missing_skills
            )
        )

    else:

        st.success(
            "No major missing skills detected."
        )

    st.subheader("💡 Recommendations")

    st.write(
        "• Practice explaining technical concepts clearly."
    )

    st.write(
        "• Work on practical projects related to your target role."
    )

    st.write(
        "• Practice HR and behavioral interview questions."
    )

    st.write(
        "• Improve answers by including real project examples."
    )

    st.divider()

    report = pd.DataFrame({
        "Question": st.session_state.questions,
        "Answer": st.session_state.answers,
        "Score": st.session_state.scores,
        "Feedback": st.session_state.feedback
    })

    st.subheader("📝 Detailed Results")

    st.dataframe(
        report,
        use_container_width=True
    )

    csv = report.to_csv(
        index=False
    )

    st.download_button(
        "⬇️ Download Interview Report",
        csv,
        "AI_Interview_Report.csv",
        "text/csv",
        use_container_width=True
    )