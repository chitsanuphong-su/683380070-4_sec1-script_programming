# Week 12 — Final Project: Enhanced Task Manager CLI

## 1. Project Overview
The **Enhanced Task Manager CLI** is a robust, object-oriented, command-line interface application written in Python. It provides comprehensive task management capabilities featuring task specialization (due dates and priorities), categorized tagging, flexible search and filtering, multi-attribute sorting, and atomic JSON persistence.

This project represents the culmination and final implementation of the Task Manager design introduced in Week 11.

---

## 2. Problem Statement
Managing daily responsibilities and project deliverables requires more than a simple linear checklist. Users frequently need to:
- Distinguish between standard actions, deadline-driven commitments, and high-priority tasks.
- Categorize tasks across multiple contexts (e.g., `#work`, `#study`, `#urgent`) using tags.
- Retrieve tasks matching specific search keywords across descriptions and categories.
- Filter task collections using complex, multi-criteria constraints (e.g., only pending tasks due before a target date).
- Sort deliverables dynamically by priority level, due date, or status.
- Ensure data integrity across application restarts without data loss or file corruption.

The Enhanced Task Manager CLI addresses all these needs within a clean, dependency-free architecture adhering to PEP 8 standards and solid software engineering practices.

---

## 3. Learning Objectives
1. **Object-Oriented Programming (OOP):** Master encapsulation, inheritance, method overriding, and polymorphism across task models.
2. **Modular Architecture:** Enforce strict separation of concerns between data models (`task.py`), persistence (`data_persistence.py`), business logic (`task_manager.py`), user interface (`cli_interface.py`), and orchestration (`main.py`).
3. **Data Persistence & Robustness:** Implement safe serialization/deserialization to JSON with atomic file writing and corrupted file preservation.
4. **Data Manipulation:** Construct robust algorithms for case-insensitive partial keyword search, multi-criteria filtering (AND logic), and polymorphic sorting.
5. **Testing & QA:** Develop a comprehensive automated test suite with `pytest` covering unit, edge-case, and CLI interaction behaviors.
6. **Documentation & Presentation Readiness:** Deliver professional project documentation and presentation guides suitable for academic and industry reviews.

---

## 4. Features
* **Comprehensive Task Models:**
  - Standard Task with unique ID, description, completion status, and tags.
  - Specialized `DueDateTask` with ISO date validation (`YYYY-MM-DD`).
  - Specialized `PriorityTask` with normalized priority levels (`High`, `Medium`, `Low`).
* **Tags System:**
  - Tag addition, removal, and automatic deduplication.
  - Whitespace trimming and case-insensitive normalization.
* **Core CRUD Operations:**
  - Add normal, due date, or priority tasks.
  - List all tasks with formatted attribute breakdowns.
  - Complete tasks with idempotency checks.
  - Delete tasks safely by ID.
* **Advanced Keyword Search:**
  - Case-insensitive search across task descriptions and associated tags.
  - Partial substring matching.
  - Duplicate result suppression.
* **Multi-Criteria Filtering:**
  - Filter by completion status (`Completed` / `Pending`).
  - Filter by deadline (`due_date_before` and `due_date_after`).
  - Filter by priority level (`High`, `Medium`, `Low`).
  - Filter by multiple required tags (task must contain *all* specified tags).
* **Flexible Dynamic Sorting:**
  - Sort by ID, Description, Completion Status, Due Date, or Priority.
  - Ascending and descending support.
  - Polymorphic grouping: tasks lacking a specific attribute (e.g., non-dated tasks during date sorting) are deterministically grouped at the end.
  - Stable secondary sorting by `id`.
* **Safe Persistence Layer:**
  - Atomic file writes using temporary files and `os.replace` to prevent corrupted states.
  - Backward compatibility with legacy JSON records lacking `tags`.
  - Corrupted file backup mechanism (`tasks.json.corrupted.bak`).

---

## 5. Task Types & Hierarchy

