from pawpal_system import Task, Pet


def test_task_completion():
    # Create a task
    task = Task(
        task_id=1,
        pet_name="Luna",
        title="Walk",
        category="walk",
        duration=30,
        priority=3,
        preferred_time="09:00"
    )

    # Initially not completed
    assert task.completed is False

    # Mark complete
    task.mark_complete()

    # Verify
    assert task.completed is True


def test_add_task_to_pet():
    # Create pet
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=3)

    # Create task
    task = Task(
        task_id=1,
        pet_name="Luna",
        title="Feed",
        category="feeding",
        duration=10,
        priority=5,
        preferred_time="08:00"
    )

    # Initially no tasks
    assert len(pet.tasks) == 0

    # Add task
    pet.add_task(task)

    # Verify task count increased
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feed"