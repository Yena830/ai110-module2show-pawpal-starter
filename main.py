from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # 1. Create Owner
    owner = Owner("Alice")

    # 2. Create Pets
    pet1 = Pet(pet_id=1, name="Luna", species="Dog", age=3)
    pet2 = Pet(pet_id=2, name="Max", species="Cat", age=5)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # 3. Add tasks intentionally OUT OF ORDER to test sort_by_time
    task1 = Task(
        task_id=1,
        pet_name="Luna",
        title="Evening Walk",
        category="walk",
        duration=30,
        priority=3,
        preferred_time="18:30"
    )

    task2 = Task(
        task_id=2,
        pet_name="Luna",
        title="Feed Breakfast",
        category="feeding",
        duration=10,
        priority=5,
        preferred_time="08:00",
        recurrence="daily",
        due_date=date.today(),
    )

    task3 = Task(
        task_id=3,
        pet_name="Max",
        title="Give Medication",
        category="medication",
        duration=5,
        priority=4,
        preferred_time="08:00",
        recurrence="weekly",
        due_date=date.today(),
    )

    task4 = Task(
        task_id=4,
        pet_name="Max",
        title="Evening Playtime",
        category="play",
        duration=20,
        priority=2,
        preferred_time="18:00"
    )

    task5 = Task(
        task_id=5,
        pet_name="Luna",
        title="Afternoon Grooming",
        category="grooming",
        duration=15,
        priority=2,
        preferred_time="14:00"
    )

    task6 = Task(
        task_id=6,
        pet_name="Max",
        title="Midday Snack",
        category="feeding",
        duration=5,
        priority=3,
        preferred_time="12:00"
    )

    # Tasks added out of order: evening first, then morning, then midday
    pet1.add_task(task1)   # 18:30
    pet1.add_task(task5)   # 14:00
    pet1.add_task(task2)   # 08:00
    pet2.add_task(task4)   # 18:00
    pet2.add_task(task3)   # 08:00
    pet2.add_task(task6)   # 12:00

    # 4. Test edit_task
    print("=== Before Edit ===")
    print(f"  task1: title={task1.title}, duration={task1.duration}, priority={task1.priority}")
    pet1.edit_task(task_id=1, duration=45, priority=4)
    print("=== After Edit (duration→45, priority→4) ===")
    print(f"  task1: title={task1.title}, duration={task1.duration}, priority={task1.priority}")

    # 5. Mark a non-recurring task complete the old way
    task1.mark_complete()

    # 6. Build scheduler
    scheduler = Scheduler(owner=owner)

    # --- NEW: Sort by time (chronological view) ---
    print("\n=== Sorted by Time (chronological) ===")
    for task in scheduler.sort_by_time():
        time_str = task.preferred_time or "no time"
        print(f"  {time_str} | [{task.pet_name}] {task.title}")

    # --- NEW: Filter — Luna's tasks only ---
    print("\n=== Filter: Luna's Tasks Only ===")
    for task in scheduler.filter_tasks(pet_name="Luna"):
        status = "done" if task.completed else "pending"
        print(f"  [{task.pet_name}] {task.title} — {status}")

    # --- NEW: Filter — pending tasks only ---
    print("\n=== Filter: Pending Tasks Only ===")
    for task in scheduler.filter_tasks(completed=False):
        print(f"  [{task.pet_name}] {task.title}")

    # --- NEW: Filter — completed tasks only ---
    print("\n=== Filter: Completed Tasks Only ===")
    for task in scheduler.filter_tasks(completed=True):
        print(f"  [{task.pet_name}] {task.title}")

    # --- NEW: Filter — feeding tasks only ---
    print("\n=== Filter: Feeding Tasks Only ===")
    for task in scheduler.filter_tasks(category="feeding"):
        print(f"  [{task.pet_name}] {task.title} at {task.preferred_time}")

    # --- NEW: Filter — Luna's pending tasks (combined filters) ---
    print("\n=== Filter: Luna's Pending Tasks ===")
    for task in scheduler.filter_tasks(pet_name="Luna", completed=False):
        print(f"  {task.title} at {task.preferred_time or 'no time'}")

    # 7. Generate priority-sorted schedule
    scheduler.generate_daily_plan()
    print("\n=== Today's Schedule (priority order) ===")
    for task in scheduler.daily_plan:
        time_str = task.preferred_time if task.preferred_time else "no time"
        print(f"  {time_str} | {task.pet_name} | {task.title} (priority {task.priority})")

    # 8. Conflict detection — two extra tasks to showcase duration-overlap detection
    #    task7: Luna's Vet Check starts at 07:45 for 30 min → ends 08:15
    #           overlaps with Feed Breakfast at 08:00 (different start, same window)
    #    task8: Max's Nail Trim starts at 18:00 for 20 min → exact same slot as Evening Playtime
    task7 = Task(
        task_id=7,
        pet_name="Luna",
        title="Vet Check",
        category="health",
        duration=30,
        priority=5,
        preferred_time="07:45",
    )
    task8 = Task(
        task_id=8,
        pet_name="Max",
        title="Nail Trim",
        category="grooming",
        duration=20,
        priority=3,
        preferred_time="18:00",
    )
    pet1.add_task(task7)
    pet2.add_task(task8)
    scheduler.tasks.extend([task7, task8])

    print("\n=== Conflict Detection (duration-aware) ===")
    warnings = scheduler.warn_conflicts()
    if warnings:
        for msg in warnings:
            print(f"  {msg}")
    else:
        print("  No conflicts found.")

    # 9. Recurring task demo
    print("\n=== Recurring Tasks: complete_and_reschedule ===")

    # task2 = Luna's Feed Breakfast (daily), task3 = Max's Give Medication (weekly)
    for task_id, task in [(task2.task_id, task2), (task3.task_id, task3)]:
        print(f"\n  Completing: [{task.pet_name}] {task.title}")
        print(f"    recurrence={task.recurrence}, due_date={task.due_date}")
        new_task = scheduler.complete_and_reschedule(task_id)
        print(f"    Old task completed: {task.completed}")
        if new_task:
            print(f"    Next occurrence → task_id={new_task.task_id}, due_date={new_task.due_date}")

    print("\n  All tasks after rescheduling:")
    for t in scheduler.sort_by_time():
        status = "done" if t.completed else "pending"
        recur = f" [{t.recurrence}]" if t.recurrence else ""
        due = f" due {t.due_date}" if t.due_date else ""
        print(f"    {t.preferred_time or 'no time'} | [{t.pet_name}] {t.title}{recur}{due} — {status}")

    # 10. Full explanation
    print("\n=== Explanation ===")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
