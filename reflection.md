# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core user actions:

1. **Add/manage a pet profile** — The user enters basic owner info (name, available time per day) and pet info (name, type/species). This sets the context and constraints for scheduling.
2. **Add/edit care tasks** — The user creates tasks such as walks, feeding, medication, grooming, or enrichment. Each task has at minimum a name, duration (in minutes), and priority level (high/medium/low).
3. **Generate and view a daily plan** — The user triggers the scheduler, which selects and orders tasks that fit within the owner's available time, ranked by priority. The app displays the resulting schedule and explains why tasks were included or excluded.

Five classes were designed:

- **Owner**: Responsible for storing who the owner is and how much daily time they have for pet care. Holds `name`, `available_minutes`, `preferences`, and a list of `pets`. Methods: `add_pet()`, `get_available_time()`.
- **Pet**: Represents the animal being cared for. Holds `name`, `species`, `age`, a back-reference to `owner`, and a list of `tasks`. Method: `get_info()`.
- **Task**: Represents a single care activity. Holds `name`, `task_type`, `duration_minutes`, `priority`, `is_completed`, and `reason_skipped`. Method: `mark_complete()`.
- **Scheduler**: The core logic engine. Takes an `Owner`, a `Pet`, and a list of `Tasks`, and produces a `DailyPlan`. Methods: `generate_plan()`, `prioritize_tasks()`, `fits_within_time()`.
- **DailyPlan**: The output of the scheduler. Holds `scheduled_tasks`, `skipped_tasks`, `total_duration`, and `date`. Methods: `display()`, `explain_reasoning()`.

**b. Design changes**

After an AI review of the skeleton, three issues were identified and fixed:

1. **`Pet` was missing a `tasks` list** — The original design only stored tasks on the `Scheduler`. This created a missing direct relationship between a pet and its care tasks. A `tasks: list[Task]` field was added to `Pet` so the pet directly owns its tasks, matching the UML intent.
2. **`Owner.pets` was untyped** — Changed from `list` to `list[Pet]` for type safety and clarity.
3. **`Task` was missing `reason_skipped`** — `DailyPlan.explain_reasoning()` needs to explain why tasks were skipped, but there was nowhere on the task to store that reason. Added `reason_skipped: Optional[str]` to `Task`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: total available time (owner's daily budget in minutes) and task priority (high/medium/low). Within the same priority level, it uses duration as a tiebreaker — shorter tasks are scheduled first to maximise the number of tasks that fit. Priority was chosen as the primary constraint because skipping a high-priority task (like medication) is more harmful than skipping a low-priority one (like enrichment).

**b. Tradeoffs**

The conflict detector only flags tasks that share the same `task_type` (e.g. two "feeding" tasks), rather than checking for overlapping time windows. This means it catches logical duplicates (feeding a pet twice in one plan) but does not detect time-based overlaps if tasks were assigned explicit start times. This tradeoff is reasonable for this scenario because PawPal+ does not schedule tasks at fixed times — it only builds an ordered list. A lightweight type-based check is sufficient and avoids the complexity of a full interval-overlap algorithm.

---

## 3. AI Collaboration

**a. How you used AI**

AI (Claude Code) was used throughout the project in distinct roles:
- **Phase 1** — brainstorming the UML class diagram and identifying missing relationships (e.g. `Pet` needing a `tasks` list)
- **Phase 2** — generating class skeletons from UML and fleshing out scheduling logic
- **Phase 4** — suggesting algorithmic improvements like the `defaultdict` approach for conflict detection and the dual sort key for `prioritize_tasks()`
- **Phase 5** — drafting the test plan and generating test cases for edge cases like empty pets and budget overflow

The most helpful prompts were specific and scoped: "Based on my skeletons in `pawpal_system.py`, how should the Scheduler retrieve all tasks from the Owner's pets?" gave a clear, actionable answer. Broad prompts like "improve my code" were less useful.

**b. Judgment and verification**

When AI suggested replacing `detect_conflicts()` with a `defaultdict`-based one-liner, the suggestion was reviewed but not accepted. While more compact, the `defaultdict` version grouped all names into lists and returned a single combined message — making it harder to trace which exact pair of tasks conflicted. The explicit `if/else` with a `seen` dict was kept because it produces a clearer per-conflict message and is easier for a new reader to understand. The decision was verified by mentally tracing both versions with the same input and comparing the output messages.

---

## 4. Testing and Verification

**a. What you tested**

14 automated tests were written covering: task completion, task addition, sorting correctness (priority and duration tiebreaker), recurrence logic for daily and weekly tasks, conflict detection with and without duplicates, empty pet edge case, time budget exceeded edge case, and filtering by pet name and completion status. These tests were important because the scheduling logic has several interacting parts — a bug in `prioritize_tasks()` could silently produce a wrong plan without any error, so automated tests catch regressions immediately.

**b. Confidence**

Confidence level: 4/5. All 14 tests pass and cover the core logic paths. The main gaps are: the Streamlit UI layer is not tested (Streamlit doesn't easily support unit tests), and the scheduler has not been stress-tested with large task lists (20+ tasks) or many pets. Edge cases to test next: owner with zero available minutes, two tasks with identical names but different types, and recurring tasks that have already passed their `next_due` date.

---

## 5. Reflection

**a. What went well**

The phased workflow (UML → stubs → logic → tests → UI) worked well. Starting with a CLI demo in `main.py` before touching the Streamlit UI made debugging much faster — problems were caught in plain Python before adding the complexity of a web framework. The test suite gave confidence that refactoring in later phases didn't break earlier work.

**b. What you would improve**

The `Scheduler` currently only works with a flat list of tasks and a single time budget. In a next iteration, it would be redesigned to support time-of-day scheduling (morning/afternoon/evening slots) so tasks like "medication" can be pinned to specific times rather than just ordered by priority. This would require `Task` to gain an optional `preferred_time` field and `Scheduler` to gain a time-slot allocation algorithm.

**c. Key takeaway**

The most important lesson was that AI is most useful as a *reviewer and generator*, not as an *architect*. Whenever AI was given a clear, scoped question with context (a file reference or a specific method), the output was useful and accurate. But the decisions about what classes to create, how they should relate, and which algorithmic tradeoffs to make had to come from a human understanding the problem. The AI filled in code quickly; the human had to decide if that code was solving the right problem.
