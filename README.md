# InsureSmart AI Insurance Recommendation Platform

InsureSmart is a generative AI-powered insurance analysis and planning application built using **Flask**, **SQLite**, and **Google Gemini AI**. It calculates personalized risk indexes, models premium ranges, matches candidates with custom insurance coverage plans (Term Life, Health, and Critical Illness), and offers tailored financial liquidity advice.

The application features a premium, responsive glassmorphism dark-theme dashboard with custom SVG gauge animations, detailed policy breakdown cards, search-enabled history log management, and robust error handles (including a smart mathematical mock actuary fallback in case of rate limits or missing API keys).

---

## Technical Stack
- **Backend Framework:** Flask (Python 3.13+)
- **Database ORM:** Flask-SQLAlchemy (SQLite)
- **AI Integration:** Google Gemini SDK (`gemini-2.5-flash` model with Structured JSON outputs)
- **Design System:** Custom Vanilla CSS (Frosted Glassmorphism, Neon gradients, Plus Jakarta Sans typography)
- **Testing Engine:** Pytest (Unit & Integration tests)

---

## Project Structure
```text
smart_insure/
├── .env                  # Local configurations & Gemini API Key
├── .env.example          # Template environment configurations
├── app.py                # Server configuration, routing rules, validations
├── models.py             # SQLAlchemy UserRecommendation schema & SQLite models
├── ai_engine.py          # Gemini AI API wrapper & Actuary fallback generators
├── requirements.txt      # Dependency package definitions
├── README.md             # Running & testing documentation
├── static/
│   ├── css/
│   │   └── style.css     # Global glassmorphism, responsive colors, & dashboard gauges
│   └── js/
│       └── main.js       # Form wizards validation & gauge count animations
├── templates/
│   ├── base.html         # Floating alert structures & navbar layout
│   ├── index.html        # Landing page with interactive preview elements
│   ├── assess.html       # Multi-step demographics, health, & preference wizard
│   ├── dashboard.html    # Detailed circular progress, comparisons, & insights reports
│   └── history.html      # Hub table for browsing, searching, and deleting past records
└── tests/
    ├── test_ai_engine.py  # AI response models & fallback mock assertions
    ├── test_app_routes.py # Flask integration test clients (get/posts/db commits)
    └── test_validation.py # Demographics, age, income boundary test assertions
```

---

## Setup & Running Instructions

### 1. Extract Workspace & Set up virtual environment
Open a terminal in the `smart_insure` workspace and create a virtual environment:
```powershell
# Create venv
py -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables (`.env`)
To run using Google Gemini AI, generate an API key from [Google AI Studio](https://aistudio.google.com/) and paste it in the `.env` file:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET_KEY=some-random-secret-key
FLASK_DEBUG=True
DATABASE_URL=sqlite:///insuresmart.db
```
*Note: If no API key is specified, the application will automatically fall back to its internal actuarial engine, calculating and simulating risk scores and plans natively.*

### 4. Run the Dev Server
```powershell
py app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser to explore.

### 5. Running the Test Suite
Ensure that core logic and integration pipelines are intact:
```powershell
pytest
```
*You should see 13 tests passing successfully!*
