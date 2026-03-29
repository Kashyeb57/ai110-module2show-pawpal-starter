from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Optional[str] = None
    pets: list = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        pass

    def get_available_time(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Optional["Owner"] = None

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    name: str
    task_type: str  # walk, feeding, meds, grooming, enrichment
    duration_minutes: int
    priority: str   # high, medium, low
    is_completed: bool = False

    def mark_complete(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.time_limit = owner.available_minutes

    def generate_plan(self) -> "DailyPlan":
        pass

    def prioritize_tasks(self) -> list[Task]:
        pass

    def fits_within_time(self, task: Task) -> bool:
        pass


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0
    date: str = ""

    def display(self) -> None:
        pass

    def explain_reasoning(self) -> str:
        pass
