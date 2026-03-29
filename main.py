from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Whiskers", species="Cat", age=5)

# Tasks added OUT OF ORDER to test sorting
dog.add_task(Task(name="Morning Walk",    task_type="walk",       duration_minutes=30, priority="high",   frequency="daily"))
dog.add_task(Task(name="Flea Medication", task_type="meds",       duration_minutes=5,  priority="high"))
dog.add_task(Task(name="Breakfast",       task_type="feeding",    duration_minutes=10, priority="high",   frequency="daily"))

cat.add_task(Task(name="Puzzle Toy",      task_type="enrichment", duration_minutes=25, priority="low"))
cat.add_task(Task(name="Dinner",          task_type="feeding",    duration_minutes=10, priority="high"))   # conflict: same type as Breakfast
cat.add_task(Task(name="Brushing",        task_type="grooming",   duration_minutes=20, priority="medium", frequency="weekly"))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# --- Sort by time ---
print("=" * 45)
print("  All tasks sorted by duration (shortest first)")
print("=" * 45)
for t in scheduler.sort_by_time(owner.get_all_tasks()):
    recur = f" [{t.frequency}]" if t.frequency else ""
    print(f"  {t.duration_minutes:>3} min  [{t.priority.upper()}]  {t.name}{recur}")

# --- Filter by pet ---
print("\n" + "=" * 45)
print("  Buddy's tasks only")
print("=" * 45)
for t in scheduler.filter_by_pet("Buddy"):
    print(f"  {t.name}  ({t.duration_minutes} min)")

# --- Conflict detection ---
print("\n" + "=" * 45)
print("  Conflict detection")
print("=" * 45)
conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")

# --- Recurring task demo ---
print("\n" + "=" * 45)
print("  Recurring task demo")
print("=" * 45)
walk = scheduler.filter_by_pet("Buddy")[0]   # Morning Walk (daily)
print(f"  Before mark_complete: is_completed={walk.is_completed}, next_due={walk.next_due}")
walk.mark_complete()
print(f"  After  mark_complete: is_completed={walk.is_completed}, next_due={walk.next_due}")

# --- Generate daily plan ---
plan = scheduler.generate_plan()
print("\n" + "=" * 45)
print(f"  Daily Plan ({plan.date})  —  {plan.total_duration}/{owner.available_minutes} min")
print("=" * 45)
for t in plan.scheduled_tasks:
    print(f"  [{t.priority.upper()}]  {t.name:<22} {t.duration_minutes} min")
if plan.skipped_tasks:
    print("\n  Skipped:")
    for t in plan.skipped_tasks:
        print(f"  - {t.name}: {t.reason_skipped}")
print("=" * 45)
