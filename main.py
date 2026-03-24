from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # 1. Create Owner
    owner = Owner("Alice")

    # 2. Create Pets
    pet1 = Pet(pet_id=1, name="Luna", species="Dog", age=3)
    pet2 = Pet(pet_id=2, name="Max", species="Cat", age=5)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # 3. Create Tasks (task2 and task3 share 08:00 — intentional conflict)
    task1 = Task(
        task_id=1,
        pet_name="Luna",
        title="Morning Walk",
        category="walk",
        duration=30,
        priority=3,
        preferred_time="09:00"
    )

    task2 = Task(
        task_id=2,
        pet_name="Luna",
        title="Feed Breakfast",
        category="feeding",
        duration=10,
        priority=5,
        preferred_time="08:00"
    )

    task3 = Task(
        task_id=3,
        pet_name="Max",
        title="Give Medication",
        category="medication",
        duration=5,
        priority=4,
        preferred_time="08:00"
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

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)
    pet2.add_task(task4)

    # 4. Test edit_task — update Luna's walk duration and priority
    print("=== Before Edit ===")
    print(f"  task1: title={task1.title}, duration={task1.duration}, priority={task1.priority}")
    pet1.edit_task(task_id=1, duration=45, priority=4)
    print("=== After Edit (duration→45, priority→4) ===")
    print(f"  task1: title={task1.title}, duration={task1.duration}, priority={task1.priority}")

    # 5. Test mark_complete and is_high_priority
    print("\n=== Task Status ===")
    task2.mark_complete()
    for task in owner.get_all_tasks():
        flag = "HIGH" if task.is_high_priority() else "normal"
        status = "done" if task.completed else "pending"
        print(f"  [{task.pet_name}] {task.title} — {flag}, {status}")

    # 6. Generate Schedule via Owner
    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan()

    print("\n=== Today's Schedule ===")
    for task in scheduler.daily_plan:
        time_str = task.preferred_time if task.preferred_time else "no time"
        print(f"  {time_str} | {task.pet_name} | {task.title} (priority {task.priority})")

    # 7. Detect conflicts
    print("\n=== Conflict Detection ===")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for t1, t2 in conflicts:
            print(f"  CONFLICT: '{t1.title}' and '{t2.title}' both at {t1.preferred_time}")
    else:
        print("  No conflicts found.")

    # 8. Full explanation
    print("\n=== Explanation ===")
    print(scheduler.explain_plan())

    # 9. Test remove_task and remove_pet
    print("\n=== After Removing task1 from Luna ===")
    pet1.remove_task(task_id=1)
    print(f"  Luna's tasks: {[t.title for t in pet1.get_tasks()]}")

    owner.remove_pet(pet_id=2)
    print(f"  Owner's pets after removing Max: {[p.name for p in owner.pets]}")


if __name__ == "__main__":
    main()
