classDiagram
    class Owner {
        +name: str
        +pets: List[Pet]
        +add_pet(pet: Pet)
        +remove_pet(pet_id: int)
        +get_all_tasks() List[Task]
    }

    class Pet {
        +pet_id: int
        +name: str
        +species: str
        +age: int
        +tasks: List[Task]
        +add_task(task: Task)
        +edit_task(task_id: int, **updates)
        +remove_task(task_id: int)
        +get_tasks() List[Task]
    }

    class Task {
        +task_id: int
        +pet_name: str
        +title: str
        +category: str
        +duration: int
        +priority: int
        +preferred_time: Optional[str]
        +completed: bool
        +recurrence: Optional[str]
        +due_date: Optional[date]
        +mark_complete()
        +update_details(**kwargs)
        +is_high_priority() bool
    }

    class Scheduler {
        +owner: Optional[Owner]
        +tasks: List[Task]
        +daily_plan: List[Task]
        +__init__(owner, tasks)
        +sort_tasks_by_priority() List[Task]
        +sort_by_time() List[Task]
        +filter_tasks(pet_name, completed, category) List[Task]
        +detect_conflicts() List[Tuple]
        +warn_conflicts() List[str]
        +complete_and_reschedule(task_id: int) Optional[Task]
        +generate_daily_plan() List[Task]
        +explain_plan() str
        -_to_minutes(time_str: str) int
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler "0..1" --> "0..1" Owner : references
    Scheduler ..> Task : sorts / filters / schedules
