# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core user actions:

1. **Add/manage a pet profile** — The user enters basic owner info (name, available time per day) and pet info (name, type/species). This sets the context and constraints for scheduling.
2. **Add/edit care tasks** — The user creates tasks such as walks, feeding, medication, grooming, or enrichment. Each task has at minimum a name, duration (in minutes), and priority level (high/medium/low).
3. **Generate and view a daily plan** — The user triggers the scheduler, which selects and orders tasks that fit within the owner's available time, ranked by priority. The app displays the resulting schedule and explains why tasks were included or excluded.

Building blocks:

- **Owner**: Holds `name` and `available_minutes` (daily time budget for pet care). Can `add_pet()` and `get_available_time()`.
- **Pet**: Holds `name`, `species`, `age`, and a reference to its `owner`. Can `get_info()`.
- **Task**: Holds `name`, `task_type` (walk/feeding/meds/grooming/enrichment), `duration_minutes`, `priority` (high/medium/low), and `is_completed`. Can `mark_complete()`.
- **Scheduler**: Holds references to `owner`, `pet`, and a list of `tasks`. Can `generate_plan()`, `prioritize_tasks()`, and `fits_within_time(task)`.
- **DailyPlan**: Holds `scheduled_tasks`, `skipped_tasks`, `total_duration`, and `date`. Can `display()` and `explain_reasoning()`.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
