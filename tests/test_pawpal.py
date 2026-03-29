from datetime import date, timedelta

import pytest

from pawpal_system import Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Helpers — build fresh objects for each test so tests don't share state
# ---------------------------------------------------------------------------

def make_task(task_id, pet_name, title, category, duration, priority,
              preferred_time=None, completed=False, recurrence=None, due_date=None):
    return Task(
        task_id=task_id,
        pet_name=pet_name,
        title=title,
        category=category,
        duration=duration,
        priority=priority,
        preferred_time=preferred_time,
        completed=completed,
        recurrence=recurrence,
        due_date=due_date,
    )


def make_scheduler(*tasks):
    """Return a Scheduler loaded with the given tasks (no owner needed)."""
    return Scheduler(tasks=list(tasks))


# ---------------------------------------------------------------------------
# Original tests (preserved)
# ---------------------------------------------------------------------------

def test_task_completion():
    task = make_task(1, "Luna", "Walk", "walk", 30, 3, "09:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_to_pet():
    pet = Pet(pet_id=1, name="Luna", species="Dog", age=3)
    task = make_task(1, "Luna", "Feed", "feeding", 10, 5, "08:00")
    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feed"


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """Tasks added in reverse order must come out earliest-first."""
    t1 = make_task(1, "Luna", "Evening Walk",    "walk",    30, 3, "18:00")
    t2 = make_task(2, "Luna", "Afternoon Groom", "groom",   15, 2, "14:00")
    t3 = make_task(3, "Luna", "Morning Feed",    "feeding", 10, 5, "08:00")
    t4 = make_task(4, "Max",  "Early Med",       "med",      5, 4, "07:45")

    scheduler = make_scheduler(t1, t2, t3, t4)
    sorted_tasks = scheduler.sort_by_time()

    times = [t.preferred_time for t in sorted_tasks]
    assert times == ["07:45", "08:00", "14:00", "18:00"], (
        f"Expected chronological order but got: {times}"
    )


def test_sort_by_time_no_preferred_time_goes_last():
    """A task with preferred_time=None must sort after all timed tasks."""
    timed   = make_task(1, "Luna", "Walk",  "walk",    30, 3, "09:00")
    untimed = make_task(2, "Luna", "Groom", "groom",   15, 2, None)

    scheduler = make_scheduler(untimed, timed)   # untimed added first
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0].title == "Walk"
    assert sorted_tasks[-1].title == "Groom"


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) must return only that pet's tasks."""
    luna_task = make_task(1, "Luna", "Walk", "walk", 30, 3, "09:00")
    max_task  = make_task(2, "Max",  "Feed", "feeding", 10, 5, "08:00")

    scheduler = make_scheduler(luna_task, max_task)
    result = scheduler.filter_tasks(pet_name="Luna")

    assert len(result) == 1
    assert result[0].pet_name == "Luna"


def test_filter_completed_returns_only_done_tasks():
    done    = make_task(1, "Luna", "Walk", "walk",    30, 3, "09:00", completed=True)
    pending = make_task(2, "Luna", "Feed", "feeding", 10, 5, "08:00", completed=False)

    scheduler = make_scheduler(done, pending)
    result = scheduler.filter_tasks(completed=True)

    assert len(result) == 1
    assert result[0].title == "Walk"


def test_filter_pending_on_all_pending_list():
    """filter_tasks(completed=True) on an all-pending list must return []."""
    t1 = make_task(1, "Luna", "Walk", "walk", 30, 3, "09:00")
    t2 = make_task(2, "Max",  "Feed", "feeding", 10, 5, "08:00")

    scheduler = make_scheduler(t1, t2)
    result = scheduler.filter_tasks(completed=True)

    assert result == []


def test_filter_nonexistent_pet_returns_empty():
    """Filtering by a pet name that doesn't exist must return [] without crashing."""
    t1 = make_task(1, "Luna", "Walk", "walk", 30, 3, "09:00")

    scheduler = make_scheduler(t1)
    result = scheduler.filter_tasks(pet_name="Ghost")

    assert result == []


def test_filter_combined_pet_and_status():
    """Combined filters must intersect, not union."""
    luna_done    = make_task(1, "Luna", "Walk", "walk",    30, 3, "09:00", completed=True)
    luna_pending = make_task(2, "Luna", "Feed", "feeding", 10, 5, "08:00", completed=False)
    max_pending  = make_task(3, "Max",  "Med",  "med",      5, 4, "07:00", completed=False)

    scheduler = make_scheduler(luna_done, luna_pending, max_pending)
    result = scheduler.filter_tasks(pet_name="Luna", completed=False)

    assert len(result) == 1
    assert result[0].title == "Feed"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_exact_same_start():
    """Two tasks at the same time must be flagged as a conflict."""
    t1 = make_task(1, "Luna", "Feed", "feeding",    10, 5, "08:00")
    t2 = make_task(2, "Max",  "Med",  "medication",  5, 4, "08:00")

    scheduler = make_scheduler(t1, t2)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    titles = {conflicts[0][0].title, conflicts[0][1].title}
    assert titles == {"Feed", "Med"}


