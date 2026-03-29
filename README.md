# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Phase 3 of this project extended the `Scheduler` class with four algorithmic improvements:

**Chronological sorting** — `sort_by_time()` converts each task's `preferred_time` string (`"HH:MM"`) to total minutes since midnight and sorts ascending. Tasks with no preferred time are treated as end-of-day (`23:59`) so they always appear last.

**Flexible filtering** — `filter_tasks(pet_name, completed, category)` accepts any combination of optional filters and applies them in sequence using list comprehensions. Passing no arguments returns all tasks; passing multiple arguments narrows the result to tasks matching every filter (case-insensitive).

**Recurring tasks** — `Task` now carries `recurrence` (`"daily"` or `"weekly"`) and `due_date` fields. Calling `Scheduler.complete_and_reschedule(task_id)` marks the current occurrence done and automatically creates the next one using Python's `timedelta`:
- daily → `due_date + timedelta(days=1)`
- weekly → `due_date + timedelta(weeks=1)`

The new task is registered with both the scheduler's flat list and the pet's own task list so everything stays in sync.

**Duration-aware conflict detection** — `detect_conflicts()` now checks whether task time *windows* overlap rather than comparing start-time strings. Two tasks conflict when `start_a < end_b and start_b < end_a`, catching partial overlaps (e.g. an 08:00+30 min task and an 08:15+10 min task) that the original exact-match check would miss. `warn_conflicts()` wraps this in plain English warning strings so the caller never needs to handle exceptions.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
