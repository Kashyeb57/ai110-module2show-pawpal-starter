from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import json

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# Weighted score: higher = more urgent. Used by weighted_generate_plan().
PRIORITY_WEIGHT = {"high": 10, "medium": 5, "low": 1}
FREQUENCY_WEIGHT = {"daily": 4, "weekly": 2}   # recurring tasks get urgency bonus


@dataclass
class Task:
    name: str
    task_type: str          # walk, feeding, meds, grooming, enrichment
    duration_minutes: int
    priority: str           # high, medium, low
    is_completed: bool = False
    reason_skipped: Optional[str] = None
    frequency: Optional[str] = None     # "daily", "weekly", or None (one-shot)
    next_due: Optional[date] = None     # next date this task is due

    def mark_complete(self) -> None:
        """Mark task complete; if recurring, reset and set next due date automatically."""
        self.is_completed = True
        if self.frequency == "daily":
            self.next_due = date.today() + timedelta(days=1)
            self.is_completed = False
        elif self.frequency == "weekly":
            self.next_due = date.today() + timedelta(weeks=1)
            self.is_completed = False

    def urgency_score(self) -> float:
        """Compute a weighted urgency score: higher = schedule sooner.

        Score = priority_weight + frequency_bonus - duration_penalty.
        Duration penalty prevents very long low-value tasks from crowding
        out multiple shorter high-value ones.
        """
        p_score = PRIORITY_WEIGHT.get(self.priority, 0)
        f_score = FREQUENCY_WEIGHT.get(self.frequency or "", 0)
        duration_penalty = self.duration_minutes / 60.0   # 1 point per hour
        return p_score + f_score - duration_penalty

    def to_dict(self) -> dict:
        """Serialise task to a plain dictionary for JSON storage."""
        return {
            "name": self.name,
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "is_completed": self.is_completed,
            "reason_skipped": self.reason_skipped,
            "frequency": self.frequency,
            "next_due": str(self.next_due) if self.next_due else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """Deserialise a Task from a plain dictionary."""
        return Task(
            name=data["name"],
            task_type=data["task_type"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            is_completed=data.get("is_completed", False),
            reason_skipped=data.get("reason_skipped"),
            frequency=data.get("frequency"),
            next_due=date.fromisoformat(data["next_due"]) if data.get("next_due") else None,
        )


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

    def to_dict(self) -> dict:
        """Serialise pet (without owner back-reference) to a dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @staticmethod
    def from_dict(data: dict) -> "Pet":
        """Deserialise a Pet from a plain dictionary."""
        pet = Pet(name=data["name"], species=data["species"], age=data["age"])
        for t in data.get("tasks", []):
            pet.add_task(Task.from_dict(t))
        return pet


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

    def to_dict(self) -> dict:
        """Serialise owner and all pets/tasks to a dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "preferences": self.preferences,
            "pets": [p.to_dict() for p in self.pets],
        }

    @staticmethod
    def from_dict(data: dict) -> "Owner":
        """Deserialise an Owner (and nested pets/tasks) from a dictionary."""
        owner = Owner(
            name=data["name"],
            available_minutes=data["available_minutes"],
            preferences=data.get("preferences"),
        )
        for p in data.get("pets", []):
            owner.add_pet(Pet.from_dict(p))
        return owner

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Persist the owner, all pets, and all tasks to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_json(filepath: str = "data.json") -> "Owner":
        """Load and reconstruct an Owner from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return Owner.from_dict(data)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.time_limit = owner.get_available_time()

    def prioritize_tasks(self) -> list[Task]:
        """Sort all tasks by priority (high → medium → low), then shortest duration first."""
        tasks = [t for t in self.owner.get_all_tasks() if not t.is_completed]
        return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by duration, shortest first."""
        return sorted(tasks, key=lambda t: t.duration_minutes)

    def filter_by_status(self, completed: bool = False) -> list[Task]:
        """Return all tasks matching the given completion status across all pets."""
        return [t for t in self.owner.get_all_tasks() if t.is_completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return tasks belonging to the pet with the given name (case-insensitive)."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for duplicate task types in the given task list."""
        seen: dict[str, str] = {}
        warnings: list[str] = []
        for task in tasks:
            if task.task_type in seen:
                warnings.append(
                    f"Conflict: '{task.name}' and '{seen[task.task_type]}' "
                    f"are both '{task.task_type}' tasks"
                )
            else:
                seen[task.task_type] = task.name
        return warnings

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

    def weighted_generate_plan(self) -> "DailyPlan":
        """Schedule tasks using weighted urgency scores instead of fixed priority tiers.

        Each task gets a float score: priority_weight + frequency_bonus - duration_penalty.
        Tasks are sorted highest score first, then scheduled greedily within the time budget.
        This rewards recurring high-priority short tasks over long low-priority one-offs.
        """
        tasks = [t for t in self.owner.get_all_tasks() if not t.is_completed]
        ranked: list[Task] = sorted(tasks, key=lambda t: t.urgency_score(), reverse=True)
        scheduled: list[Task] = []
        skipped: list[Task] = []
        time_used: int = 0

        for task in ranked:
            if self.fits_within_time(task, time_used):
                scheduled.append(task)
                time_used = time_used + task.duration_minutes  # type: ignore[operator]
            else:
                time_left: int = self.time_limit - time_used  # type: ignore[operator]
                task.reason_skipped = (
                    f"Score {task.urgency_score():.1f} — not enough time "
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
            print(f"  [{task.priority.upper()}] {task.name} - {task.duration_minutes} min")
        if self.skipped_tasks:
            print("\nSkipped tasks:")
            for task in self.skipped_tasks:
                print(f"  {task.name} - {task.reason_skipped}")

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
