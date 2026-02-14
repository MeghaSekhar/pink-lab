# 💗 Pink Focus Lab 📚  
### Emotion-Aware Study Planner with Soft Productivity

---

## 🎯 Basic Details

**Project Type:** Individual Project  
**Developer:** Megha M Sekhar  
**College:** LBSITW
**Live App:** https://pink-focus-lab.streamlit.app/
**Repository:** https://github.com/MeghaSekhar/pink-lab

---

## 📌 Project Description

Pink Focus Lab is an emotion-aware study planner built with Streamlit that adapts daily study plans based on mood, energy levels, and sleep quality.

Instead of forcing productivity, the system intelligently adjusts study difficulty, time budget, and recommended techniques to prevent burnout while maintaining consistency.

It blends productivity with emotional intelligence 💕

---

## ❗ Problem Statement

Traditional productivity tools:

- Ignore emotional state  
- Encourage over-planning  
- Increase burnout risk  
- Don’t adapt to low-energy days  
- Offer generic study advice  

Students need a system that understands their mental state before assigning workload.

---

## 💡 The Solution

Pink Focus Lab:

- Calculates a daily study time budget based on mood + energy + sleep  
- Restricts task difficulty when energy is low  
- Automatically selects suitable tasks within budget  
- Suggests study techniques dynamically  
- Tracks technique usage  
- Provides motivational support  
- Includes a built-in focus timer  

It promotes sustainable productivity instead of hustle culture.

---

# 🛠 Technical Architecture

## 💻 Tech Stack

**Language:** Python  
**Framework:** Streamlit  
**Data Storage:** Local JSON file (`planner_data.json`)  

**Libraries Used:**
- streamlit  
- datetime  
- random  
- json  
- os  

---

# 🧠 Core Planning Logic

The app uses adaptive logic inside `emotion_aware_study_planner.py`.

## 🎯 1. Daily Study Budget Calculation

```python
def get_daily_budget(mood, energy, sleep_hours)
```

Budget is determined by:

- Mood score (1–5)  
- Energy score (1–5)  
- Sleep hours  

Rules:
- < 5 hours sleep → 45 min cap  
- Low combined score → 60–90 min  
- High combined score → up to 180 min  

This prevents overload on low-capacity days.

---

## 🎯 2. Allowed Difficulty System

```python
def allowed_difficulties(mood, energy, sleep_hours)
```

Low mood/energy → only "easy" tasks allowed  
Medium state → "easy" + "medium"  
High state → all difficulties allowed  

This ensures emotional safety in planning.

---

## 🎯 3. Task Selection Algorithm

Inside:

```python
plan_today_for_app()
```

Steps:
1. Filter incomplete tasks  
2. Filter by allowed difficulty  
3. Sort by:
   - Earliest due date  
   - Shortest duration  
4. Add tasks until daily budget is filled  
5. Log session data  

---

# 📊 Data Model

Stored inside `planner_data.json`.

## Tasks Structure

```json
{
  "id": 1,
  "subject": "Math",
  "topic": "Integration",
  "difficulty": "medium",
  "estimated_minutes": 45,
  "due_date": "2026-02-20",
  "completed": false
}
```

---

## Log Structure

Each planning session saves:

```json
{
  "date": "2026-02-14",
  "mood": 3,
  "energy": 4,
  "sleep_hours": 7,
  "planned_task_ids": [1, 2],
  "completed_task_ids": [],
  "technique_used": null
}
```

---

## Technique Stats

Tracks usage count:

```json
{
  "pomodoro": 4,
  "active_recall": 2
}
```

---

# ✨ Features

## 🧠 Emotion-Based Daily Planning
Adaptive workload based on psychological state.

## 📝 Smart Task Manager
- Add tasks  
- Set difficulty  
- Assign due dates  
- Mark complete  
- Delete tasks  

## 🎯 Study Technique Recommendation
Dynamic suggestion using:

```python
suggest_technique_for_app()
```

Logic:
- Low mood/energy → Pomodoro  
- High difficulty tasks → Active Recall / Interleaving  
- Otherwise → Random technique  

## 📈 Technique Progress Tracking
Displays number of days each technique was used.

## 💬 Motivation System
Randomly selected supportive lines each session.

## ⏱ Built-In Focus Timer
- Custom label  
- Adjustable duration  
- Live countdown  
- Auto refresh using `st.rerun()`  

---

# 🏗 System Architecture

User Input (Mood, Energy, Sleep)  
↓  
Streamlit UI  
↓  
Planning Logic Layer (`emotion_aware_study_planner.py`)  
↓  
JSON Storage (`planner_data.json`)  
↓  
Dynamic Plan Output  

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/MeghaSekhar/PINK-FOCUS-LABS.git
cd pink-focus-lab
```

## 2️⃣ Install Dependencies

```bash
pip install streamlit
```

Or if using requirements file:

```bash
pip install -r requirements.txt
```

## 3️⃣ Run Application

```bash
streamlit run app.py
```

---


# 🔒 Limitations

- Uses local JSON storage (not multi-user ready)  
- No authentication system  
- No cloud database  
- Data resets if JSON file deleted  

---

# 🚀 Future Improvements

- User login & authentication  
- Cloud database (Firebase / Supabase)  
- Mood history analytics dashboard  
- Study streak tracking  
- Calendar integration  
- AI-generated adaptive scheduling  
- Push notifications  
- Dark mode toggle  

---

# 🤖 AI Transparency

**Tool Used:** ChatGPT  

**Used For:**
- UI refinement ideas  
- Debugging support  
- Code optimization suggestions  
- Documentation formatting  

**Estimated AI Contribution:** ~15–20%  

Core logic and architecture were designed and implemented manually.

---

# 👩‍💻 Developer Contributions

Megha M Sekhar

- Concept design  
- Planning algorithm creation  
- Difficulty gating system  
- Task prioritization logic  
- UI implementation  
- Timer logic  
- JSON data architecture  
- Testing and debugging  
- Documentation  
