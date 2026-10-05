import os
import re
import streamlit as st
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from google import genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Interview System",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 AI Interview System")
st.write("Practice interviews with an AI interviewer.")

# -----------------------------
# Gemini AI
# -----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None


# -----------------------------
# Session State
# -----------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "current" not in st.session_state:
    st.session_state.current = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "started" not in st.session_state:
    st.session_state.started = False


# -----------------------------
# Skill Extraction
# -----------------------------
def extract_skills(text):

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Data Science",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "Natural Language Processing",
        "Streamlit",
        "Git",
        "GitHub",
        "Django",
        "Flask",
        "MongoDB",
        "MySQL",
        "PostgreSQL",
        "AWS",
        "Docker"
    ]

    found = []

    for skill in skills:
        if re.search(
            r"\b" + re.escape(skill) + r"\b",
            text,
            re.IGNORECASE
        ):
            found.append(skill)

    return found


# -----------------------------
# Generate AI Questions
# -----------------------------
def generate_questions(role, description, skills, count):

    if client:

        prompt = f"""
You are an AI technical interviewer.

Job Role:
{role}

Job Description:
{description}

Required Skills:
{", ".join(skills)}

Generate exactly {count} interview questions.

Requirements:
- Suitable for a CSE student
- Mix technical and practical questions
- Focus on the job description
- Do not provide answers
- Number each question
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text

            questions = []

            for line in text.split("\n"):
                line = re.sub(
                    r"^\s*\d+[\.\)\-]\s*",
                    "",
                    line
                ).strip()

                if len(line) > 10:
                    questions.append(line)

            return questions[:count]

        except Exception:
            pass

    questions = []

    if skills:

        for skill in skills:

            questions.append(
                f"What is {skill} and how is it used in real-world applications?"
            )

            if len(questions) >= count:
                break

    default_questions = [
        "Tell me about yourself.",
        "Why are you interested in this role?",
        "Explain one technical project you have worked on.",
        "What are your strengths as a CSE student?",
        "What is your approach to solving a programming problem?",
        "How do you debug an error in your program?",
        "Where do you see yourself in the next three years?"
    ]

    for question in default_questions:

        if len(questions) >= count:
            break

        questions.append(question)

    return questions[:count]


# -----------------------------
# AI Answer Evaluation
# -----------------------------
def evaluate_answer(question, answer):

    if client:

        prompt = f"""
You are an experienced technical interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate answer.

Give:
Score: X/10
Feedback: short constructive feedback
Improvement: one specific improvement

Keep the response concise.
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text

            match = re.search(
                r"Score:\s*(\d+)",
                result,
                re.IGNORECASE
            )

            if match:
                score = int(match.group(1))
                score = max(0, min(score, 10))
            else:
                score = 5

            return score, result

        except Exception:
            pass

    words = answer.split()

    if len(words) >= 50:
        score = 9
    elif len(words) >= 30:
        score = 8
    elif len(words) >= 20:
        score = 7
    elif len(words) >= 10:
        score = 5
    else:
        score = 3

    feedback = (
        f"Score: {score}/10\n\n"
        "Feedback: Try to provide a clear and detailed answer.\n\n"
        "Improvement: Include a practical example."
    )

    return score, feedback


# -----------------------------
# Speech Recognition
# -----------------------------
def get_voice_answer():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            st.info("🎤 Listening... Speak now.")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=60
            )

        text = recognizer.recognize_google(audio)

        return text

    except sr.WaitTimeoutError:

        return "No speech detected."

    except sr.UnknownValueError:

        return "Could not understand your voice."

    except sr.RequestError:

        return "Speech recognition service is unavailable."

    except Exception as e:

        return f"Microphone error: {e}"


# -----------------------------
# Text To Speech
# -----------------------------
def speak_question(text):

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            150
        )

        engine.say(text)

        engine.runAndWait()

        engine.stop()

    except Exception:

        try:

            filename = "question.mp3"

            speech = gTTS(
                text=text,
                lang="en"
            )

            speech.save(filename)

            audio_file = open(
                filename,
                "rb"
            )

            st.audio(
                audio_file.read(),
                format="audio/mp3"
            )

        except Exception:
            pass


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Interview Settings")

candidate_name = st.sidebar.text_input(
    "Candidate Name",
    "Geetha"
)

job_role = st.sidebar.text_input(
    "Job Role",
    "Python Developer"
)

question_count = st.sidebar.slider(
    "Number of Questions",
    3,
    10,
    5
)


# -----------------------------
# Job Description
# -----------------------------
st.subheader("📋 Job Description")

