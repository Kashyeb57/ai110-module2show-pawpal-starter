from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(*tasks_per_pet, available_minutes=120):
    """Build an Owner with one Pet per tuple of tasks and return a Scheduler."""
    owner = Owner(name="TestOwner", available_minutes=available_minutes)
    for i, tasks in enumerate(tasks_per_pet):
        pet = Pet(name=f"Pet{i}", species="dog", age=1)
        for task in tasks:
            pet.add_task(task)
        owner.add_pet(pet)
    return Scheduler(owner)


# ---------------------------------------------------------------------------
# Original Phase 2 tests (kept)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """One-shot task: mark_complete() sets is_completed to True."""
    task = Task(name="Morning Walk", task_type="walk", duration_minutes=30, priority="high")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Adding tasks to a Pet grows its task list."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Breakfast", task_type="feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Evening Walk", task_type="walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_shortest_first():
    """sort_by_time() returns tasks ordered by duration ascending."""
    tasks = [
        Task(name="Long",   task_type="walk",    duration_minutes=40, priority="high"),
        Task(name="Short",  task_type="feeding", duration_minutes=5,  priority="high"),
        Task(name="Medium", task_type="meds",    duration_minutes=20, priority="high"),
    ]
    scheduler = make_scheduler(tasks)
    sorted_tasks = scheduler.sort_by_time(tasks)
    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == sorted(durations), "Tasks should be sorted shortest to longest"


def test_prioritize_tasks_high_before_low():
    """prioritize_tasks() places high priority tasks before low priority ones."""
    tasks = [
        Task(name="Low task",  task_type="enrichment", duration_minutes=10, priority="low"),
        Task(name="High task", task_type="walk",        duration_minutes=10, priority="high"),
    ]
    scheduler = make_scheduler(tasks)
    result = scheduler.prioritize_tasks()
    assert result[0].priority == "high"
    assert result[1].priority == "low"


def test_prioritize_same_priority_shortest_first():
    """Within same priority, shorter tasks come first."""
    tasks = [
        Task(name="Long high",  task_type="walk",    duration_minutes=30, priority="high"),
        Task(name="Short high", task_type="feeding", duration_minutes=5,  priority="high"),
    ]
    scheduler = make_scheduler(tasks)
    result = scheduler.prioritize_tasks()
    assert result[0].duration_minutes == 5


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_resets_after_complete():
    """Daily task: mark_complete() keeps is_completed=False and sets next_due to tomorrow."""
    task = Task(name="Walk", task_type="walk", duration_minutes=20, priority="high", frequency="daily")
    task.mark_complete()
    assert task.is_completed is False
    assert task.next_due == date.today() + timedelta(days=1)


def test_weekly_task_resets_after_complete():
    """Weekly task: mark_complete() keeps is_completed=False and sets next_due to next week."""
    task = Task(name="Grooming", task_type="grooming", duration_minutes=30, priority="medium", frequency="weekly")
    task.mark_complete()
    assert task.is_completed is False
    assert task.next_due == date.today() + timedelta(weeks=1)


def test_one_shot_task_stays_complete():
    """One-shot task (no frequency): mark_complete() permanently sets is_completed=True."""
    task = Task(name="Vet visit", task_type="meds", duration_minutes=60, priority="high")
    task.mark_complete()
    assert task.is_completed is True
    assert task.next_due is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_duplicate_type():
    """detect_conflicts() returns a warning when two tasks share the same task_type."""
    tasks = [
        Task(name="Breakfast", task_type="feeding", duration_minutes=10, priority="high"),
        Task(name="Dinner",    task_type="feeding", duration_minutes=10, priority="high"),
    ]
    scheduler = make_scheduler(tasks)
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "feeding" in warnings[0]


def test_detect_conflicts_no_duplicates():
    """detect_conflicts() returns an empty list when all task types are unique."""
    tasks = [
        Task(name="Walk",      task_type="walk",    duration_minutes=30, priority="high"),
        Task(name="Breakfast", task_type="feeding", duration_minutes=10, priority="high"),
    ]
    scheduler = make_scheduler(tasks)
    assert scheduler.detect_conflicts(tasks) == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_produces_empty_plan():
    """A pet with no tasks results in an empty scheduled plan."""
    scheduler = make_scheduler([])   # one pet, zero tasks
    plan = scheduler.generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_duration == 0


def test_task_skipped_when_budget_exceeded():
    """Tasks that exceed the time budget appear in skipped_tasks with a reason."""
    tasks = [
        Task(name="Long task", task_type="walk", duration_minutes=90, priority="high"),
    ]
    scheduler = make_scheduler(tasks, available_minutes=30)
    plan = scheduler.generate_plan()
    assert len(plan.scheduled_tasks) == 0
    assert len(plan.skipped_tasks) == 1
    assert plan.skipped_tasks[0].reason_skipped is not None


def test_filter_by_pet_returns_correct_tasks():
    """filter_by_pet() returns only tasks belonging to the named pet."""
    owner = Owner(name="Alex", available_minutes=60)
    dog = Pet(name="Buddy", species="Dog", age=3)
    cat = Pet(name="Whiskers", species="Cat", age=5)
    dog.add_task(Task(name="Walk",   task_type="walk",    duration_minutes=20, priority="high"))
    cat.add_task(Task(name="Dinner", task_type="feeding", duration_minutes=10, priority="high"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)
    buddy_tasks = scheduler.filter_by_pet("Buddy")
    assert len(buddy_tasks) == 1
    assert buddy_tasks[0].name == "Walk"


def test_filter_by_status_incomplete_only():
    """filter_by_status(completed=False) excludes completed tasks."""
    tasks = [
        Task(name="Walk",      task_type="walk",    duration_minutes=20, priority="high"),
        Task(name="Breakfast", task_type="feeding", duration_minutes=10, priority="high"),
    ]
    tasks[0].mark_complete()   # mark Walk as done (one-shot, stays complete)
    scheduler = make_scheduler(tasks)
    incomplete = scheduler.filter_by_status(completed=False)
    assert all(not t.is_completed for t in incomplete)
    assert "Breakfast" in [t.name for t in incomplete]
