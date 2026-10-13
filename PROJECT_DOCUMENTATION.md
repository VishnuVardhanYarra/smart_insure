# InsureSmart - Complete Project Documentation

This document outlines the complete lifecycle of the **InsureSmart** project, organized into seven standard software engineering phases.

---

## 1. Ideation Phase

### 1.1 Problem Statement Definition
The traditional insurance industry often suffers from opaque pricing, complex policy terms, and one-size-fits-all recommendations. Users struggle to calculate their true risk index based on their unique demographics, health data, and financial standing, leading to either under-insurance or over-paying for unnecessary coverage. 

### 1.2 Brainstorming & Idea Generation
To solve this, **InsureSmart** was conceived as a generative AI-powered insurance analysis, carrier quotation, and financial planning application. The core idea is to leverage **Google Gemini AI** alongside a **Real-Time Indian Insurance Carrier API Engine** to act as a personalized digital actuary. It takes user input through an intuitive, multi-step wizard, calculates risk indexes, queries live carrier rates with 18% GST tax breakdowns, executes digital policy proposal bindings, and offers tailored financial liquidity advice.

### 1.3 Empathy Map Canvas & Target Audience
- **Target Audience:** Young professionals, families, individuals with complex medical histories, and people looking for tailored, transparent insurance advice.
- **Needs:** Fast, unbiased insurance recommendations without speaking to high-pressure sales agents.
- **Pain Points:** Confusion over insurance terms, fear of hidden clauses, sales call spam from aggregators, and inability to calculate coverage needs based on income.

---

## 2. Requirement Analysis

### 2.1 Functional Requirements
- **User Assessment Form:** A multi-step wizard to collect demographic, health, financial, and lifestyle data.
- **AI Recommendation Engine:** Integration with `gemini-2.5-flash` to process user data and return structured JSON containing risk indexes and policy recommendations.
- **Real-Time Carrier Engine:** Query live rates from top Indian underwriters (HDFC Life, Star Health, ICICI Lombard, Niva Bupa, Max Life), compute 18% GST, and issue digital policy proposal certificate IDs (`PROP-IRDAI-XXXXXXXX`).
- **User Authentication & Privacy:** Secure user registration, password hashing (`werkzeug.security`), login/logout session handling, and strict user-isolated history logs (User A cannot view User B's records).
- **Downloadable PDF Report Export:** Single-click print-optimized PDF generation on `/dashboard`.
- **Actuarial Fallback Mechanism:** A native mathematical fallback engine to calculate risk scores and plans if the AI API fails or rate limits.
- **Dashboard & Insights:** A detailed dashboard presenting circular progress gauges, real-time carrier quotes, proposal binding modals, and financial tips.

### 2.2 Non-Functional Requirements
- **Performance:** Fast response times (< 2 seconds) for AI generation, carrier queries, and database operations.
- **UI/UX:** A premium, responsive "glassmorphism" dark theme with dynamic SVG animations and dedicated print media stylesheets (`@media print`).
- **Data Privacy & Security:** Strict session-based access control and password hashing.
- **Reliability:** Graceful error handling for missing API keys or external server downtime via internal mathematical fallbacks.
- **Maintainability:** Modular code structure separating routing (`app.py`), carrier logic (`carrier_api.py`), AI logic (`ai_engine.py`), and ORM models (`models.py`).

---

## 3. Project Design Phase

### 3.1 System Architecture
The system uses a monolithic architecture built on **Flask (Python 3.13+)**:
- **Frontend Layer:** Jinja2 templates (`templates/`) styled with Vanilla CSS (`static/css/style.css`) and vanilla JavaScript for interactivity (`static/js/main.js`).
- **Backend Application Core:** Flask routing, user authentication, session security, and validation logic (`app.py`).
- **Carrier API Service Layer:** `carrier_api.py` managing real-time rate queries from Indian underwriters, 18% GST tax calculations, and IRDAI digital proposal bindings.
- **AI Service Layer:** `ai_engine.py` wrapper for the Google Gemini SDK with structured JSON enforcement.
- **Database Layer:** SQLAlchemy ORM managing SQLite (`insuresmart.db`).

### 3.2 Database Schemas (`models.py`)

#### 1. `User` Schema
- `id` (Integer, Primary Key)
- `username` (String(80), Unique, Not Null)
- `email` (String(120), Unique, Not Null)
- `password_hash` (String(255), Not Null)
- `created_at` (DateTime, Timezone UTC)

#### 2. `UserRecommendation` Schema
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key `users.id`, Nullable for guest support)
- `name`, `age`, `gender`, `annual_income`, `dependents` (Candidate inputs)
- `health_conditions`, `lifestyle_habits`, `insurance_preferences` (Text fields)
- `risk_score` (Integer 0-100)
- `risk_factors_raw` (JSON Array string)
- `premium_estimates_raw` (JSON Object string)
- `recommended_plans_raw` (JSON Array string)
- `financial_insights_raw` (JSON Object string)
- `created_at` (DateTime, Timezone UTC)

