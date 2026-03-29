import base64
from datetime import date
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

BANNER_FILE = "photo.jpg" 


# ── 全局样式：浅粉色主题 ──────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #FFF0F3;
}
[data-testid="stHeader"] {
    background-color: transparent;
    box-shadow: none;
}
.block-container {
    background-color: #FFF0F3;
    padding-top: 0 !important;
}


h1, h2, h3 { color: #B5334E; }


div.stButton > button {
    background-color: #E8748A;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: background 0.2s;
}
div.stButton > button:hover {
    background-color: #C2476A;
    color: #fff;
}


label {
    color: #7A2A3E !important;
    font-weight: 500;
}

table { background-color: #FFF8F9; border-radius: 8px; }
thead tr th {
    background-color: #F5B8C4 !important;
    color: #4A1428 !important;
}

hr { border-color: #F5C6CF; }

.stCaption, small { color: #9E4A61 !important; }
</style>
""", unsafe_allow_html=True)


# ── Banner / Hero ───────────────────────────────────────────────
banner_path = Path(BANNER_FILE) if BANNER_FILE else None

if banner_path and banner_path.exists():
    st.markdown("""
<div style="border-radius:16px; overflow:hidden; margin-bottom:8px;
            box-shadow:0 4px 20px rgba(180,80,100,0.15);">
""", unsafe_allow_html=True)
    st.image(str(banner_path), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="
    background: linear-gradient(135deg, #F5B8C4 0%, #FADADD 60%, #FFF0F3 100%);
    border-radius: 16px;
    padding: 36px 32px 28px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(180,80,100,0.15);
">
    <span style="font-size:3.2rem;">🐾</span>
    <h1 style="color:#B5334E; margin:8px 0 6px; font-size:2.6rem; letter-spacing:1px;">PawPal+</h1>
    <p style="color:#9E4A61; margin:0; font-size:1.05rem;">Smart daily care scheduling for your pets</p>
</div>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ── Step 1: Create Owner ──────────────────────────────────────────────────────
st.subheader("1. Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Set Owner"):
    st.session_state.owner = Owner(owner_name)
    st.session_state.next_pet_id = 1
    st.session_state.next_task_id = 1
    st.session_state.scheduler = None
    st.success(f"Owner '{owner_name}' created.")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
st.caption(f"Current owner: **{owner.name}** — {len(owner.pets)} pet(s)")

st.divider()


# ── Step 2: Add a Pet ─────────────────────────────────────────────────────────
st.subheader("2. Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    new_pet = Pet(
        pet_id=st.session_state.next_pet_id,
        name=pet_name,
        species=species,
        age=age,
    )
    try:
        owner.add_pet(new_pet)
        st.session_state.next_pet_id += 1
        st.session_state.scheduler = None
        st.success(f"Added pet '{pet_name}' (ID {new_pet.pet_id}).")
    except ValueError as e:
        st.error(str(e))

if owner.pets:
    st.write("**Your pets:**")
    st.table([
        {"ID": p.pet_id, "Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)}
        for p in owner.pets
    ])

st.divider()


# ── Step 3: Add a Task ────────────────────────────────────────────────────────
st.subheader("3. Add a Task")

if not owner.pets:
    st.info("Add at least one pet first.")
else:
    pet_options = {f"{p.name} (ID {p.pet_id})": p for p in owner.pets}
    selected_label = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet: Pet = pet_options[selected_label]

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox(
            "Category", ["walk", "feeding", "medication", "play", "grooming", "other"]
        )
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)

    col3, col4 = st.columns(2)
    with col3:
        preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
    with col4:
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

    due_input = None
    if recurrence != "none":
        due_input = st.date_input("First due date", value=date.today())

    if st.button("Add Task"):
        new_task = Task(
            task_id=st.session_state.next_task_id,
            pet_name=selected_pet.name,
            title=task_title,
            category=category,
            duration=duration,
            priority=priority,
            preferred_time=preferred_time.strip() if preferred_time.strip() else None,
            recurrence=recurrence if recurrence != "none" else None,
            due_date=due_input if recurrence != "none" else None,
        )
        selected_pet.add_task(new_task)
        st.session_state.next_task_id += 1
        st.session_state.scheduler = None
        st.success(f"Task '{task_title}' added to {selected_pet.name}.")

    if selected_pet.tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")

        status_filter = st.radio(
            "Show", ["All", "Pending only", "Done only"],
            horizontal=True,
            key="task_status_filter",
        )

        pet_scheduler = Scheduler(tasks=list(selected_pet.tasks))
        if status_filter == "Pending only":
            display_tasks = pet_scheduler.filter_tasks(completed=False)
        elif status_filter == "Done only":
            display_tasks = pet_scheduler.filter_tasks(completed=True)
        else:
            display_tasks = selected_pet.tasks

        if display_tasks:
            st.table([
                {
                    "ID": t.task_id,
                    "Title": t.title,
                    "Category": t.category,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Time": t.preferred_time or "—",
                    "Recurrence": t.recurrence or "—",
                    "Due": str(t.due_date) if t.due_date else "—",
                    "Status": "✅ Done" if t.completed else "⬜ Pending",
                }
                for t in display_tasks
            ])
        else:
            st.info(f"No {status_filter.lower()} tasks for {selected_pet.name}.")

st.divider()


# ── Step 4: Generate Schedule ─────────────────────────────────────────────────
st.subheader("4. Daily Schedule")

all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("Add some tasks first to generate a schedule.")
else:
    col_sort, col_filter = st.columns(2)
    with col_sort:
        sort_mode = st.radio(
            "Sort by", ["Priority (high → low)", "Time (chronological)"],
            horizontal=True,
        )
    with col_filter:
        pet_names = ["All pets"] + [p.name for p in owner.pets]
        filter_pet = st.selectbox("Filter by pet", pet_names)

    if st.button("Generate Schedule"):
        st.session_state.scheduler = Scheduler(owner=owner)

    scheduler: Scheduler = st.session_state.scheduler

    if scheduler is not None:
        if sort_mode == "Time (chronological)":
            sorted_tasks = scheduler.sort_by_time()
            sort_label = "chronological order"
        else:
            scheduler.generate_daily_plan()
            sorted_tasks = scheduler.daily_plan
            sort_label = "priority order"

        if filter_pet != "All pets":
            sorted_tasks = scheduler.filter_tasks(pet_name=filter_pet)
            if sort_mode == "Time (chronological)":
                sorted_tasks = Scheduler(tasks=sorted_tasks).sort_by_time()
            else:
                sorted_tasks = sorted(sorted_tasks, key=lambda t: (-t.priority, t.preferred_time or "99:99"))

        warnings = scheduler.warn_conflicts()
        if warnings:
            st.error(
                f"**{len(warnings)} scheduling conflict(s) detected.** "
                "Resolve these before your day starts:"
            )
            for msg in warnings:
                clean = msg.replace("WARNING: ", "", 1)
                st.warning(clean)
        else:
            st.success("No scheduling conflicts — your day looks clear!")

        if sorted_tasks:
            st.write(f"**Showing {len(sorted_tasks)} task(s) in {sort_label}:**")
            st.table([
                {
                    "Time": t.preferred_time or "—",
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Category": t.category,
                    "Duration (min)": t.duration,
                    "Priority": "★" * t.priority,
                    "Recurrence": t.recurrence or "—",
                    "Status": "✅ Done" if t.completed else "⬜ Pending",
                }
                for t in sorted_tasks
            ])
        else:
            st.info("No tasks match the current filter.")