```text
                  +-------------------+
                  |       Task        |
                  |-------------------|
                  | id: int           |
                  | description: str  |
                  | completed: bool   |
                  | tags: List[str]   |
                  +-------------------+
                            ^
                            |
           +----------------+----------------+
           |                                 |
+---------------------+           +---------------------+
|     DueDateTask     |           |    PriorityTask     |
|---------------------|           |---------------------|
| due_date: date      |           | priority: str       |
+---------------------+           +---------------------+
```

- **`Task`:** Base entity representing a general task.
- **`DueDateTask`:** Extends `Task` with `due_date` stored internally as `datetime.date`.
- **`PriorityTask`:** Extends `Task` with `priority` validated against `["High", "Medium", "Low"]`.

---

## 6. Project Structure

```text
week12/final-task-manager-project/
├── data/
│   └── tasks.json               # Persistent JSON data storage
├── src/
│   ├── __init__.py              # Package initializer
│   ├── task.py                  # Domain models (Task, DueDateTask, PriorityTask)
│   ├── data_persistence.py      # Safe file I/O and JSON serialization
│   ├── task_manager.py          # Business logic (CRUD, search, filter, sort)
│   └── cli_interface.py         # Terminal user interface and input validation
├── tests/
│   ├── test_task.py             # Unit tests for models and tag handling
│   ├── test_data_persistence.py # Persistence and recovery tests
│   ├── test_task_manager.py     # Business logic tests
│   └── test_cli_interface.py    # CLI and mock user interaction tests
├── .gitignore                   # Standard Python Git ignore rules
├── main.py                      # Application entry point
├── PLAN.md                      # Comprehensive development plan and reflection
├── README.md                    # Project documentation
└── requirements.txt             # Project testing dependencies
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.

### Steps
1. Navigate to the project directory:
   ```bash
   cd week12/final-task-manager-project
   ```

2. (Optional) Create and activate a virtual environment:
   - **Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install testing dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 8. How to Run

### Start the Application
Execute `main.py` directly from the project directory:
```bash
python main.py
```

### Run Automated Tests
Execute the comprehensive test suite with `pytest`:
```bash
python -m pytest -q
```

---

## 9. CLI Menu & Navigation

When launched, the application presents the following menu:

```text
--- Enhanced Task Manager Menu ---
1. Add Normal Task
2. Add Due Date Task
3. Add Priority Task
4. List All Tasks
5. Complete Task
6. Delete Task
7. Search Tasks
8. Filter Tasks
9. Sort Tasks
0. Exit
----------------------------------
Enter your choice (0-9):
```

---

## 10. Usage Examples & Workflows

### 10.1 Adding Tasks
- **Normal Task:**
  - Description: `Revise Python lecture slides`
  - Tags: `study, python`
- **Due Date Task:**
  - Description: `Submit Final Project Report`
  - Due Date: `2026-10-31`
  - Tags: `school, urgent`
- **Priority Task:**
  - Description: `Fix critical security vulnerability`
  - Priority: `High`
  - Tags: `work, security`

### 10.2 Searching Tasks
- Keyword: `python` matches `Revise Python lecture slides` (found via description or tag).
- Case-insensitivity: Searching `URGENT` correctly matches `#urgent`.

### 10.3 Filtering Tasks
- **By Completion Status:** Choose `yes` for completed, `no` for pending, or press Enter for all.
- **By Due Date:** Enter boundary dates (`YYYY-MM-DD`) for `due_date_before` or `due_date_after`.
- **By Priority:** Specify `High`, `Medium`, or `Low`.
- **By Tags:** Provide comma-separated tags (e.g. `work, urgent`). The filter enforces **AND** logic (task must contain all tags).

### 10.4 Sorting Tasks
- **Criteria:** `id`, `description`, `completed`, `due_date`, `priority`.
- **Order:** Ascending by default, or descending when `yes` is entered.
- **Example:** Sorting by `priority` orders `High` &rarr; `Medium` &rarr; `Low` &rarr; Tasks without priority.

---

