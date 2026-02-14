# emotion_aware_study_planner.py
import json
import os
import calendar
from datetime import datetime, date

DATA_FILE = "planner_data.json"

TECHNIQUES = {
    "pomodoro": {
        "name": "Pomodoro (focus sprints)",
        "how": "Study 25–30 minutes, then 5-minute breaks; after 3–4 rounds, take a longer 20–30 minute break."
    },
    "active_recall": {
        "name": "Active Recall",
        "how": "Study by testing yourself: close notes, try to recall concepts using questions, then check and fix gaps."
    },
    "spaced_repetition": {
        "name": "Spaced Repetition",
        "how": "Review material over increasing intervals (e.g., after 1 day, 3 days, 7 days) instead of one long cram session."
    },
    "interleaving": {
        "name": "Interleaving",
        "how": "Mix related topics in one session (e.g., different problem types) instead of practicing only one type the whole time."
    },
}

MOTIVATION_LINES = [
    "Tiny consistent sessions beat random all-nighters.",
    "You don’t need a perfect day, just one honest study block.",
    "Rest is part of the plan, not outside it.",
    "Start small. Momentum will take care of the rest.",
    "You’re building a system, not chasing a mood.",
]

# ---------- Data Handling ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "tasks": [],
            "logs": [],
            "technique_stats": {},
            "journals": [],
            "achievements": [],
        }
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    data.setdefault("technique_stats", {})
    data.setdefault("journals", [])
    data.setdefault("achievements", [])
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Helper Functions ----------

def generate_task_id(data):
    if not data["tasks"]:
        return 1
    return max(task["id"] for task in data["tasks"]) + 1

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return None

def input_difficulty():
    while True:
        diff = input("Difficulty (easy/medium/hard): ").strip().lower()
        if diff in ["easy", "medium", "hard"]:
            return diff
        print("Please enter easy, medium, or hard.")

def pick_motivation_line():
    import random
    return random.choice(MOTIVATION_LINES)

def get_recent_achievements(data, limit=3):
    achievements = sorted(
        data.get("achievements", []),
        key=lambda a: a.get("date", ""),
        reverse=True,
    )
    return achievements[:limit]

def get_task_deadline_info(task):
    """Return (days_left, label) like (2, 'in 2 days') or (0, 'today')."""
    due_str = task.get("due_date")
    try:
        due = datetime.strptime(due_str, "%Y-%m-%d").date()
    except Exception:
        return None, "no due date"

    today = date.today()
    delta = (due - today).days

    if delta < 0:
        return delta, f"{abs(delta)} day(s) overdue"
    elif delta == 0:
        return delta, "today"
    elif delta == 1:
        return delta, "in 1 day"
    else:
        return delta, f"in {delta} days"


# ---------- Task Operations ----------

def add_task(data):
    print("\n--- Add New Task ---")
    subject = input("Subject: ").strip()
    topic = input("Topic: ").strip()
    difficulty = input_difficulty()
    try:
        est_minutes = int(input("Estimated minutes (e.g., 30): "))
    except ValueError:
        print("Hmm, that doesn’t look like a number. Setting to 30 minutes.")
        est_minutes = 30
    due_str = input("Due date (YYYY-MM-DD): ").strip()
    due = parse_date(due_str)
    if not due:
        return

    task = {
        "id": generate_task_id(data),
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "estimated_minutes": est_minutes,
        "due_date": due_str,
        "completed": False,
    }
    data["tasks"].append(task)
    save_data(data)
    print(f"Nice. Task added with ID {task['id']}!")

def list_tasks(data):
    print("\n--- All Tasks ---")
    if not data["tasks"]:
        print("No tasks yet. Add one and we’ll build from there.")
        return
    for task in data["tasks"]:
        status = "✅" if task["completed"] else "⏳"
        print(
            f"[{task['id']}] {status} {task['subject']} - {task['topic']} "
            f"({task['difficulty']}, {task['estimated_minutes']} min, due {task['due_date']})"
        )

def delete_task(data):
    try:
        tid = int(input("Enter task ID to delete: "))
    except ValueError:
        print("That ID doesn’t look right.")
        return
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != tid]
    after = len(data["tasks"])
    if before == after:
        print("No task with that ID.")
    else:
        save_data(data)
        print("Poof. Task deleted.")

