from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
from typing import List, Optional, Tuple


@dataclass
class Task:
    task_id: int
    pet_name: str
    title: str
    category: str
    duration: int
    priority: int
    preferred_time: Optional[str] = None  # expected format: HH:MM
    completed: bool = False
    recurrence: Optional[str] = None   # "daily", "weekly", or None
    due_date: Optional[date] = None    # date this occurrence is due

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update_details(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
        preferred_time: Optional[str] = None,
    ) -> None:
        """Update only the provided fields, leaving others unchanged."""
        if title is not None:
            self.title = title
        if category is not None:
            self.category = category
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if preferred_time is not None:
            self.preferred_time = preferred_time

    def is_high_priority(self) -> bool:
        """Return True if priority is 3 or above."""
        return self.priority >= 3


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def edit_task(self, task_id: int, **updates) -> None:
        """Locate a task by ID and delegate updates to Task.update_details()."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.update_details(**updates)
                return
        raise ValueError(f"Task with id {task_id} not found in {self.name}'s task list.")

    def remove_task(self, task_id: int) -> None:
        """Remove a task by ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        if any(existing.pet_id == pet.pet_id for existing in self.pets):
            raise ValueError(f"Pet with id {pet.pet_id} already exists.")
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by ID from this owner's pet list."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_all_tasks(self) -> List[Task]:
        """Return a flattened list of all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Optional["Owner"] = None, tasks: Optional[List[Task]] = None) -> None:
        """Initialize the Scheduler.

        Args:
            owner: If provided, tasks are pulled from all of the owner's pets
                   via Owner.get_all_tasks(). A reference is kept so that
                   complete_and_reschedule() can write new tasks back to pets.
            tasks: Explicit task list used when no owner is provided (e.g. tests).
        """
        self.owner = owner
        if owner is not None:
            self.tasks: List[Task] = owner.get_all_tasks()
        else:
            self.tasks = tasks if tasks is not None else []
        self.daily_plan: List[Task] = []

    def complete_and_reschedule(self, task_id: int) -> Optional[Task]:
        """Mark a recurring task complete and auto-create the next occurrence.

        Uses timedelta to calculate the next due_date:
          - "daily"  → due_date + 1 day
          - "weekly" → due_date + 7 days

        The new task is added to both the scheduler's task list and, if an
        owner is set, back to the correct pet's task list.

        Returns the newly created Task, or None if the task has no recurrence.
        """
        # Find the task
        target = next((t for t in self.tasks if t.task_id == task_id), None)
        if target is None:
            raise ValueError(f"Task with id {task_id} not found.")

        # Mark this occurrence done
        target.mark_complete()

        if target.recurrence is None:
            return None

        # Calculate next due date using timedelta
        base_date = target.due_date if target.due_date is not None else date.today()
        if target.recurrence == "daily":
            next_due = base_date + timedelta(days=1)
        elif target.recurrence == "weekly":
            next_due = base_date + timedelta(weeks=1)
        else:
            return None  # unknown recurrence value — don't reschedule

        # Assign a new unique ID (one more than the current maximum)
        next_id = max(t.task_id for t in self.tasks) + 1

        new_task = Task(
            task_id=next_id,
            pet_name=target.pet_name,
            title=target.title,
            category=target.category,
            duration=target.duration,
            priority=target.priority,
            preferred_time=target.preferred_time,
            completed=False,
            recurrence=target.recurrence,
            due_date=next_due,
        )

        # Add to scheduler's flat task list
        self.tasks.append(new_task)

        # Add back to the pet so owner.get_all_tasks() stays consistent
        if self.owner is not None:
            for pet in self.owner.pets:
                if pet.name.lower() == new_task.pet_name.lower():
                    pet.add_task(new_task)
                    break

        return new_task

    def sort_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority, highest first."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted chronologically by preferred_time (HH:MM).

        Tasks without a preferred_time are treated as end-of-day (23:59)
        so timed tasks always appear first.
        """
        def time_key(task: Task) -> int:
            if task.preferred_time is None:
                return 23 * 60 + 59
            hours, minutes = task.preferred_time.split(":")
            return int(hours) * 60 + int(minutes)

        return sorted(self.tasks, key=time_key)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks matching all provided filters.

        Args:
            pet_name:  Keep only tasks belonging to this pet (case-insensitive).
            completed: True → completed only, False → pending only, None → all.
            category:  Keep only tasks of this category (case-insensitive).
        """
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if category is not None:
            result = [t for t in result if t.category.lower() == category.lower()]
        return result

    @staticmethod
    def _to_minutes(time_str: str) -> int:
        """Convert 'HH:MM' string to total minutes since midnight."""
        hours, mins = time_str.split(":")
        return int(hours) * 60 + int(mins)

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose time intervals overlap.

        Two tasks conflict when their [start, start+duration) windows intersect:
            start_a < end_b  AND  start_b < end_a

        This catches both exact same-start conflicts and partial overlaps caused
        by task duration (e.g. 08:00+30 min vs 08:15+10 min).
        Only pending (incomplete) tasks are checked.
        """
        conflicts = []
        timed = [t for t in self.tasks if t.preferred_time is not None and not t.completed]
        for a, b in combinations(timed, 2):
            a_start = self._to_minutes(a.preferred_time)
            a_end   = a_start + a.duration
            b_start = self._to_minutes(b.preferred_time)
            b_end   = b_start + b.duration
            if a_start < b_end and b_start < a_end:
                conflicts.append((a, b))
        return conflicts

    def warn_conflicts(self) -> List[str]:
        """Return a list of human-readable warning strings for every conflict.

        Returns an empty list when there are no conflicts, so callers never
        need to handle exceptions — just check if the list is empty.
        """
        warnings = []
        for a, b in self.detect_conflicts():
            a_start = self._to_minutes(a.preferred_time)
            b_start = self._to_minutes(b.preferred_time)
            # Describe overlap kind
            if a_start == b_start:
                overlap_desc = f"both start at {a.preferred_time}"
            else:
                later = b if b_start > a_start else a
                earlier = a if b_start > a_start else b
                overlap_min = (
                    self._to_minutes(earlier.preferred_time) + earlier.duration
                    - self._to_minutes(later.preferred_time)
                )
                overlap_desc = (
                    f"'{earlier.title}' ({earlier.preferred_time}, {earlier.duration} min) "
                    f"runs {overlap_min} min into '{later.title}' ({later.preferred_time})"
                )
            warnings.append(
                f"WARNING: [{a.pet_name}] '{a.title}' conflicts with "
                f"[{b.pet_name}] '{b.title}' — {overlap_desc}"
            )
        return warnings

    def generate_daily_plan(self) -> List[Task]:
        """Generate a daily plan sorted by priority first, time as tiebreaker.

        Tasks with higher priority always appear before lower-priority tasks,
        regardless of whether they have a preferred_time. Within the same
        priority, timed tasks are ordered by time; untimed tasks come last.
        """
        self.daily_plan = sorted(
            self.tasks,
            key=lambda t: (-t.priority, t.preferred_time or "99:99"),
        )
        return self.daily_plan

    def explain_plan(self) -> str:
        """Return a human-readable summary of the daily plan."""
        if not self.daily_plan:
            self.generate_daily_plan()
        if not self.daily_plan:
            return "No tasks scheduled."

        lines = ["Daily Plan:"]
        for i, task in enumerate(self.daily_plan, start=1):
            time_info = f" at {task.preferred_time}" if task.preferred_time else ""
            status = "done" if task.completed else "pending"
            lines.append(
                f"  {i}. [{task.pet_name}] {task.title} ({task.category})"
                f" — {task.duration} min{time_info}, priority {task.priority}, {status}"
            )

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\nConflicts detected:")
            for t1, t2 in conflicts:
                lines.append(f"  - '{t1.title}' and '{t2.title}' both scheduled at {t1.preferred_time}")

        return "\n".join(lines)
