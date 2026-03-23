# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

From a system design perspective, I identified three core user actions:

1. Enter and manage basic owner and pet information  
2. Add and edit care tasks for a pet (including duration and priority)  
3. Generate and review a daily care plan based on constraints and task priority  

Based on these actions, I designed four primary classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- `Owner` is responsible for managing user-level data and maintaining a collection of pets.
- `Pet` represents an individual pet and maintains its associated care tasks.
- `Task` models a single care activity (e.g., feeding, walking, medication) and stores attributes such as duration, priority, and scheduling-related metadata.
- `Scheduler` encapsulates all scheduling logic, including sorting tasks by priority, detecting conflicts, and generating a structured daily plan.

This design follows separation of concerns: data is modeled in `Owner`, `Pet`, and `Task`, while all planning and algorithmic logic is centralized in `Scheduler`.

![alt text](image.png)


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
