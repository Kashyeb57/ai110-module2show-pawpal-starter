import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation — objects are created once and reused on every
# subsequent rerun (Streamlit re-executes the whole script on each interaction)
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # set after the setup form is submitted

if "pet" not in st.session_state:
    st.session_state.pet = None

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Info")

with st.form("setup_form"):
    owner_name      = st.text_input("Owner name", value="Jordan")
    available_mins  = st.number_input("Available minutes today", min_value=10, max_value=480, value=60)
    pet_name        = st.text_input("Pet name", value="Mochi")
    species         = st.selectbox("Species", ["dog", "cat", "other"])
    submitted       = st.form_submit_button("Save owner & pet")

if submitted:
    # Build fresh Owner + Pet and store in session state
    owner = Owner(name=owner_name, available_minutes=int(available_mins))
    pet   = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.success(f"Saved: {owner_name} with pet {pet_name} ({species})")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add tasks (only available after owner/pet are set up)
# ---------------------------------------------------------------------------
st.subheader("Add Care Tasks")

if st.session_state.pet is None:
    st.info("Save an owner & pet above before adding tasks.")
else:
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
        with col2:
            task_type = st.selectbox("Type", ["walk", "feeding", "meds", "grooming", "enrichment"])
        with col3:
            priority  = st.selectbox("Priority", ["high", "medium", "low"])
        duration      = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        add_task      = st.form_submit_button("Add task")

    if add_task:
        task = Task(
            name=task_name,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
        )
        st.session_state.pet.add_task(task)
        st.success(f"Added: {task_name} ({duration} min, {priority} priority)")

    # Show current task list
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table([
            {"Task": t.name, "Type": t.task_type, "Duration (min)": t.duration_minutes, "Priority": t.priority}
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Generate Daily Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an owner & pet first.")
    elif not st.session_state.owner.get_all_tasks():
        st.warning("Please add at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan      = scheduler.generate_plan()

        st.success(f"Schedule generated for {plan.date} — {plan.total_duration} min used out of {st.session_state.owner.available_minutes} min")

        st.markdown("**Scheduled Tasks:**")
        st.table([
            {"Task": t.name, "Type": t.task_type, "Duration (min)": t.duration_minutes, "Priority": t.priority}
            for t in plan.scheduled_tasks
        ])

        if plan.skipped_tasks:
            st.markdown("**Skipped Tasks:**")
            st.table([
                {"Task": t.name, "Reason": t.reason_skipped}
                for t in plan.skipped_tasks
            ])

        st.info(plan.explain_reasoning())
