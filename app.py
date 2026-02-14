import streamlit as st
import time
from datetime import datetime, date
st.markdown(
    """
    <style>
    /* APP BACKGROUND: SOFT GIRLY PINK */
    .stApp {
        background: linear-gradient(
            135deg,
            #FFB6F0 0%,
            #FFE6F7 35%,
            #FFC2EB 70%,
            #FFE6F7 100%
        );
        min-height: 100vh;
    }
    /* DROPDOWN: WHITE TEXT ON PINK */
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #FF1493 !important;
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] [role="listbox"] {
    background-color: #FF1493 !important;
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] [role="option"] {
    color: #FFFFFF !important;
    background-color: #FF1493 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] svg {
    color: #FFFFFF !important;
}

/* SELECTBOX: LIGHT PINK INSTEAD OF BLACK */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFE6F7 !important;
    color: #000000 !important;
    border: 2px solid #FF69B4 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
    color: #000000 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] input {
    background-color: #FFE6F7 !important;
    color: #000000 !important;
}

section[data-testid="stSidebar"] [role="combobox"] {
    background-color: #FFE6F7 !important;
    color: #000000 !important;
}
    

    /* SIDEBAR: HOT PINK WITH WHITE TEXT */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #C20063 0%, #FF1493 40%, #FF0066 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 8px 32px rgba(194, 0, 99, 0.7);
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    /* HEADERS/TITLE: PINK */
    h1, h2, h3, h4, h5, h6 {
        color: #FF1493 !important;
        text-shadow: 0 0 6px rgba(255, 182, 240, 0.9);
    }

    /* NORMAL TEXT: BLACK */
    body, p, span, li {
        color: #000000 !important;
    }

    /* BUTTONS: PINK PILL STYLE */
    .stButton > button {
        background-color: #FF1493 !important;
        color: #FFFFFF !important;
        border-radius: 999px !important;
        border: 2px solid #FF8AD9 !important;
        font-weight: 700 !important;
        box-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
    }

    .stButton > button:hover {
        background-color: #FF69B4 !important;
        color: #000000 !important;
    }

    /* INPUTS */
    input, textarea, select {
        border-radius: 999px !important;
        border: 2px solid #FF9AD9 !important;
        background-color: #FFE6F7 !important;
        color: #000000 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


from emotion_aware_study_planner import (
    get_study_plan_for_app,
    get_tasks_for_app,
    add_task_from_app,
    delete_task_from_app,
    add_journal_entry_from_app,
    get_recent_journals_for_app,
    get_techniques_for_app,
    save_technique_usage_from_app,
    get_technique_stats_for_app,
    plan_today_for_app,
    suggest_technique_for_app,
    get_tasks_grouped_by_due_date_for_app,
    get_motivation_for_app,
    delete_journal_entry_from_app,
    get_task_deadline_info,
    load_data,
    save_data,
    set_task_completed_from_app,
)

st.title("Pink Focus Lab 💗📚")
st.caption("An emotion-aware study studio that plans your tasks, techniques, and tiny wins.")

page = st.sidebar.selectbox(
    "Section",
    ["Today's Plan", "Tasks", "Journal", "Techniques", "Calendar"]
)

# ---------------------------------------------------------
# TODAY'S PLAN
# ---------------------------------------------------------
if page == "Today's Plan":
    st.header("Today's Plan 🧠")
    st.write("This uses your original logic to plan study time based on mood, energy, and sleep.")

    mood_display = st.selectbox(
        "Mood 💭",
        ["Very low 🥺", "Low 😞", "Okay 🙂", "Good 😊", "Great 🤩"]
    )

    energy_display = st.selectbox(
        "Energy level",
        ["Very low", "Low", "Medium", "High", "Very high"]
    )

    sleep_hours = st.slider(
        "How many hours did you sleep last night?",
        min_value=0.0,
        max_value=12.0,
        value=7.0,
        step=0.5
    )

    mood_map = {
        "Very low 🥺": 1,
        "Low 😞": 2,
        "Okay 🙂": 3,
        "Good 😊": 4,
        "Great 🤩": 5
    }

    energy_map = {
        "Very low": 1,
        "Low": 2,
        "Medium": 3,
        "High": 4,
        "Very high": 5
    }

    plan = None
    mood_level = None
    energy_level = None

    if st.button("Plan my study"):
        mood_level = mood_map[mood_display]
        energy_level = energy_map[energy_display]

        plan = plan_today_for_app(mood_level, energy_level, sleep_hours)

        st.subheader("Today's plan:")
        for msg in plan["messages"]:
            st.write(msg)

        if plan["tasks"]:
            st.markdown("**Suggested tasks for today:**")
            for t in plan["tasks"]:
                status = "✅" if t.get("completed") else "⏳"
                _, deadline_label = get_task_deadline_info(t)
                st.write(
                    f"[{t['id']}] {status} {t['subject']} - {t['topic']} "
                    f"({t['difficulty']}, {t['estimated_minutes']} min, "
                    f"due {t['due_date']} — {deadline_label})"
                )
        else:
            st.write("No suitable tasks for today.")

        st.markdown("---")
        st.subheader("Suggested study technique for this plan")

        tech = suggest_technique_for_app(
            mood_level,
            energy_level,
            plan["max_difficulty"]
        )
        if tech:
            st.markdown(f"**{tech['name']}**")
            st.write(tech["how"])
            if st.button("Use this technique today"):
                save_technique_usage_from_app(tech["code"])
                st.success("Technique saved for today and progress updated.")
        else:
            st.write("No techniques defined.")

        st.markdown("---")
        st.subheader("Motivation for you today")
        st.write(get_motivation_for_app())

    st.subheader("Focus timer (Today's Plan)")
    timer_label = st.text_input("Timer label", value="Focus block")
    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input("Hours", min_value=0, max_value=12, value=0, step=1)
    with col2:
        minutes = st.number_input("Minutes", min_value=0, max_value=55, value=25, step=5)

    total_seconds = int(hours * 3600 + minutes * 60)

    if "plan_timer_end" not in st.session_state:
        st.session_state.plan_timer_end = None
    if "plan_timer_label" not in st.session_state:
        st.session_state.plan_timer_label = None

    start_col, stop_col = st.columns(2)
    with start_col:
        if st.button("Start timer (Plan)"):
            if total_seconds > 0:
                st.session_state.plan_timer_end = time.time() + total_seconds
                st.session_state.plan_timer_label = timer_label
    with stop_col:
        if st.button("Reset timer (Plan)"):
            st.session_state.plan_timer_end = None
            st.session_state.plan_timer_label = None

    if st.session_state.plan_timer_end:
        remaining = int(st.session_state.plan_timer_end - time.time())
        if remaining <= 0:
            st.session_state.plan_timer_end = None
            st.success(f"{st.session_state.plan_timer_label or 'Timer'} finished!")
        else:
            mins, secs = divmod(remaining, 60)
            hours_left, mins_left = divmod(mins, 60)
            st.markdown(
                f"**{st.session_state.plan_timer_label or 'Timer'}:** "
                f"{hours_left:02d}:{mins_left:02d}:{secs:02d} left"
            )
            time.sleep(1)
            st.rerun()
    else:
        st.info("Set hours and minutes, give a label, then click Start timer.")

# ---------------------------------------------------------
# CALENDAR
# ---------------------------------------------------------
elif page == "Calendar":
    st.header("Calendar of Due Tasks 📅")

    by_date = get_tasks_grouped_by_due_date_for_app()
    if not by_date:
        st.info("No tasks yet.")
    else:
        for due, tasks_on_date in sorted(by_date.items()):
            st.subheader(due)
            for t in tasks_on_date:
                status = "✅" if t["completed"] else "⏳"
                _, deadline_label = get_task_deadline_info(t)
                st.write(
                    f"[{t['id']}] {status} {t['subject']} - {t['topic']} "
                    f"({t['difficulty']}, {t['estimated_minutes']} min — {deadline_label})"
                )

# ---------------------------------------------------------
# TECHNIQUES
# ---------------------------------------------------------
elif page == "Techniques":
    st.header("Study Techniques 🎯")

    st.subheader("Learn and pick a technique for today")
    techniques = get_techniques_for_app()
    options = {f"{t['name']} ({t['code']})": t['code'] for t in techniques}
    if options:
        chosen_label = st.selectbox("Choose a technique", list(options.keys()))
        chosen_code = options[chosen_label]
        chosen = next(t for t in techniques if t["code"] == chosen_code)

        st.markdown(f"**{chosen['name']}**")
        st.write(chosen["how"])

        if st.button("Use this technique today"):
            save_technique_usage_from_app(chosen_code)
            st.success("Technique saved for today and progress updated.")
    else:
        st.info("No techniques defined.")

    st.subheader("Technique progress")
    stats = get_technique_stats_for_app()
    if not stats:
        st.info("No technique usage tracked yet.")
    else:
        for s in stats:
            st.write(f"{s['name']}: used on {s['count']} day(s)")

# ---------------------------------------------------------
# JOURNAL
# ---------------------------------------------------------
elif page == "Journal":
    st.header("Tea Corner / Journal ☕")

    st.subheader("Write about your day")
    text = st.text_area("Spill what’s on your mind (like in Tea Corner):")

    uploaded_image = st.file_uploader(
        "Optional: add an image (PNG/JPG)",
        type=["png", "jpg", "jpeg"]
    )

    win_today = st.checkbox("I overcame a block / finished something faster than expected today ✨")
    win_summary = ""
    if win_today:
        win_summary = st.text_input("One-line description of that win:")

    if st.button("Save journal entry"):
        if text.strip():
            image_name = None
            if uploaded_image is not None:
                image_name = uploaded_image.name
                with open(image_name, "wb") as f:
                    f.write(uploaded_image.getbuffer())

            add_journal_entry_from_app(text, image_name)

            if win_today and win_summary.strip():
                data = load_data()
                today_str = date.today().isoformat()
                data["achievements"].append({
                    "date": today_str,
                    "summary": win_summary.strip()
                })
                save_data(data)

            st.success("Journal entry saved.")
        else:
            st.warning("Write something before saving.")

    st.subheader("Recent entries")
    journals = get_recent_journals_for_app()
    if not journals:
        st.info("No journal entries yet.")
    else:
        for idx, entry in enumerate(journals):
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"**{entry.get('date', '')}**")
                st.write(entry.get("text", ""))
                if entry.get("image"):
                    st.image(entry["image"], caption="Attached image", use_column_width=True)
            with cols[1]:
                if st.button("Delete", key=f"del_journal_{idx}"):
                    delete_journal_entry_from_app(idx)
                    st.success("Journal entry deleted.")
                    st.rerun()
            st.markdown("---")

# ---------------------------------------------------------
# TASKS
# ---------------------------------------------------------
elif page == "Tasks":
    st.header("Tasks 📝")

    st.subheader("Add a new task")
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
    est_minutes = st.number_input(
        "Estimated minutes",
        min_value=5,
        max_value=300,
        value=30,
        step=5
    )
    due_str = st.text_input("Due date (YYYY-MM-DD)")
    planned_time = st.time_input("When do you plan to study this? (optional)")

    if st.button("Add task"):
        if subject.strip() and topic.strip() and due_str.strip():
            planned_time_str = planned_time.strftime("%H:%M") if planned_time else None
            add_task_from_app(
                subject,
                topic,
                difficulty,
                est_minutes,
                due_str,
                planned_time_str
            )
            st.success("Task added!")
        else:
            st.warning("Please fill subject, topic, and due date.")

    st.subheader("Focus timer (Tasks)")
    t_label = st.text_input("Timer label (Tasks)", value="Task focus block")
    c1, c2 = st.columns(2)
    with c1:
        t_hours = st.number_input("Hours (Tasks)", min_value=0, max_value=12, value=0, step=1)
    with c2:
        t_minutes = st.number_input("Minutes (Tasks)", min_value=0, max_value=55, value=25, step=5)

    t_seconds = int(t_hours * 3600 + t_minutes * 60)

    if "tasks_timer_end" not in st.session_state:
        st.session_state.tasks_timer_end = None
    if "tasks_timer_label" not in st.session_state:
        st.session_state.tasks_timer_label = None

    c3, c4 = st.columns(2)
    with c3:
        if st.button("Start tasks timer"):
            if t_seconds > 0:
                st.session_state.tasks_timer_end = time.time() + t_seconds
                st.session_state.tasks_timer_label = t_label
    with c4:
        if st.button("Reset tasks timer"):
            st.session_state.tasks_timer_end = None
            st.session_state.tasks_timer_label = None

    if st.session_state.tasks_timer_end:
        remaining = int(st.session_state.tasks_timer_end - time.time())
        if remaining <= 0:
            st.session_state.tasks_timer_end = None
            st.success(f"{st.session_state.tasks_timer_label or 'Timer'} finished!")
        else:
            mins, secs = divmod(remaining, 60)
            hours_left, mins_left = divmod(mins, 60)
            st.markdown(
                f"**{st.session_state.tasks_timer_label or 'Timer'}:** "
                f"{hours_left:02d}:{mins_left:02d}:{secs:02d} left"
            )
            time.sleep(1)
            st.rerun()
    else:
        st.info("Set hours and minutes, give a label, then click Start tasks timer.")

    st.subheader("All tasks")
    tasks = get_tasks_for_app()
    if not tasks:
        st.info("No tasks yet.")
    else:
        for t in tasks:
            cols = st.columns([1, 5, 1])
            with cols[0]:
                checked = st.checkbox(
                    "",
                    value=t["completed"],
                    key=f"chk_{t['id']}"
                )
            with cols[1]:
                status = "✅" if checked else "⏳"
                pt = t.get("planned_time")
                planned_label = f", planned at {pt}" if pt else ""
                _, deadline_label = get_task_deadline_info(t)
                st.write(
                    f"[{t['id']}] {status} {t['subject']} - {t['topic']} "
                    f"({t['difficulty']}, {t['estimated_minutes']} min, "
                    f"due {t['due_date']} — {deadline_label}{planned_label})"
                )
            with cols[2]:
                if st.button("Delete", key=f"del_{t['id']}"):
                    deleted = delete_task_from_app(t["id"])
                    if deleted:
                        st.success(f"Deleted task {t['id']}")
                        st.rerun()

            if checked != t["completed"]:
                set_task_completed_from_app(t["id"], checked)






