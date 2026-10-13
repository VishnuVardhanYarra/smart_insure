# InsureSmart AI Insurance Recommendation & Real-Time Carrier Engine

**Live Local Application:** [http://127.0.0.1:5000](http://127.0.0.1:5000)

InsureSmart is a generative AI-powered insurance analysis, carrier quotation, and financial planning platform built using **Flask**, **SQLite**, **Google Gemini AI**, and a **Real-Time Indian Insurance Carrier API Engine**. It calculates personalized risk indexes, queries live underwriting rates, models 18% GST tax breakdowns, executes digital policy proposal bindings, and offers tailored financial liquidity advice.

The application features a premium, responsive glassmorphism dark-theme dashboard with custom SVG gauge animations, detailed policy breakdown cards, downloadable PDF report generation, secure user authentication with session isolation, and robust fallback error handling (including a native mathematical actuary fallback in case of rate limits or missing API keys).

---

## Key Features

1. **🤖 Google Gemini Generative AI Actuary:** Analyzes candidate demographics, health conditions, and lifestyle habits using `gemini-2.5-flash` with structured JSON output enforcement.
2. **🏬 Real-Time Carrier API & Proposal Binding Engine:** Queries live underwriting rates from top Indian insurers (HDFC Life, Star Health, ICICI Lombard, Niva Bupa, Max Life), calculates statutory 18% GST, rider add-ons, and executes digital policy proposals (`/api/bind_proposal`).
3. **🔒 User Authentication & Strict Data Isolation:** Features secure user registration, password hashing (`werkzeug.security`), session login/logout, and strict user-isolated assessment histories (User A cannot view User B's records).
4. **📄 Single-Click PDF Report Export:** Print CSS ruleset (`@media print`) that formats the dark-mode dashboard into a clean, high-contrast, professional A4 printable PDF report.
5. **🛡️ Dual-Mode Native Fallback:** If Gemini API keys are missing or offline, the app seamlessly activates an internal mathematical actuarial engine without failing.
6. **📊 Financial Liquidity & Debt-to-Income Insights:** Evaluates premium-to-income ratios against 5-10% personal finance standards, suggests 6-month emergency corpus allocations, and highlights premium savings tips.

---

## Technical Stack
- **Backend Framework:** Flask (Python 3.13+)
- **Database ORM:** Flask-SQLAlchemy (SQLite)
- **Security & Auth:** Werkzeug Security (Password Hashing) & Flask Session Management
- **AI Integration:** Google Gemini SDK (`gemini-2.5-flash` with Structured JSON outputs)
- **Carrier Engine:** Real-Time Indian Insurer Quote Calculation & Proposal Binding (`carrier_api.py`)
- **Design System:** Custom Vanilla CSS (Frosted Glassmorphism, Neon gradients, Plus Jakarta Sans typography, Print CSS)
- **Testing Engine:** Pytest (18 Unit, Integration, Auth, & Carrier API tests)

---

## Project Structure
```text
smart_insure/
├── .env                  # Local configurations & Gemini API Key
├── .env.example          # Template environment configurations
├── app.py                # Flask routes, auth endpoints, validations, REST APIs
├── models.py             # User & UserRecommendation SQLAlchemy database schemas
├── ai_engine.py          # Gemini AI API wrapper & Actuary fallback generator
├── carrier_api.py        # Real-time carrier quote calculation & proposal binding engine
├── requirements.txt      # Dependency package definitions
├── README.md             # Running & testing documentation
├── PROJECT_DOCUMENTATION.md # 7-phase software engineering documentation
├── static/
│   ├── css/
│   │   └── style.css     # Global glassmorphism, gauges, responsive & print CSS
│   └── js/
│       └── main.js       # Form wizard validation & SVG gauge count animations
├── templates/
│   ├── base.html         # Floating alert toasts & responsive navigation bar
│   ├── index.html        # Landing page with interactive preview elements
│   ├── assess.html       # Multi-step demographics, health, & preference wizard
│   ├── dashboard.html    # Visual risk gauge, real-time quotes, proposal modal, & PDF export
│   ├── history.html      # Isolated user assessment history search hub
│   ├── login.html        # User login portal
│   └── register.html     # User registration portal
└── tests/
    ├── test_ai_engine.py  # AI response models & fallback mock assertions
    ├── test_app_routes.py # Flask integration test clients (GET/POST/DB commits)
    ├── test_carrier_api.py # Real-time carrier quotes & binding API tests
    ├── test_user_auth.py   # User registration, login, logout, & history isolation tests
    └── test_validation.py # Demographics, age, income boundary test assertions
```

---

## Setup & Running Instructions

### 1. Set up Virtual Environment
Open a terminal in the `smart_insure` workspace:
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
Create a `.env` file from `.env.example`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET_KEY=some-random-secret-key
FLASK_DEBUG=True
DATABASE_URL=sqlite:///insuresmart.db
```
*Note: If no API key is specified, the application will automatically fall back to its internal actuarial engine, calculating risk scores and plans natively.*

### 4. Run the Server
```powershell
py app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

### 5. Run Test Suite
To verify core logic, carrier engine, user auth, health check, and route integration:
```powershell
pytest
```
*All 19 tests will pass successfully!*

---

## Deployment Guide (GitHub & Render)

### Step 1: Push Project to GitHub

1. Ensure sensitive files (`.env`, `*.db`, caches) are ignored via `.gitignore` (already configured).
2. Stage and commit your changes:
   ```bash
   git add .
   git commit -m "Prepare repository for Render deployment"
   ```
3. Push to your repository:
   ```bash
   git push origin main
   ```

---

### Step 2: Deploy to Render (Render.com)

You can deploy on Render in one of two easy ways:

#### Option A: Quick Blueprint Deploy (Recommended)
Because the repository includes `render.yaml`, Render can configure the service automatically:
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository (`smart_insure`).
4. Enter your `GEMINI_API_KEY` when prompted.
5. Click **Apply**. Render will automatically build and deploy your app.

#### Option B: Manual Web Service Deploy
1. In [Render Dashboard](https://dashboard.render.com/), click **New +** > **Web Service**.
2. Connect your GitHub repository (`smart_insure`).
3. Set the following configuration settings:
   - **Name:** `smart-insure` (or your preferred name)
   - **Region:** Any region close to your users (e.g., Singapore or Oregon)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = your Google AI Studio API key
   - `FLASK_SECRET_KEY` = (generate a random string or click generate)
   - `FLASK_DEBUG` = `False`
   - `PYTHON_VERSION` = `3.11.9`
5. (Optional) Set the **Health Check Path** to `/health`.
6. Click **Deploy Web Service**.
7. Once deployed, Render will provide a free live URL (e.g., `https://smart-insure-xxxx.onrender.com`).

