# PawPal+ Final UML Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes
        +String preferences
        +List~Pet~ pets
        +add_pet(pet) void
        +get_available_time() int
        +get_all_tasks() List~Task~
    }

    class Pet {
        +String name
        +String species
        +int age
        +Owner owner
        +List~Task~ tasks
        +add_task(task) void
        +get_info() String
    }

    class Task {
        +String name
        +String task_type
        +int duration_minutes
        +String priority
        +bool is_completed
        +String reason_skipped
        +String frequency
        +date next_due
        +mark_complete() void
    }

    class Scheduler {
        +Owner owner
        +int time_limit
        +prioritize_tasks() List~Task~
        +sort_by_time(tasks) List~Task~
        +filter_by_status(completed) List~Task~
        +filter_by_pet(pet_name) List~Task~
        +detect_conflicts(tasks) List~String~
        +fits_within_time(task, time_used) bool
        +generate_plan() DailyPlan
    }

    class DailyPlan {
        +List~Task~ scheduled_tasks
        +List~Task~ skipped_tasks
        +int total_duration
        +String date
        +display() void
        +explain_reasoning() String
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Owner "1" --> "0..*" Task : get_all_tasks()
    Scheduler --> Owner : uses
    Scheduler --> DailyPlan : produces
    DailyPlan --> "0..*" Task : contains
```

## Changes from initial UML (Phase 1)

| What changed | Why |
|---|---|
| `Task` gained `frequency` and `next_due` | Added in Phase 4 to support recurring tasks |
| `Scheduler` gained `sort_by_time()`, `filter_by_status()`, `filter_by_pet()`, `detect_conflicts()` | Added algorithmic layer in Phase 4 |
| `Owner` gained `get_all_tasks()` | Added so Scheduler stays decoupled from Pet internals |
| `prioritize_tasks()` uses dual sort key (priority + duration) | Tiebreaker added for same-priority tasks |
| Removed single-`pet` constructor on Scheduler | Scheduler now works with all pets via Owner |
