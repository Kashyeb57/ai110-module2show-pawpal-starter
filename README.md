# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a busy pet owner plan daily care tasks using smart scheduling algorithms.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Features

- **Owner & Pet profiles** — enter owner name, daily time budget, pet name, and species
- **Task management** — add tasks with name, type, duration, priority, and frequency
- **Priority scheduling** — high-priority tasks are always scheduled first
- **Sort by time** — within the same priority, shorter tasks are scheduled first to maximise the number of tasks that fit
- **Recurring tasks** — mark tasks as `daily` or `weekly`; `mark_complete()` auto-resets them and sets the next due date using `timedelta`
- **Conflict warnings** — duplicate task types (e.g. two "feeding" tasks) trigger a plain-English warning in the UI before the plan is generated
- **Filter by pet or status** — retrieve tasks for a specific pet or filter by completion status
- **Explained reasoning** — the app tells the owner why each task was scheduled or skipped

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

## Testing PawPal+

```bash
python -m pytest
```

**What the tests cover (14 tests):**

- Task completion — `mark_complete()` correctly sets `is_completed`
- Task addition — adding tasks to a `Pet` grows its task list
- Sorting correctness — `sort_by_time()` returns tasks shortest-first; `prioritize_tasks()` orders high before low
- Recurrence logic — daily/weekly tasks auto-reset `is_completed` and calculate `next_due` via `timedelta`
- Conflict detection — duplicate `task_type` triggers a warning; unique types return no warnings
- Edge cases — pet with no tasks produces an empty plan; tasks exceeding the time budget appear in `skipped_tasks`
- Filtering — `filter_by_pet()` and `filter_by_status()` return the correct subsets

**Confidence level: 4/5** — all 14 tests pass. The main untested area is the Streamlit UI layer and multi-pet scheduling with larger task sets.

## Optional Extensions Implemented

| Challenge | What was built |
|---|---|
| **1 — Weighted Prioritization** | `Task.urgency_score()` computes a float score (priority weight + frequency bonus − duration penalty). `Scheduler.weighted_generate_plan()` uses this instead of fixed priority tiers. Toggled in the UI. Agent Mode was used to design the scoring formula and integrate it alongside the existing `generate_plan()`. |
| **2 — JSON Persistence** | `Owner.save_to_json()` and `Owner.load_from_json()` use custom `to_dict()`/`from_dict()` methods on all three classes. `app.py` loads `data.json` on startup so pets and tasks survive page refreshes. |
| **3 — Priority Color-Coding** | 🔴 High / 🟡 Medium / 🟢 Low emoji labels in all Streamlit tables. |
| **4 — Professional Formatting** | Task-type emojis (🦮 walk, 🍽️ feeding, 💊 meds, ✂️ grooming, 🧩 enrichment), urgency score column, metric row, and toggle for weighted mode. |
| **5 — Multi-Model Comparison** | Documented in `reflection.md` section 6 — Claude vs GPT-4 style responses for the weekly recurrence logic. |

## Smarter Scheduling

PawPal+ goes beyond a basic task list with four algorithmic features:

- **Sort by time** — tasks sorted shortest-first within same priority, maximising tasks that fit the time budget
- **Filter by pet or status** — retrieve tasks for a specific pet by name, or by completion status
- **Recurring tasks** — `daily`/`weekly` tasks auto-reset after `mark_complete()` using `timedelta`
- **Conflict detection** — flags duplicate `task_type` entries with a warning, without crashing the app

## Project Structure

```
pawpal_system.py   # Backend logic: Owner, Pet, Task, Scheduler, DailyPlan
app.py             # Streamlit UI — connects to backend via session_state
main.py            # CLI demo script to verify backend in terminal
tests/
  test_pawpal.py   # 14 automated pytest tests
uml_final.md       # Final Mermaid.js class diagram
reflection.md      # Design decisions and AI collaboration notes
```

## Suggested Workflow

1. Read the scenario and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
