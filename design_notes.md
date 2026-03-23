# PawPal+ System Design — Step 2: Building Blocks

## Overview

This section outlines the core objects in the PawPal+ system and defines their responsibilities, attributes, and methods. The goal is to model the system using clear object-oriented design before implementing the logic.

The system is built around four main classes:
- Owner
- Pet
- Task
- Scheduler

Each class is designed with a single responsibility to maintain modularity and separation of concerns.

---

## 1. Owner

### Responsibility
Represents the user of the system and manages a collection of pets.

### Attributes
- `name`: str — name of the owner
- `pets`: List[Pet] — list of pets owned by the user

### Methods
- `add_pet(pet: Pet)` — add a new pet
- `remove_pet(pet_name: str)` — remove a pet by name
- `get_all_tasks() -> List[Task]` — retrieve all tasks across all pets

---

## 2. Pet

### Responsibility
Represents an individual pet and stores its associated care tasks.

### Attributes
- `name`: str — pet name
- `species`: str — type of pet (e.g., dog, cat)
- `age`: int — age of the pet
- `tasks`: List[Task] — list of tasks assigned to this pet

### Methods
- `add_task(task: Task)` — assign a new task to the pet
- `edit_task(task_id: int, ...)` — update task details
- `remove_task(task_id: int)` — delete a task
- `get_tasks() -> List[Task]` — retrieve all tasks for this pet

---

## 3. Task

### Responsibility
Represents a single care activity such as feeding, walking, or medication.

### Attributes
- `task_id`: int — unique identifier for the task
- `title`: str — task name (e.g., "Feed Luna")
- `category`: str — type of task (feeding, walk, medication, etc.)
- `duration`: int — estimated duration (minutes)
- `priority`: int — priority level (higher = more important)
- `preferred_time`: str — preferred execution time (optional)
- `completed`: bool — whether the task is completed

### Methods
- `mark_complete()` — mark the task as completed
- `update_details(...)` — update task attributes
- `is_high_priority() -> bool` — check if task is high priority

---

## 4. Scheduler

### Responsibility
Handles all scheduling logic, including sorting tasks, detecting conflicts, and generating a daily plan.

### Attributes
- `tasks`: List[Task] — list of all tasks to schedule
- `daily_plan`: List[Task] — generated daily schedule

### Methods
- `sort_tasks_by_priority()` — sort tasks based on priority
- `detect_conflicts()` — identify time conflicts between tasks
- `generate_daily_plan()` — create a structured daily schedule
- `explain_plan() -> str` — provide reasoning for scheduling decisions

---

## Design Notes

- The system separates **data models** (`Owner`, `Pet`, `Task`) from **business logic** (`Scheduler`).
- Each class has a clear and focused responsibility.
- The `Scheduler` is designed to be extendable for more advanced logic (e.g., time constraints, optimization strategies).
- This structure supports scalability and maintainability.

---