import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Helpers: emojis for priority and task type (Challenges 3 & 4)
# ---------------------------------------------------------------------------
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
TYPE_EMOJI = {
    "walk":       "🦮",
    "feeding":    "🍽️",
    "meds":       "💊",
    "grooming":   "✂️",
    "enrichment": "🧩",
}

def priority_label(p: str) -> str:
    return f"{PRIORITY_EMOJI.get(p, '')} {p.upper()}"

def type_label(t: str) -> str:
    return f"{TYPE_EMOJI.get(t, '')} {t}"


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
DATA_FILE = "data.json"

if "owner" not in st.session_state:
    # Challenge 2: load persisted data on startup if file exists
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.session_state.pet = (
                st.session_state.owner.pets[0] if st.session_state.owner.pets else None
            )
        except Exception:
            st.session_state.owner = None
            st.session_state.pet = None
    else:
        st.session_state.owner = None
        st.session_state.pet = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "use_weighted" not in st.session_state:
    st.session_state.use_weighted = False

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.caption("Smart daily pet care scheduling")

if st.session_state.owner:
    st.info(
        f"Loaded saved data for **{st.session_state.owner.name}** "
        f"({len(st.session_state.owner.pets)} pet(s), "
        f"{len(st.session_state.owner.get_all_tasks())} task(s))"
    )

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet setup
# ---------------------------------------------------------------------------
st.subheader("1. 👤 Owner & Pet Info")

with st.form("setup_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name     = st.text_input("Owner name", value="Jordan")
        available_mins = st.number_input("Available minutes today", min_value=10, max_value=480, value=60)
    with col2:
        pet_name = st.text_input("Pet name", value="Mochi")
        species  = st.selectbox("Species", ["dog", "cat", "other"])
    submitted = st.form_submit_button("Save owner & pet")

if submitted:
    owner = Owner(name=owner_name, available_minutes=int(available_mins))
    pet   = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet   = pet
    owner.save_to_json(DATA_FILE)   # Challenge 2: persist immediately
    st.success(f"Saved {owner_name}'s pet {pet_name} ({species}) — {available_mins} min budget")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add tasks
# ---------------------------------------------------------------------------
st.subheader("2. 📋 Add Care Tasks")

if st.session_state.pet is None:
    st.info("Complete Step 1 before adding tasks.")
else:
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
        with col2:
            task_type = st.selectbox("Type", ["walk", "feeding", "meds", "grooming", "enrichment"])
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        col4, col5 = st.columns(2)
        with col4:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col5:
            frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly"])
        add_task = st.form_submit_button("➕ Add task")

    if add_task:
        task = Task(
            name=task_name,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
            frequency=None if frequency == "one-time" else frequency,
        )
        st.session_state.pet.add_task(task)
        st.session_state.owner.save_to_json(DATA_FILE)   # Challenge 2: persist
        st.success(
            f"{TYPE_EMOJI.get(task_type, '')} Added: **{task_name}** "
            f"({duration} min, {priority_label(priority)}, {frequency})"
        )

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        scheduler = Scheduler(st.session_state.owner)

        # Conflict warnings
        conflicts = scheduler.detect_conflicts(all_tasks)
        for warning in conflicts:
            st.warning(f"⚠️ Task conflict: {warning}")

        # Sorted task table with emoji labels (Challenges 3 & 4)
        st.markdown("**Current tasks (sorted shortest first):**")
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.table([
            {
                "Task": task.name,
                "Type": type_label(task.task_type),
                "Duration": f"{task.duration_minutes} min",
                "Priority": priority_label(task.priority),
                "Frequency": task.frequency or "one-time",
                "Score": f"{task.urgency_score():.1f}",
            }
            for task in sorted_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# ---------------------------------------------------------------------------
st.subheader("3. 📅 Generate Daily Schedule")

use_weighted = st.toggle(
    "Use weighted scoring (Challenge 1)",
    value=st.session_state.use_weighted,
    help="Weighted mode scores tasks by priority + recurrence bonus - duration penalty instead of fixed priority tiers.",
)
st.session_state.use_weighted = use_weighted

if st.button("⚡ Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please complete Step 1 first.")
    elif not st.session_state.owner.get_all_tasks():
        st.warning("Please add at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # Conflict check before generating
        conflicts = scheduler.detect_conflicts(st.session_state.owner.get_all_tasks())
        if conflicts:
            st.warning("⚠️ Heads up — conflicts exist in your task list:")
            for c in conflicts:
                st.caption(f"• {c}")

        plan = (
            scheduler.weighted_generate_plan()
            if use_weighted
            else scheduler.generate_plan()
        )

        mode_label = "weighted scoring" if use_weighted else "priority order"
        col1, col2, col3 = st.columns(3)
        col1.metric("Scheduled", f"{len(plan.scheduled_tasks)} tasks")
        col2.metric("Time used", f"{plan.total_duration} min")
        col3.metric("Time remaining",
                    f"{st.session_state.owner.available_minutes - plan.total_duration} min")

        if plan.scheduled_tasks:
            st.success(f"Daily plan ready for {plan.date} ({mode_label})")
            st.markdown("**Scheduled Tasks:**")
            st.table([
                {
                    "Task": t.name,
                    "Type": type_label(t.task_type),
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": priority_label(t.priority),
                    "Recurring": t.frequency or "one-time",
                    "Score": f"{t.urgency_score():.1f}",
                }
                for t in plan.scheduled_tasks
            ])

        if plan.skipped_tasks:
            st.error(f"{len(plan.skipped_tasks)} task(s) could not fit in today's schedule:")
            st.table([
                {"Skipped Task": t.name, "Priority": priority_label(t.priority), "Reason": t.reason_skipped}
                for t in plan.skipped_tasks
            ])

        with st.expander("💡 Why was this plan chosen?"):
            st.info(plan.explain_reasoning())