def mark_task_completed(data):
    try:
        tid = int(input("Enter task ID to mark completed: "))
    except ValueError:
        print("That ID doesn’t look right.")
        return
    for task in data["tasks"]:
        if task["id"] == tid:
            task["completed"] = True
            save_data(data)
            print("Task marked as completed. Go you.")
            return
    print("No task with that ID.")

# ---------- Emotion & Rest-Aware Logic ----------

def get_daily_budget(mood, energy, sleep_hours):
    score = mood + energy
    if sleep_hours < 5:
        score -= 2
    elif sleep_hours < 7:
        score -= 1

    if sleep_hours < 5:
        print("\nYou slept very little. Keep it light and be kind to yourself.")
        return 45
    if sleep_hours > 9:
        print("\nYou got a lot of sleep. Nice reset. Let’s do a focused session, not an endless scroll.")
        if score <= 4:
            return 60
        elif score <= 6:
            return 90
        else:
            return 120

    if score <= 4:
        return 60
    elif score <= 6:
        return 90
    elif score <= 8:
        return 120
    else:
        return 180

def allowed_difficulties(mood, energy, sleep_hours):
    if sleep_hours < 5:
        return ["easy"]
    if mood <= 2 or energy <= 2:
        return ["easy"]
    elif mood == 3 or energy == 3:
        return ["easy", "medium"]
    else:
        return ["easy", "medium", "hard"]

# ---------- Planning & Logging (CLI) ----------

def plan_today(data):
    if not data["tasks"]:
        print("No tasks available to plan. Add at least one first.")
        return

    print("\n--- Plan Today ---")
    try:
        mood = int(input("Mood (1-5): "))
        energy = int(input("Energy (1-5): "))
        sleep_hours = float(input("Sleep hours last night: "))
    except ValueError:
        print("Inputs got messy. Try again with numbers.")
        return

    budget = get_daily_budget(mood, energy, sleep_hours)
    allowed = allowed_difficulties(mood, energy, sleep_hours)
    today_str = date.today().isoformat()

    pending = [
        t for t in data["tasks"]
        if not t["completed"] and t["difficulty"] in allowed
    ]

    if not pending:
        print("No pending tasks that match your current energy/mood. Maybe today is pure rest.")
        return

    pending.sort(
        key=lambda t: (parse_date(t["due_date"]), t["estimated_minutes"])
    )

    chosen = []
    total_minutes = 0
    for task in pending:
        if total_minutes + task["estimated_minutes"] <= budget:
            chosen.append(task)
            total_minutes += task["estimated_minutes"]

    if not chosen:
        chosen.append(pending[0])
        total_minutes = pending[0]["estimated_minutes"]

    print(f"\nToday's budget: ~{budget} minutes")
    print("Today's Plan:")
    for task in chosen:
        print(
            f"- [{task['id']}] {task['subject']} - {task['topic']} "
            f"({task['difficulty']}, {task['estimated_minutes']} min, due {task['due_date']})"
        )

    print("\nBreak suggestion:")
    if budget <= 60:
        print("Try 25 min focus + 5 min break cycles, then real rest afterwards.")
    elif budget <= 120:
        print("Try 2–3 blocks of 25–30 min focus + 5 min breaks, with a 20–30 min longer break after.")
    else:
        print("Use 45–50 min focus + 10 min breaks, with a longer 25–30 min reset after 3 blocks.")

    if mood <= 2 or energy <= 2:
        print("\nYou sound drained. Let’s remind you of your receipts:")
        wins = get_recent_achievements(data)
        if wins:
            for w in wins:
                print(f"- {w.get('date', '')}: {w.get('summary', '')}")
        else:
            print("- No saved wins yet, but today can give you one tiny win.")

    print("\nMotivation:")
    print(pick_motivation_line())

    log_entry = {
        "date": today_str,
        "mood": mood,
        "energy": energy,
        "sleep_hours": sleep_hours,
        "planned_task_ids": [t["id"] for t in chosen],
        "completed_task_ids": [],
        "technique_used": None,
    }
    data["logs"].append(log_entry)
    save_data(data)
    print("\nPlan saved for today. Use 'Log completion' later to record what you finished.")

# ---------- Helpers used by Calendar/Today’s Plan in app ----------

def get_tasks_grouped_by_due_date_for_app():
    data = load_data()
    tasks = data["tasks"]
    by_date = {}
    for t in tasks:
        d = t.get("due_date", "No date")
        by_date.setdefault(d, []).append(t)
    return by_date