def test_detect_conflicts_duration_overlap():
    """07:45+30 min must conflict with 08:00+10 min (different starts, overlapping windows)."""
    early = make_task(1, "Luna", "Vet Check", "health",   30, 5, "07:45")
    later = make_task(2, "Max",  "Breakfast", "feeding",  10, 4, "08:00")

    scheduler = make_scheduler(early, later)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1, (
        "Duration-aware overlap (07:45+30min vs 08:00) should be detected"
    )


def test_detect_conflicts_completed_tasks_ignored():
    """Completed tasks must not be flagged even when times overlap."""
    done    = make_task(1, "Luna", "Walk", "walk",    30, 3, "08:00", completed=True)
    pending = make_task(2, "Max",  "Feed", "feeding", 10, 5, "08:00", completed=False)

    scheduler = make_scheduler(done, pending)
    conflicts = scheduler.detect_conflicts()

    assert conflicts == []


def test_detect_conflicts_no_overlap_returns_empty():
    """Tasks with non-overlapping windows must produce no conflicts."""
    t1 = make_task(1, "Luna", "Walk", "walk",    30, 3, "08:00")   # ends 08:30
    t2 = make_task(2, "Max",  "Feed", "feeding", 10, 5, "09:00")   # starts 09:00

    scheduler = make_scheduler(t1, t2)
    assert scheduler.detect_conflicts() == []


def test_warn_conflicts_returns_strings():
    """warn_conflicts() must return non-empty strings, not exceptions."""
    t1 = make_task(1, "Luna", "Feed", "feeding",    10, 5, "08:00")
    t2 = make_task(2, "Max",  "Med",  "medication",  5, 4, "08:00")

    scheduler = make_scheduler(t1, t2)
    warnings = scheduler.warn_conflicts()

    assert len(warnings) == 1
    assert isinstance(warnings[0], str)
    assert "WARNING" in warnings[0]


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------

def test_complete_and_reschedule_daily():
    """Daily task: next occurrence due_date must be today + 1 day."""
    today = date.today()
    task = make_task(1, "Luna", "Feed", "feeding", 10, 5, "08:00",
                     recurrence="daily", due_date=today)

    scheduler = make_scheduler(task)
    new_task = scheduler.complete_and_reschedule(task_id=1)

    assert task.completed is True
    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False


def test_complete_and_reschedule_weekly():
    """Weekly task: next occurrence due_date must be today + 7 days."""
    today = date.today()
    task = make_task(1, "Max", "Grooming", "groom", 20, 3, "14:00",
                     recurrence="weekly", due_date=today)

    scheduler = make_scheduler(task)
    new_task = scheduler.complete_and_reschedule(task_id=1)

    assert task.completed is True
    assert new_task is not None
    assert new_task.due_date == today + timedelta(weeks=1)


def test_complete_and_reschedule_non_recurring_returns_none():
    """Non-recurring task: method must return None and still mark the task done."""
    task = make_task(1, "Luna", "One-off Vet", "health", 30, 5, "10:00",
                     recurrence=None)

    scheduler = make_scheduler(task)
    result = scheduler.complete_and_reschedule(task_id=1)

    assert result is None
    assert task.completed is True


def test_complete_and_reschedule_invalid_id_raises():
    """Passing a non-existent task_id must raise ValueError."""
    task = make_task(1, "Luna", "Walk", "walk", 30, 3, "09:00")
    scheduler = make_scheduler(task)

    with pytest.raises(ValueError):
        scheduler.complete_and_reschedule(task_id=999)


def test_complete_and_reschedule_new_task_inherits_details():
    """The rescheduled task must carry the same title, category, and time."""
    today = date.today()
    task = make_task(1, "Luna", "Evening Walk", "walk", 45, 4, "18:30",
                     recurrence="daily", due_date=today)

    scheduler = make_scheduler(task)
    new_task = scheduler.complete_and_reschedule(task_id=1)

    assert new_task.title == "Evening Walk"
    assert new_task.category == "walk"
    assert new_task.preferred_time == "18:30"
    assert new_task.duration == 45
    assert new_task.recurrence == "daily"


# ---------------------------------------------------------------------------
# generate_daily_plan
# ---------------------------------------------------------------------------

def test_generate_daily_plan_priority_over_time():
    """A high-priority late task must appear before a low-priority early task."""
    early_low  = make_task(1, "Max",  "Playtime", "play",    20, 2, "08:00")
    late_high  = make_task(2, "Luna", "Medication", "med",    5, 5, "18:00")

    scheduler = make_scheduler(early_low, late_high)
    plan = scheduler.generate_daily_plan()

    assert plan[0].title == "Medication", (
        "Priority 5 task must be first regardless of time"
    )


def test_generate_daily_plan_empty_task_list():
    """An empty task list must produce an empty plan without crashing."""
    scheduler = make_scheduler()
    plan = scheduler.generate_daily_plan()
    assert plan == []
