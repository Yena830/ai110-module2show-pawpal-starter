import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session State: initialise Owner once ──────────────────────────────────────
# st.session_state works like a dictionary that survives page reruns.
# We check whether "owner" already exists before creating a new one,
# so the object (and all its pets/tasks) is never reset on button clicks.

if "owner" not in st.session_state:
    st.session_state.owner = None

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

# ── Step 1: Create Owner ──────────────────────────────────────────────────────
st.subheader("1. Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Set Owner"):
    st.session_state.owner = Owner(owner_name)
    st.session_state.next_pet_id = 1
    st.session_state.next_task_id = 1
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

# ── Step 3: Add a Task to a Pet ───────────────────────────────────────────────
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
        category = st.selectbox("Category", ["walk", "feeding", "medication", "play", "grooming", "other"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)

    preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")

    if st.button("Add Task"):
        new_task = Task(
            task_id=st.session_state.next_task_id,
            pet_name=selected_pet.name,
            title=task_title,
            category=category,
            duration=duration,
            priority=priority,
            preferred_time=preferred_time.strip() if preferred_time.strip() else None,
        )
        selected_pet.add_task(new_task)
        st.session_state.next_task_id += 1
        st.success(f"Task '{task_title}' added to {selected_pet.name}.")

    if selected_pet.tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")
        st.table([
            {
                "ID": t.task_id,
                "Title": t.title,
                "Category": t.category,
                "Duration": t.duration,
                "Priority": t.priority,
                "Time": t.preferred_time or "—",
                "Done": "✅" if t.completed else "⬜",
            }
            for t in selected_pet.tasks
        ])

st.divider()

# ── Step 4: Generate Schedule ─────────────────────────────────────────────────
st.subheader("4. Generate Schedule")

all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("Add some tasks first to generate a schedule.")
else:
    if st.button("Generate Schedule"):
        scheduler = Scheduler(owner=owner)
        scheduler.generate_daily_plan()

        st.write("**Daily Plan:**")
        st.table([
            {
                "Pet": t.pet_name,
                "Title": t.title,
                "Category": t.category,
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Time": t.preferred_time or "—",
                "Status": "Done" if t.completed else "Pending",
            }
            for t in scheduler.daily_plan
        ])

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("⚠️ Conflicts detected:")
            for t1, t2 in conflicts:
                st.write(f"- **{t1.title}** and **{t2.title}** both scheduled at `{t1.preferred_time}`")
        else:
            st.success("No scheduling conflicts.")

        st.write("**Explanation:**")
        st.text(scheduler.explain_plan())
