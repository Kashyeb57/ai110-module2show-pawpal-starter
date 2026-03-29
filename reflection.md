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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
