# 🤖 AI Interview System

An AI-powered interview preparation system that helps users practice interviews, answer questions, and improve their interview skills using artificial intelligence.

## 🚀 Features

* AI-based interview questions
* Interactive interview practice
* Job-role-based interview preparation
* Python Developer and AI/ML Engineer interview support
* Speech input for answering questions
* Candidate response analysis
* Simple and user-friendly interface
* Interview feedback and suggestions

## 🛠️ Technologies Used

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **SpeechRecognition**
* **PyAudio**
* **Librosa**
* **SoundFile**
* **Google Generative AI**
* **python-dotenv**

## 📁 Project Structure

```text
AI_Interview/
│
├── app.py
├── app2.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI_Interview.git
cd AI_Interview
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```powershell
venv\Scripts\activate
```

### 4. Install the required packages

```powershell
pip install -r requirements.txt
```

## 🔑 Environment Variables

If the project uses an API key, create a `.env` file in the project folder:

```text
API_KEY=your_api_key_here
```

**Do not upload the `.env` file to GitHub.**

Make sure `.gitignore` contains:

```text
venv/
.env
__pycache__/
*.pyc
```

## ▶️ Run the Application

Run the Streamlit application using:

```powershell
python -m streamlit run app.py
```

The application will open in your web browser.

## 🔄 How It Works

1. The user selects a job role.
2. The system generates relevant interview questions.
3. The user answers the questions.
4. The system processes the user's response.
5. AI analyzes the response.
6. The system provides feedback and suggestions.
7. The user can continue practicing with additional questions.

## 🎯 Supported Interview Roles

The system can be used for different technical roles, such as:

* Python Developer
* AI/ML Engineer
* Data Analyst
* Software Developer
* Other customized j
