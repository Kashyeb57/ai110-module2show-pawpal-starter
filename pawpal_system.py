from dataclasses import dataclass, field
from datetime import date
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    task_type: str          # walk, feeding, meds, grooming, enrichment
    duration_minutes: int
    priority: str           # high, medium, low
    is_completed: bool = False
    reason_skipped: Optional[str] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Optional["Owner"] = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)

    def get_info(self) -> str:
        """Return a human-readable summary of this pet's details."""
        return f"{self.name} ({self.species}, age {self.age})"


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Optional[str] = None
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner and set the back-reference."""
        pet.owner = self
        self.pets.append(pet)

    def get_available_time(self) -> int:
        """Return the owner's total available minutes for pet care today."""
        return self.available_minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect all tasks from all pets owned by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.time_limit = owner.get_available_time()

    def prioritize_tasks(self) -> list[Task]:
        """Sort all tasks by priority (high → medium → low), skipping completed ones."""
        tasks = [t for t in self.owner.get_all_tasks() if not t.is_completed]
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def fits_within_time(self, task: Task, time_used: int) -> bool:
        """Return True if the task fits within the remaining available time."""
        return time_used + task.duration_minutes <= self.time_limit

    def generate_plan(self) -> "DailyPlan":
        """Greedily schedule tasks in priority order until time runs out."""
        sorted_tasks: list[Task] = self.prioritize_tasks()
        scheduled: list[Task] = []
        skipped: list[Task] = []
        time_used: int = 0

        for task in sorted_tasks:
            if self.fits_within_time(task, time_used):
                scheduled.append(task)
                time_used = time_used + task.duration_minutes  # type: ignore[operator]
            else:
                time_left: int = self.time_limit - time_used  # type: ignore[operator]
                task.reason_skipped = (
                    f"Not enough time remaining "
                    f"({time_left} min left, needs {task.duration_minutes} min)"
                )
                skipped.append(task)

        return DailyPlan(
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            total_duration=time_used,
            date=str(date.today()),
        )


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0
    date: str = ""

    def display(self) -> None:
        """Print the daily plan in a readable format to the terminal."""
        print(f"\n=== PawPal+ Daily Plan ({self.date}) ===")
        print(f"Total scheduled time: {self.total_duration} minutes\n")
        print("Scheduled tasks:")
        for task in self.scheduled_tasks:
            print(f"  [{task.priority.upper()}] {task.name} — {task.duration_minutes} min")
        if self.skipped_tasks:
            print("\nSkipped tasks:")
            for task in self.skipped_tasks:
                print(f"  {task.name} — {task.reason_skipped}")

    def explain_reasoning(self) -> str:
        """Return a plain-English explanation of why tasks were scheduled or skipped."""
        lines = [
            f"Tasks were selected by priority (high first) and fit within "
            f"{self.total_duration} minutes of available time."
        ]
        if self.skipped_tasks:
            lines.append(f"{len(self.skipped_tasks)} task(s) were skipped due to time constraints:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.name}: {task.reason_skipped}")
        return "\n".join(lines)
