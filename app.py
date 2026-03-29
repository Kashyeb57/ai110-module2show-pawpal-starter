import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("PawPal+")
st.caption("Smart daily pet care scheduling")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet setup
# ---------------------------------------------------------------------------
st.subheader("1. Owner & Pet Info")

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
    st.success(f"Saved {owner_name}'s pet {pet_name} ({species}) — {available_mins} min budget")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add tasks
# ---------------------------------------------------------------------------
st.subheader("2. Add Care Tasks")

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
        add_task = st.form_submit_button("Add task")

    if add_task:
        task = Task(
            name=task_name,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
            frequency=None if frequency == "one-time" else frequency,
        )
        st.session_state.pet.add_task(task)
        st.success(f"Added: {task_name} ({duration} min, {priority} priority, {frequency})")

    # --- Conflict warnings shown live as tasks are added ---
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        scheduler = Scheduler(st.session_state.owner)
        conflicts = scheduler.detect_conflicts(all_tasks)
        if conflicts:
            for warning in conflicts:
                st.warning(f"Task conflict detected: {warning}")

        # Show tasks sorted by duration (shortest first)
        st.markdown("**Current tasks (sorted shortest first):**")
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.table([
            {
                "Task": t.name,
                "Type": t.task_type,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency or "one-time",
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# ---------------------------------------------------------------------------
st.subheader("3. Generate Daily Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please complete Step 1 first.")
    elif not st.session_state.owner.get_all_tasks():
        st.warning("Please add at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # --- Conflict check before generating ---
        conflicts = scheduler.detect_conflicts(st.session_state.owner.get_all_tasks())
        if conflicts:
            st.warning("Heads up — conflicts exist in your task list. Review them in Step 2.")
            for c in conflicts:
                st.caption(f"• {c}")

        plan = scheduler.generate_plan()

        # --- Summary metric row ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Scheduled", f"{len(plan.scheduled_tasks)} tasks")
        col2.metric("Time used", f"{plan.total_duration} min")
        col3.metric("Time remaining", f"{st.session_state.owner.available_minutes - plan.total_duration} min")

        # --- Scheduled tasks ---
        if plan.scheduled_tasks:
            st.success(f"Daily plan ready for {plan.date}")
            st.markdown("**Scheduled Tasks:**")
            st.table([
                {
                    "Task": t.name,
                    "Type": t.task_type,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.upper(),
                    "Recurring": t.frequency or "one-time",
                }
                for t in plan.scheduled_tasks
            ])

        # --- Skipped tasks ---
        if plan.skipped_tasks:
            st.error(f"{len(plan.skipped_tasks)} task(s) could not fit in today's schedule:")
            st.table([
                {"Skipped Task": t.name, "Reason": t.reason_skipped}
                for t in plan.skipped_tasks
            ])

        # --- Reasoning ---
        with st.expander("Why was this plan chosen?"):
            st.info(plan.explain_reasoning())