## 11. Week 11 to Week 12 Improvements
| Feature Area | Week 11 Design | Week 12 Final Implementation |
|---|---|---|
| **Tags System** | Planned conceptually | Fully implemented with normalization, deduplication, and display |
| **Search Function** | Basic description match | Dual-scope search across descriptions and tags, partial matching |
| **Filter Function** | Single criterion | Multi-criteria combined filtering with inclusive date ranges and tag intersection |
| **Sort Function** | ID only | 5 sorting criteria with polymorphic grouping and secondary ID sorting |
| **Persistence** | Basic JSON dump | Atomic file replacement (`os.replace`) and corrupted file backup protection |
| **Test Coverage** | None | 39 automated tests covering 100% of functional requirements |

---

## 12. Final Presentation Guide & Demo Script

### 12.1 Presentation Outline (5–7 Minutes)
1. **Introduction & Motivation (1 min):** Project title, objectives, and role of OOP in scalable CLI tools.
2. **Architecture & Design (1.5 min):** Separation of concerns across `task.py`, `data_persistence.py`, `task_manager.py`, and `cli_interface.py`.
3. **Live Demonstration (2.5 min):** Step-by-step feature execution.
4. **Technical Challenges & Solutions (1 min):** Atomic saving, polymorphic sorting keys, and multi-criteria filters.
5. **Q&A Readiness (1 min).**

### 12.2 Step-by-Step Live Demo Scenario
1. **Launch:** Run `python main.py`.
2. **List Existing:** Select `4` to show initial tasks.
3. **Add Tasks:**
   - Select `1` &rarr; Description: `Prepare presentation slides` | Tags: `school, presentation`.
   - Select `2` &rarr; Description: `Submit lab assignment` | Due: `2026-10-25` | Tags: `school, homework`.
   - Select `3` &rarr; Description: `Resolve server outage` | Priority: `High` | Tags: `devops, urgent`.
4. **Search:** Select `7` &rarr; Keyword: `school` (demonstrates matching across both description and tags).
5. **Filter:** Select `8` &rarr; Pending: `no`, Tags: `school` (demonstrates combined filtering).
6. **Sort:** Select `9` &rarr; Criterion: `priority` (demonstrates custom priority ranking High &rarr; Medium &rarr; Low).
7. **Complete:** Select `5` &rarr; Enter task ID (demonstrates status change to `Completed`).
8. **Delete:** Select `6` &rarr; Enter task ID (demonstrates removal).
9. **Exit & Restart:** Select `0` to exit. Re-run `python main.py` and select `4` to verify persistent storage.

### 12.3 Anticipated Presentation Q&A
- **Q: Why use Object-Oriented Programming and inheritance for tasks?**
  *A:* Inheritance allows specialized tasks (`DueDateTask`, `PriorityTask`) to reuse core task attributes (`id`, `description`, `completed`, `tags`) while extending behavior without code duplication. Polymorphic `to_dict()` and `__str__()` methods enable uniform treatment of all task types.
- **Q: How does the application handle invalid or corrupted data files?**
  *A:* `DataPersistence` verifies JSON integrity on startup. If JSON decoding fails, it backs up the file to `tasks.json.corrupted.bak` to prevent data loss and resets in-memory tasks cleanly.
- **Q: How does polymorphic sorting handle mixed task types?**
  *A:* When sorting by `due_date`, non-dated tasks are given `datetime.date.max` (or `min` in reverse) to push them to the end of the collection deterministically, followed by a secondary tie-breaking sort on `task.id`.

---

## 13. Future Enhancements
- **Graphical User Interface (GUI):** Implement a Desktop GUI using Tkinter or PyQt.
- **Database Backend:** Migrate storage from JSON to SQLite or PostgreSQL for relational queries.
- **Due Date Reminders:** Add OS background notifications for approaching deadlines.
- **Recurring Tasks:** Support daily, weekly, or monthly repetition cycles.
- **Export Capabilities:** Support exporting task reports to CSV, Markdown, or PDF.
