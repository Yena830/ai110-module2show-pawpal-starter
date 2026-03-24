from dataclasses import dataclass, field
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
        if owner is not None:
            self.tasks: List[Task] = owner.get_all_tasks()
        else:
            self.tasks = tasks if tasks is not None else []
        self.daily_plan: List[Task] = []

    def sort_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority, highest first."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks that share the same preferred_time."""
        conflicts = []
        timed_tasks = [t for t in self.tasks if t.preferred_time is not None]
        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                if timed_tasks[i].preferred_time == timed_tasks[j].preferred_time:
                    conflicts.append((timed_tasks[i], timed_tasks[j]))
        return conflicts

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