def get_month_calendar_tasks_for_app(year, month):
    data = load_data()
    tasks = data["tasks"]

    by_date = {}
    for t in tasks:
        d = t.get("due_date")
        if d:
            by_date.setdefault(d, []).append(t)

    cal = calendar.monthcalendar(year, month)
    rows = []
    for week in cal:
        for day in week:
            if day == 0:
                continue
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            weekday_idx = datetime(year, month, day).weekday()
            weekday_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][weekday_idx]

            tasks_today = by_date.get(date_str, [])
            if tasks_today:
                summaries = []
                for t in tasks_today:
                    status = "✅" if t.get("completed") else "⏳"
                    summaries.append(f"{status} {t['subject']} - {t['topic']}")
                tasks_str = "\n".join(summaries)
            else:
                tasks_str = ""

            rows.append({
                "date": date_str,
                "weekday": weekday_name,
                "tasks": tasks_str,
            })
    return rows

def plan_today_for_app(mood, energy, sleep_hours):
    """
    Pure version of plan_today for the app.
    """
    data = load_data()
    messages = []

    if not data["tasks"]:
        messages.append("No tasks available to plan. Add at least one first.")
        return {"budget": 0, "tasks": [], "messages": messages, "max_difficulty": 0}

    budget = get_daily_budget(mood, energy, sleep_hours)
    allowed = allowed_difficulties(mood, energy, sleep_hours)

    pending = [
        t for t in data["tasks"]
        if not t["completed"] and t["difficulty"] in allowed
    ]

    if not pending:
        messages.append("No pending tasks that match your current energy/mood. Maybe today is pure rest.")
        return {"budget": budget, "tasks": [], "messages": messages, "max_difficulty": 0}

    pending.sort(
        key=lambda t: (parse_date(t["due_date"]), t["estimated_minutes"])
    )

    chosen = []
    total_minutes = 0
    for task in pending:
        if total_minutes + task["estimated_minutes"] <= budget:
            chosen.append(task)
            total_minutes += task["estimated_minutes"]

    if not chosen:
        chosen.append(pending[0])
        total_minutes = pending[0]["estimated_minutes"]

    if budget <= 60:
        break_text = "Try 25 min focus + 5 min break cycles, then real rest afterwards."
    elif budget <= 120:
        break_text = "Try 2–3 blocks of 25–30 min focus + 5 min breaks, with a 20–30 min longer break after."
    else:
        break_text = "Use 45–50 min focus + 10 min breaks, with a longer 25–30 min reset after 3 blocks."

    messages.append(f"Today's budget: ~{budget} minutes.")
    messages.append("Break suggestion: " + break_text)

    today_str = date.today().isoformat()
    log_entry = {
        "date": today_str,
        "mood": mood,
        "energy": energy,
        "sleep_hours": sleep_hours,
        "planned_task_ids": [t["id"] for t in chosen],
        "completed_task_ids": [],
        "technique_used": None,
    }
    data["logs"].append(log_entry)
    save_data(data)

    max_diff_score = 0
    if chosen:
        diff_map = {"easy": 1, "medium": 2, "hard": 3}
        max_diff_score = max(diff_map.get(t["difficulty"], 1) for t in chosen)

    return {
        "budget": budget,
        "tasks": chosen,
        "messages": messages,
        "max_difficulty": max_diff_score,
    }

# ---------- Log completion (CLI) ----------

def log_completion(data):
    today_str = date.today().isoformat()
    todays_logs = [log for log in data["logs"] if log["date"] == today_str]
    if not todays_logs:
        print("No plan logged for today. Run 'Plan Today' first.")
        return
    log_entry = todays_logs[-1]

    print("\n--- Log Completion ---")
    print("Planned tasks:")
    for tid in log_entry["planned_task_ids"]:
        task = next((t for t in data["tasks"] if t["id"] == tid), None)
        if task:
            print(f"- [{task['id']}] {task['subject']} - {task['topic']}")

    done_ids = input(
        "Enter completed task IDs separated by commas (e.g., 1,3), or press Enter if none: "
    ).strip()

    if done_ids:
        try:
            done_ids = [int(x) for x in done_ids.split(",")]
        except ValueError:
            print("Those IDs didn’t parse. Skip for now.")
            return

        log_entry["completed_task_ids"] = done_ids
        for t in data["tasks"]:
            if t["id"] in done_ids:
                t["completed"] = True

        save_data(data)
        print("Completion logged.")
    else:
        print("No tasks marked as completed today.")

    procrast = input("Did today feel like a big procrastination day? (y/n): ").strip().lower()
    if procrast == "y":
        print("Okay, no shame. Think of tomorrow’s first move as just a 10-minute starter, nothing more.")

