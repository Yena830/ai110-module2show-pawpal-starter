# PawPal+ Project Reflection

## 1. System Design
From a system design perspective, I identified three core user actions:

1. Enter and manage basic owner and pet information  
2. Add and edit care tasks for a pet (including duration and priority)  
3. Generate and review a daily care plan based on constraints and task priority  



**a. Initial design**

- Briefly describe your initial UML design.
![alt text](image.png)
- What classes did you include, and what responsibilities did you assign to each?

Based on these actions, I designed four primary classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- `Owner` is responsible for managing user-level data and maintaining a collection of pets.
- `Pet` represents an individual pet and maintains its associated care tasks.
- `Task` models a single care activity (e.g., feeding, walking, medication) and stores attributes such as duration, priority, and scheduling-related metadata.
- `Scheduler` encapsulates all scheduling logic, including sorting tasks by priority, detecting conflicts, and generating a structured daily plan.

This design follows separation of concerns: data is modeled in `Owner`, `Pet`, and `Task`, while all planning and algorithmic logic is centralized in `Scheduler`.




**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed after reviewing the initial class skeleton.

One important change was adding a `pet_name` field to the `Task` class. In the original design, tasks could be collected from multiple pets into a single list, but they no longer clearly indicated which pet they belonged to. Adding `pet_name` makes the generated schedule easier to read and also helps the scheduler explain the daily plan more clearly.

I also introduced a `pet_id` field in the `Pet` class and updated `Owner.remove_pet()` to use this identifier instead of the pet name. This change avoids ambiguity when multiple pets share the same name and makes the system more robust and closer to real-world design practices.

I refined the responsibility of task editing as well. Instead of having both `Pet` and `Task` independently handle updates, I made `Pet.edit_task()` responsible for locating the correct task and delegating the actual modification to `Task.update_details()`. This reduces duplicated logic and keeps responsibilities clearly separated.

Another change was improving how the `Scheduler` retrieves data. Initially, it operated only on a list of tasks passed directly to it. I updated the design so that the `Scheduler` can also be initialized with an `Owner`, allowing it to retrieve tasks through `Owner.get_all_tasks()`. This makes the interaction between components more natural and better reflects the system structure.

I also adjusted the design of conflict detection. I originally planned for `detect_conflicts()` to return a list of tasks, but this did not clearly represent which tasks were in conflict. I updated it to return pairs of conflicting tasks instead, which better captures the relationship between them.

Finally, I refined the scheduling logic. The initial version separated timed and untimed tasks, which could lead to lower-priority tasks appearing earlier. I updated `generate_daily_plan()` to sort tasks by priority first and use `preferred_time` only as a tiebreaker. This ensures that higher-priority tasks are always scheduled first while still respecting time preferences when possible. I also documented that `preferred_time` should follow a consistent `HH:MM` format to make scheduling logic more reliable.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints: **task priority** (1–5 scale), **preferred time** (an optional `HH:MM` string), and **task duration** (in minutes). Priority is treated as the primary sorting key in `generate_daily_plan()`, with `preferred_time` used only as a tiebreaker. Duration is used exclusively by `detect_conflicts()` to compute each task's time window `[start, start + duration)`.

I decided that priority matters most because the core user problem is ensuring that important care tasks — like medication — never get crowded out by lower-stakes activities like playtime. Preferred time is a "nice-to-have": the owner can express a preference, but if two high-priority tasks both want the same slot, the conflict warning puts the decision back in the owner's hands rather than silently reshuffling anything. Duration feeds only the conflict check because a 60-minute walk that starts at 8:00 genuinely blocks tasks scheduled at 8:30, regardless of their priority.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One key tradeoff in the scheduler is using an **O(n²) pair-comparison algorithm** for conflict detection instead of a more efficient data structure like a sorted interval tree.

The current `detect_conflicts()` method compares every unique pair of pending timed tasks using `itertools.combinations(timed, 2)`. For each pair, it converts the `preferred_time` strings to integer minutes and checks whether the two `[start, start+duration)` intervals overlap using the formula `a_start < b_end and b_start < a_end`. This correctly catches both exact same-start conflicts and partial overlaps caused by task duration — a refinement over the original version that only compared time strings.

The tradeoff is performance vs simplicity. An interval tree or a sweep-line algorithm could detect all conflicts in O(n log n) time, which scales better for large task lists. However, for a pet scheduling app where a typical owner manages 5–20 tasks per day, the O(n²) approach is fast enough that the difference is undetectable. The pair-comparison code is also straightforward to read and verify by hand, which matters more in a small app than raw algorithmic efficiency.

A second related tradeoff: the scheduler only flags conflicts as **warnings** (returning plain strings via `warn_conflicts()`) rather than automatically resolving them by shifting tasks. Auto-resolution would require choosing which task to delay and by how much — a decision that depends on the owner's preferences. Returning warnings keeps the owner in control and avoids making silent assumptions about priority.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used VS Code Copilot across three distinct phases, intentionally keeping each phase in a separate chat session to avoid context bleed.

In the **design phase**, I used Copilot Chat to brainstorm the class structure. The most effective prompt pattern was giving it a concrete user story and asking it to propose classes with single responsibilities: "A pet owner wants to see a conflict-free daily care schedule. What classes would you define, and what is each class responsible for?" This produced a clean first draft of `Owner`, `Pet`, `Task`, and `Scheduler` that matched my own intuition, which gave me confidence the separation of concerns was sound.

In the **implementation phase**, Copilot's inline completions (Tab autocomplete) were most effective for filling in boilerplate — `__init__` signatures, `@dataclass`-style attribute assignments, and list comprehensions inside `get_all_tasks()` and `filter_tasks()`. I also used Copilot Chat to generate the initial body of `detect_conflicts()` by describing the interval-overlap condition in plain English, then reviewed and corrected the output.