job_description = st.text_area(
    "Enter the job description",
    height=180,
    placeholder=(
        "Example: We are looking for a Python Developer "
        "with knowledge of Python, SQL, Machine Learning "
        "and Streamlit."
    )
)


# -----------------------------
# Extract Skills
# -----------------------------
if st.button("🔍 Extract Skills"):

    if job_description.strip():

        skills = extract_skills(
            job_description
        )

        if skills:

            st.success(
                "### 🧠 Extracted Skills"
            )

            st.write(
                ", ".join(skills)
            )

        else:

            st.warning(
                "No predefined skills detected."
            )

    else:

        st.warning(
            "Please enter a job description."
        )


# -----------------------------
# Start Interview
# -----------------------------
if st.button("🚀 Start Interview"):

    if not job_description.strip():

        st.error(
            "Please enter a job description."
        )

    else:

        skills = extract_skills(
            job_description
        )

        questions = generate_questions(
            job_role,
            job_description,
            skills,
            question_count
        )

        st.session_state.questions = questions

        st.session_state.current = 0

        st.session_state.answers = []

        st.session_state.scores = []

        st.session_state.feedback = []

        st.session_state.started = True

        st.rerun()


# -----------------------------
# Interview
# -----------------------------
if st.session_state.started:

    questions = st.session_state.questions

    current = st.session_state.current

    if current < len(questions):

        st.divider()

        st.subheader(
            f"Question {current + 1} of {len(questions)}"
        )

        question = questions[current]

        st.info(question)

        if st.button("🔊 Hear Question"):

            speak_question(question)

        st.subheader("✍️ Type Your Answer")

        answer = st.text_area(
            "Your Answer",
            height=180,
            key=f"answer_{current}"
        )

        st.write("OR")

        if st.button("🎤 Speak Answer"):

            voice_answer = get_voice_answer()

            st.session_state[
                f"voice_{current}"
            ] = voice_answer

            st.rerun()

        voice_answer = st.session_state.get(
            f"voice_{current}",
            ""
        )

        if voice_answer:

            st.subheader(
                "🎤 Recognized Answer"
            )

            st.write(
                voice_answer
            )

        if st.button("✅ Submit Answer"):

            final_answer = answer.strip()

            if not final_answer and voice_answer:

                final_answer = voice_answer

            if not final_answer:

                st.warning(
                    "Please type or speak an answer."
                )

            else:

                score, feedback = evaluate_answer(
                    question,
                    final_answer
                )

                st.session_state.answers.append(
                    final_answer
                )

                st.session_state.scores.append(
                    score
                )

                st.session_state.feedback.append(
                    feedback
                )

                st.success(
                    f"🎯 Score: {score}/10"
                )

                st.write(
                    feedback
                )

                if current + 1 < len(questions):

                    if st.button("➡️ Next Question"):

                        st.session_state.current += 1

                        st.rerun()

                else:

                    st.session_state.current += 1

                    st.rerun()


# -----------------------------
# Final Result
# -----------------------------
if (
    st.session_state.started
    and st.session_state.current >= len(
        st.session_state.questions
    )
):

    st.divider()

    st.header("🏆 Interview Result")

    scores = st.session_state.scores

    if scores:

        average = sum(scores) / len(scores)

        st.metric(
            "Overall Score",
            f"{average:.1f}/10"
        )

        if average >= 8:

            st.success(
                "Excellent performance! 🎉"
            )

        elif average >= 6:

            st.info(
                "Good performance! Keep practicing."
            )

        else:

            st.warning(
                "Keep practicing and improve your technical concepts."
            )

        st.subheader("📊 Question-wise Scores")

        for i, score in enumerate(scores):

            st.write(
                f"Question {i + 1}: {score}/10"
            )

        st.subheader("👤 Candidate Details")

        st.write(
            f"**Name:** {candidate_name}"
        )

        st.write(
            f"**Role:** {job_role}"
        )

        st.write(
            f"**Questions:** {len(scores)}"
        )

        st.write(
            f"**Average:** {average:.1f}/10"
        )

        st.subheader("💡 Feedback")

        for i, feedback in enumerate(
            st.session_state.feedback
        ):

            with st.expander(
                f"Question {i + 1} Feedback"
            ):

                st.write(feedback)

        if st.button("🔄 Start New Interview"):

            st.session_state.questions = []

            st.session_state.current = 0

            st.session_state.answers = []

            st.session_state.scores = []

            st.session_state.feedback = []

            st.session_state.started = False

            st.rerun()