# ---------- Advice & Techniques (CLI) ----------

def advice_menu(data):
    print("\n--- Study Advice & Techniques ---")
    for key, info in TECHNIQUES.items():
        print(f"- {info['name']}  (code: {key})")
    choice = input("Enter technique code to learn/apply (or Enter to go back): ").strip().lower()
    if not choice:
        return
    if choice not in TECHNIQUES:
        print("Unknown technique code.")
        return

    info = TECHNIQUES[choice]
    print(f"\n{info['name']}")
    print("How to apply today:")
    print(info["how"])

    use_now = input("Use this technique for today's plan? (y/n): ").strip().lower()
    if use_now == "y":
        today_str = date.today().isoformat()
        todays_logs = [log for log in data["logs"] if log["date"] == today_str]
        if not todays_logs:
            log_entry = {
                "date": today_str,
                "mood": None,
                "energy": None,
                "sleep_hours": None,
                "planned_task_ids": [],
                "completed_task_ids": [],
                "technique_used": choice,
            }
            data["logs"].append(log_entry)
        else:
            todays_logs[-1]["technique_used"] = choice

        stats = data.setdefault("technique_stats", {})
        stats[choice] = stats.get(choice, 0) + 1
        save_data(data)
        print("Got it. Technique saved for today and progress updated.")

def show_technique_progress(data):
    print("\n--- Technique Progress ---")
    stats = data.get("technique_stats", {})
    if not stats:
        print("No technique usage tracked yet. Pick one and try it for a few days.")
        return
    for key, count in stats.items():
        name = TECHNIQUES.get(key, {}).get("name", key)
        print(f"- {name}: used on {count} day(s)")

# ---------- Journal & Tea Corner (CLI) ----------

def tea_corner(data):
    print("\n--- Tea Corner / Vent Space ---")
    print("Spill what’s on your mind. No filter, no grading.")
    print("(Press Enter on an empty line to finish.)")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    if not lines:
        print("Nothing today? That’s okay.")
        return

    text = "\n".join(lines)
    today_str = date.today().isoformat()

    entry = {
        "date": today_str,
        "text": text,
    }
    data["journals"].append(entry)

    win = input("Did you overcome a block or finish something faster than you expected today? (y/n): ").strip().lower()
    if win == "y":
        summary = input("Write a one-line description of that win: ").strip()
        if summary:
            data["achievements"].append({
                "date": today_str,
                "summary": summary,
            })
            print("Love that. Saved as a future reminder that you can do hard things.")

    save_data(data)
    print("Journal saved. Brain has been listened to.")

def view_journal_entries(data):
    print("\n--- Recent Journal Entries ---")
    journals = sorted(
        data.get("journals", []),
        key=lambda j: j.get("date", ""),
        reverse=True,
    )
    if not journals:
        print("No entries yet. Tea Corner is empty but waiting.")
        return

    for entry in journals[:7]:
        print(f"\n[{entry.get('date', '')}]")
        print(entry.get("text", ""))

# ---------- Main Menu (CLI) ----------