---

## 4. Project Planning Phase

### 4.1 Tech Stack Justification
- **Flask:** Lightweight, flexible, and ideal for prototyping Python AI and RESTful web applications.
- **SQLite & SQLAlchemy:** Zero-config relational database for local history logging and easy deployment.
- **Google Gemini (2.5 Flash):** Fast, structured JSON generation for rendering UI dashboards from LLM outputs.
- **Carrier Rating Engine:** Custom RESTful rating models simulating Indian market rate cards with 18% statutory GST.
- **Vanilla CSS/JS:** Zero build-tool overhead (no Webpack/Vite required), ensuring rapid execution and easy maintenance.

---

## 5. Project Development Phase

### 5.1 Implementation Details
- **Routing & Auth (`app.py`):** Routes for `/`, `/assess`, `/dashboard/<id>`, `/history`, `/register`, `/login`, `/logout`, `/api/bind_proposal`, `/api/recommendation/<id>`, and `/api/delete/<id>`.
- **Carrier Engine (`carrier_api.py`):** Real-time rate cards, 18% GST tax calculations, and IRDAI proposal binding certificate generator.
- **User Privacy Guard:** Route-level `user_id` checks preventing users from viewing or modifying other users' private assessment reports.
- **PDF Export CSS:** Dedicated `@media print` CSS block hiding navbars and buttons while turning dark glassmorphism into a clean, printable A4 document.

### 5.2 Testing Strategy
The project uses **Pytest** for a comprehensive testing suite located in `tests/` (**18 passing tests**):
- `test_ai_engine.py`: Asserts AI response schemas and fallback mock engine integrity.
- `test_app_routes.py`: Flask integration test clients for GET/POST requests and DB commits.
- `test_carrier_api.py`: Asserts real-time carrier quote calculations, GST tax math, and digital proposal binding.
- `test_user_auth.py`: Asserts user registration, login, logout, and strict user history privacy isolation.
- `test_validation.py`: Asserts boundary logic for demographics, age, income, and dependents.

---

## 6. Project Documentation

### 6.1 Setup Instructions
1. **Virtual Environment:** `py -m venv venv` and `.\venv\Scripts\Activate.ps1`
2. **Install Dependencies:** `pip install -r requirements.txt`
3. **Environment Variables:** Create `.env` file from `.env.example` with `GEMINI_API_KEY` and `FLASK_SECRET_KEY`.
4. **Run Server:** `py app.py`

### 6.2 API Reference
- `POST /api/bind_proposal`: Accepts `{"quote_id": "...", "candidate_name": "..."}` and returns a digital proposal certificate ID (`PROP-IRDAI-XXXXXXXX`).
- `GET /api/recommendation/<id>`: Returns a candidate's complete recommendation record as JSON (protected by user authorization).
- `POST /api/delete/<id>`: Deletes a user's recommendation record (protected by user ownership verification).

---

## 7. Project Demonstration

### 7.1 Walkthrough of User Journey
1. **Landing Page:** Interactive preview greeting users with platform value propositions.
2. **Authentication (`/register`, `/login`):** Users create an account or sign in to keep their insurance evaluations completely private.
3. **Assessment (`/assess`):** Users enter demographic, health, lifestyle, and preference data across a multi-step form wizard.
4. **Dashboard (`/dashboard`):** Displays SVG risk gauges, real-time carrier quotes from top Indian insurers with 18% GST breakdowns, a "Get Quote & Bind Proposal" action modal, and financial liquidity advice.
5. **PDF Export:** Single-click "Download PDF Report" generates a high-contrast printable document.
6. **History Hub (`/history`):** Allows logged-in users to search, browse, and manage their own private evaluation history.
