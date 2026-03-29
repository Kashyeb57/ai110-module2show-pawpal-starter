# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

**What the tests cover:**

- Task completion — `mark_complete()` correctly sets `is_completed`
- Task addition — adding tasks to a `Pet` grows its task list
- Sorting correctness — `sort_by_time()` returns tasks shortest-first; `prioritize_tasks()` orders high before low
- Recurrence logic — daily/weekly tasks auto-reset `is_completed` and calculate `next_due` via `timedelta`
- Conflict detection — duplicate `task_type` in a plan triggers a warning; unique types return no warnings
- Edge cases — pet with no tasks produces an empty plan; tasks exceeding the time budget appear in `skipped_tasks`
- Filtering — `filter_by_pet()` and `filter_by_status()` return the correct subsets

**Confidence level: ⭐⭐⭐⭐ (4/5)** — all 14 tests pass. The main untested area is the Streamlit UI layer and multi-pet scheduling with larger task sets.

---

## Smarter Scheduling

PawPal+ goes beyond a basic task list with four algorithmic features:

- **Sort by time** — tasks are sorted shortest-first within the same priority level, maximising the number of tasks that fit in the owner's daily time budget.
- **Filter by pet or status** — retrieve tasks for a specific pet by name, or filter by completion status (completed vs. pending).
- **Recurring tasks** — tasks can be marked `daily` or `weekly`. Calling `mark_complete()` on a recurring task automatically resets it and calculates the next due date using `timedelta`.
- **Conflict detection** — the scheduler scans the task list for duplicate `task_type` entries and returns plain-English warnings (e.g. two "feeding" tasks in the same plan), without crashing the app.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