def main():
    data = load_data()
    while True:
        print("\n=== Emotion-Aware Study Planner ===")
        print("1. Add task")
        print("2. List tasks")
        print("3. Delete task")
        print("4. Mark task completed")
        print("5. Plan today (emotion & rest aware)")
        print("6. Log completion for today")
        print("7. Study advice & techniques")
        print("8. View technique progress")
        print("9. Tea Corner / Vent")
        print("10. View journal entries")
        print("11. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(data)
        elif choice == "2":
            list_tasks(data)
        elif choice == "3":
            delete_task(data)
        elif choice == "4":
            mark_task_completed(data)
        elif choice == "5":
            plan_today(data)
        elif choice == "6":
            log_completion(data)
        elif choice == "7":
            advice_menu(data)
        elif choice == "8":
            show_technique_progress(data)
        elif choice == "9":
            tea_corner(data)
        elif choice == "10":
            view_journal_entries(data)
        elif choice == "11":
            print("Goodbye! Go drink water and blink at something far away.")
            break
        else:
            print("Option not recognised. Try again.")

# ---------- Helpers for Streamlit App ----------

def get_motivation_for_app():
    return pick_motivation_line()

def delete_journal_entry_from_app(index):
    data = load_data()
    journals = data.get("journals", [])
    if 0 <= index < len(journals):
        journals.pop(index)
        data["journals"] = journals
        save_data(data)
        return True
    return False


def get_tasks_for_app():
    data = load_data()
    return data["tasks"]

def add_journal_entry_from_app(text, image_name=None):
    data = load_data()
    today_str = date.today().isoformat()
    entry = {
        "date": today_str,
        "text": text,
    }
    if image_name:
        entry["image"] = image_name
    data["journals"].append(entry)
    save_data(data)
    return entry


def get_recent_journals_for_app(limit=7):
    data = load_data()
    journals = sorted(
        data.get("journals", []),
        key=lambda j: j.get("date", ""),
        reverse=True,
    )
    return journals[:limit]

def add_task_from_app(subject, topic, difficulty, est_minutes, due_str, planned_time_str=None):
    data = load_data()
    try:
        est_minutes = int(est_minutes)
    except ValueError:
        est_minutes = 30

    task = {
        "id": generate_task_id(data),
        "subject": subject.strip(),
        "topic": topic.strip(),
        "difficulty": difficulty,
        "estimated_minutes": est_minutes,
        "due_date": due_str,
        "planned_time": planned_time_str,   # new field
        "completed": False,
    }
    data["tasks"].append(task)
    save_data(data)
    return task

def delete_task_from_app(task_id):
    data = load_data()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    after = len(data["tasks"])
    if before != after:
        save_data(data)
        return True
    return False

def set_task_completed_from_app(task_id, completed: bool):
    data = load_data()
    changed = False
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["completed"] = completed
            changed = True
            break
    if changed:
        save_data(data)
    return changed

def get_techniques_for_app():
    items = []
    for code, info in TECHNIQUES.items():
        items.append({
            "code": code,
            "name": info.get("name", code),
            "how": info.get("how", ""),
        })
    return items

def save_technique_usage_from_app(tech_code):
    data = load_data()
    today_str = date.today().isoformat()
    todays_logs = [log for log in data["logs"] if log["date"] == today_str]
    if not todays_logs:
        log_entry = {
            "date": today_str,
            "mood": None,
            "energy": None,
            "sleep_hours": None,
            "planned_task_ids": [],
            "completed_task_ids": [],
            "technique_used": tech_code,
        }
        data["logs"].append(log_entry)
    else:
        todays_logs[-1]["technique_used"] = tech_code

    stats = data.setdefault("technique_stats", {})
    stats[tech_code] = stats.get(tech_code, 0) + 1
    save_data(data)

def get_technique_stats_for_app():
    data = load_data()
    stats = data.get("technique_stats", {})
    result = []
    for code, count in stats.items():
        name = TECHNIQUES.get(code, {}).get("name", code)
        result.append({
            "code": code,
            "name": name,
            "count": count,
        })
    return result

def get_study_plan_for_app(mood_level, energy_level, sleep_hours):
    daily_budget = get_daily_budget(mood_level, energy_level, sleep_hours)
    allowed = allowed_difficulties(mood_level, energy_level, sleep_hours)
    lines = []
    lines.append(f"Today's study budget: {daily_budget} minutes.")
    lines.append(f"Recommended difficulty levels for today: {', '.join(allowed)}.")
    return "\n".join(lines)

def suggest_technique_for_app(mood, energy, max_difficulty):
    import random
    if not TECHNIQUES:
        return None

    low = (mood <= 2 or energy <= 2)
    medium = (mood == 3 or energy == 3)
    high = (mood >= 4 and energy >= 4)

    if low:
        candidates = ["pomodoro"]
    elif medium:
        candidates = ["pomodoro", "active_recall"]
    else:
        if max_difficulty >= 3:
            candidates = ["active_recall", "interleaving", "spaced_repetition"]
        else:
            candidates = ["active_recall", "spaced_repetition"]

    candidates = [c for c in candidates if c in TECHNIQUES]
    if not candidates:
        candidates = list(TECHNIQUES.keys())

    code = random.choice(candidates)
    info = TECHNIQUES[code]
    return {
        "code": code,
        "name": info.get("name", code),
        "how": info.get("how", ""),
    }

if __name__ == "__main__":
    main()