In the **testing phase**, I prompted Copilot with: "Write pytest tests for these three edge cases: two tasks with identical preferred times, a task with no preferred time, and an owner with no pets." This gave me a solid test scaffold that I then extended by hand to cover the multi-pet scenario and the `warn_conflicts()` formatting.

The most reliably useful prompt pattern throughout was: **describe the contract, not the implementation** — tell Copilot what a function should return given specific inputs, rather than asking it to "write a scheduler." Narrower prompts produced code I could verify and trust more quickly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked Copilot to implement `detect_conflicts()`, its first suggestion compared only the `preferred_time` strings with `==` — flagging two tasks as conflicting only if they had the exact same start time. It did not account for duration at all.

I rejected this because I recognized it would miss a common real-world conflict: a 60-minute walk starting at 08:00 and a feeding task starting at 08:30 overlap by 30 minutes, but their start times are different. The string-equality check would silently let both tasks pass.

I verified my concern by tracing through the logic manually with a small example, then rewrote `detect_conflicts()` to convert `preferred_time` values to integer minutes and apply the standard interval-overlap formula: `a_start < b_end and b_start < a_end`. I then added a specific test case (`test_conflict_detection_partial_overlap`) to confirm the corrected version caught partial overlaps that the original would have missed. This gave me confidence the fix was correct and complete.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the following behaviors:

1. **Owner and pet management** — adding a pet, preventing duplicate pet IDs, and retrieving all tasks across multiple pets via `get_all_tasks()`. These tests matter because the entire scheduling pipeline depends on the data model being consistent; a silent duplicate ID would corrupt the schedule.

2. **Task operations** — adding a task to a pet, editing a task's details through `Pet.edit_task()` → `Task.update_details()`, and marking a task complete. These cover the most common mutations a user will perform through the UI.

3. **Scheduling logic** — verifying that `generate_daily_plan()` produces tasks sorted descending by priority, and that `sort_by_time()` orders tasks chronologically. Correctness here directly determines whether the generated schedule is trustworthy.

4. **Conflict detection** — testing the exact-same-start case, a partial-overlap case (where duration causes the intervals to intersect even though start times differ), and a no-conflict case. These three cases together fully characterize the interval-overlap logic.

5. **Filtering** — verifying that `filter_tasks()` correctly returns only pending tasks, only completed tasks, and only tasks belonging to a specific pet. The UI relies on this to power the status radio and pet dropdown, so filtering bugs would silently show the wrong data.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident the scheduler handles the common cases correctly: the unit tests cover the core happy paths and the most likely edge cases (no preferred time, duplicate start, partial overlap, empty owner). The Streamlit UI has also been manually tested with the multi-pet scenario.

The edge cases I would add next if I had more time are:

- **Tasks that span midnight** — e.g., a task at 23:30 with a 90-minute duration. The current interval math would calculate `end = 1470` minutes, which is > 1440, and the overlap check could produce incorrect results against early-morning tasks.
- **Tasks with the same priority and the same preferred time** — the current tiebreaker in `generate_daily_plan()` is deterministic by insertion order, but the sort stability is not explicitly guaranteed across Python versions.
- **Removing a pet that has tasks** — `Owner.remove_pet()` should either cascade-delete the tasks or raise an error; currently this path has no test coverage.
- **Very large task lists** — not a correctness edge case, but worth a quick performance smoke test to confirm the O(n²) conflict check stays imperceptibly fast up to the expected scale (~50 tasks).


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the clean separation between the data model and the scheduling logic. `Owner`, `Pet`, and `Task` are purely responsible for holding and mutating state, while all algorithmic work — sorting, filtering, conflict detection — lives in `Scheduler`. This made it straightforward to test each class in isolation and meant that changing the conflict-detection algorithm did not require touching any of the data classes. When I later added `sort_by_time()` and `filter_tasks()` to support the Streamlit UI, both methods slotted naturally into `Scheduler` without any restructuring.

The conflict detection improvement was also satisfying — catching it required me to read the AI-generated code critically rather than accepting it at face value, and the end result (interval arithmetic with a focused test case) is noticeably more correct and more auditable than the original string-comparison approach.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The two things I would change in the next iteration are:

1. **Persistent storage.** Right now all data lives in Streamlit session state and disappears on page reload. I would add a lightweight persistence layer — even just serializing the `Owner` object to a JSON file on disk — so users can return to their schedule across sessions.

2. **Conflict resolution, not just detection.** The current design flags conflicts as warnings and leaves resolution to the user. In a real app, I would add a `resolve_conflicts()` method that proposes a reschedule: shift lower-priority conflicting tasks to the next available slot. This would require tracking which time slots are occupied and choosing a reschedule heuristic (e.g., earliest available slot after the conflict window). The design is already well-positioned for this because `Scheduler` owns all the scheduling logic — the change would be additive rather than structural.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that **AI tools are most valuable when you come to them with a clear contract, not a vague goal.** When I gave Copilot a precise description of what a function should return — including input types, output types, and edge case behavior — the suggestions were accurate and useful. When I started a session with a broad prompt like "help me build a scheduler," the suggestions were plausible-sounding but structurally opinionated in ways that did not always match my design.

This means the "lead architect" role is not just about reviewing AI output — it starts before the AI generates anything. Defining the interfaces, naming the responsibilities, and specifying the contracts in advance is the work that makes AI assistance precise instead of generic. The AI accelerated the implementation dramatically, but the quality of the system depended entirely on the clarity of the design I brought to it. Put differently: the AI is an excellent contractor, but only if the architect has already drawn the blueprints.
