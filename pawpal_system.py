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
        pass

    def update_details(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
        preferred_time: Optional[str] = None,
    ) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_id: int, **updates) -> None:
        pass

    def remove_task(self, task_id: int) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, tasks: Optional[List[Task]] = None) -> None:
        self.tasks: List[Task] = tasks if tasks is not None else []
        self.daily_plan: List[Task] = []

    def sort_tasks_by_priority(self) -> List[Task]:
        pass

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        pass

    def generate_daily_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass