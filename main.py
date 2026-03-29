from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Whiskers", species="Cat", age=5)

# --- Tasks for Buddy (Dog) ---
dog.add_task(Task(name="Morning Walk",     task_type="walk",       duration_minutes=30, priority="high"))
dog.add_task(Task(name="Breakfast",        task_type="feeding",    duration_minutes=10, priority="high"))
dog.add_task(Task(name="Flea Medication",  task_type="meds",       duration_minutes=5,  priority="high"))

# --- Tasks for Whiskers (Cat) ---
cat.add_task(Task(name="Dinner",           task_type="feeding",    duration_minutes=10, priority="high"))
cat.add_task(Task(name="Brushing",         task_type="grooming",   duration_minutes=20, priority="medium"))
cat.add_task(Task(name="Puzzle Toy",       task_type="enrichment", duration_minutes=25, priority="low"))

# --- Add pets to owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Run Scheduler ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

# --- Print Today's Schedule ---
print("=" * 45)
print(f"  PawPal+ — Today's Schedule  ({plan.date})")
print("=" * 45)
print(f"  Owner : {owner.name}")
print(f"  Budget: {owner.available_minutes} min available")
print("-" * 45)

print("\n>> Scheduled Tasks:\n")
for task in plan.scheduled_tasks:
    priority_tag = f"[{task.priority.upper()}]".ljust(8)
    print(f"  {priority_tag} {task.name:<22} {task.duration_minutes} min")

if plan.skipped_tasks:
    print("\n-- Skipped Tasks (not enough time):\n")
    for task in plan.skipped_tasks:
        print(f"  - {task.name:<22} ({task.reason_skipped})")

print("-" * 45)
print(f"\n  Total time used : {plan.total_duration} min")
print(f"  Time remaining  : {owner.available_minutes - plan.total_duration} min")
print("\n" + plan.explain_reasoning())
print("=" * 45)
