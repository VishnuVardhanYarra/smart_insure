# InsureSmart - Complete Project Documentation

This document outlines the complete lifecycle of the **InsureSmart** project, organized into seven standard software engineering phases.

---

## 1. Ideation Phase

### 1.1 Problem Statement Definition
The traditional insurance industry often suffers from opaque pricing, complex policy terms, and one-size-fits-all recommendations. Users struggle to calculate their true risk index based on their unique demographics, health data, and financial standing, leading to either under-insurance or over-paying for unnecessary coverage. 

### 1.2 Brainstorming & Idea Generation
To solve this, **InsureSmart** was conceived as a generative AI-powered insurance analysis and planning application. The core idea is to leverage **Google Gemini AI** to act as a personalized digital actuary. It takes user input through an intuitive, multi-step wizard and instantly calculates personalized risk indexes, models premium ranges, and matches candidates with optimal insurance coverage plans (Term Life, Health, and Critical Illness) alongside financial liquidity advice.

### 1.3 Empathy Map Canvas & Target Audience
- **Target Audience:** Young professionals, individuals with complex medical histories, and people looking for tailored, transparent insurance advice.
- **Needs:** Fast, unbiased insurance recommendations without speaking to high-pressure sales agents.
- **Pain Points:** Confusion over insurance terms, fear of hidden clauses, inability to manually calculate coverage needs based on income.

---

## 2. Requirement Analysis

### 2.1 Functional Requirements
- **User Assessment Form:** A multi-step wizard to collect demographic, health, financial, and lifestyle data.
- **AI Recommendation Engine:** Integration with `gemini-2.5-flash` to process user data and return structured JSON containing risk indexes and policy recommendations.
- **Actuarial Fallback Mechanism:** A native mathematical fallback engine to simulate risk scores and plans if the AI API fails or rate limits.
- **Dashboard & Insights:** A detailed dashboard presenting circular progress gauges, policy breakdowns, and financial tips.
- **History Management:** Ability to browse, search, and delete past insurance assessments via a SQLite database.

### 2.2 Non-Functional Requirements
- **Performance:** Fast response times (< 2 seconds) for AI generation and database queries.
- **UI/UX:** A premium, responsive "glassmorphism" dark theme with dynamic SVG animations.
- **Reliability:** Graceful error handling for missing API keys or external server downtime.
- **Maintainability:** Modular code structure separating routing (`app.py`), AI logic (`ai_engine.py`), and models (`models.py`).

---

## 3. Project Design Phase

### 3.1 System Architecture
The system uses a monolithic architecture built on **Flask (Python)**:
- **Frontend:** Jinja2 templates (`templates/`) styled with Vanilla CSS (`static/css/style.css`) and vanilla JavaScript for interactivity (`static/js/main.js`).
- **Backend Core:** Flask routing and validation logic (`app.py`).
- **AI Service Layer:** `ai_engine.py` wrapper for the Google Gemini SDK, which maps data to the prompt and parses the JSON response.
- **Database Layer:** SQLAlchemy ORM managing SQLite (`insuresmart.db`).

### 3.2 UI/UX Design System
- **Theme:** Frosted Glassmorphism, Neon gradients, dark backgrounds.
- **Typography:** Plus Jakarta Sans.
- **Key Components:** Floating alert structures, SVG gauge count animations, multi-step form wizards, and detailed breakdown cards.

### 3.3 Database Schema (UserRecommendation Model)
- `id` (Integer, Primary Key)
- `name`, `age`, `income`, `dependents`, `health_status`, `smoker` (User inputs)
- `risk_score` (Integer 0-100)
- `recommended_plans` (JSON string storing Life, Health, Critical details)
- `financial_advice` (Text)
- `created_at` (Timestamp)

---

## 4. Project Planning Phase

### 4.1 Tech Stack Justification
- **Flask:** Lightweight, highly customizable, and perfect for rapidly prototyping Python AI applications.
- **SQLite:** Requires no external server setup, perfect for local history logging and easy deployment.
- **Google Gemini (2.5 Flash):** Offers fast, affordable structured JSON generation which is crucial for creating structured UI dashboards from LLM outputs.
- **Vanilla CSS/JS:** Keeps the frontend lightweight and removes the need for complex build tools (like Webpack or Vite), ensuring the project is easy to run and modify.

### 4.2 Milestones & Deliverables
1. Initial UI mockups and CSS Glassmorphism design system.
2. Flask routing and SQLite database setup.
3. Gemini AI integration and prompt engineering for structured outputs.
4. Fallback Actuary Engine development.
5. Pytest integration and QA.

---

## 5. Project Development Phase

### 5.1 Implementation Details
- **Routing Rules (`app.py`):** RESTful routes for `/`, `/assess` (GET/POST), `/dashboard/<id>`, and `/history`.
- **AI Engine (`ai_engine.py`):** Centralizes the AI logic. The fallback system uses Python's `random` and mathematical weighting to generate realistic fallback data if Gemini is unavailable.
- **Frontend Interactivity:** JavaScript is used in `main.js` to handle the multi-step form validation, smoothly transitioning between steps without page reloads, and animating the SVG gauges on the dashboard on load.

### 5.2 Testing Strategy
The project uses **Pytest** for a comprehensive testing suite located in `tests/`:
- `test_ai_engine.py`: Asserts that AI response models and the fallback mock engine return the correct data structures.
- `test_app_routes.py`: Flask integration test clients to test GET/POST requests and DB commits.
- `test_validation.py`: Asserts boundary logic for demographics, age, and income.

---

## 6. Project Documentation

### 6.1 Setup Instructions
1. **Virtual Environment:** `py -m venv venv` and `.\venv\Scripts\Activate.ps1`
2. **Install Dependencies:** `pip install -r requirements.txt`
3. **Environment Variables:** Create a `.env` file from `.env.example` and add `GEMINI_API_KEY`.
4. **Run Server:** `py app.py`

### 6.2 API & Internal Engine Reference
- `generate_recommendation(user_data)`: Takes a dictionary of user demographics and returns a parsed JSON dictionary with keys `risk_score`, `plans`, and `financial_advice`.
- `_fallback_actuary(user_data)`: Native Python fallback generator used when `GEMINI_API_KEY` is missing or fails.

---

## 7. Project Demonstration

### 7.1 Walkthrough of User Journey
1. **Landing Page:** The user is greeted by a high-end, animated landing page that explains the value proposition.
2. **Assessment (`/assess`):** The user enters their name, age, dependents, income, health status, and smoking habits across a sleek, multi-step form.
3. **Dashboard (`/dashboard`):** The system processes the data instantly and displays a circular `risk_score` gauge. Below, it breaks down the recommended Term Life, Health, and Critical Illness policies with estimated monthly premiums and deductibles, along with customized financial advice.
4. **History (`/history`):** Users can browse past generations, search by name, and delete old records to keep their data clean.

*(To view the live demo, run the application locally on `http://127.0.0.1:5000` or visit the configured ngrok proxy link if active).*
