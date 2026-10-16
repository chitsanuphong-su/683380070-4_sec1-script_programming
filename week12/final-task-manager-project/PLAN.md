# Project Plan: Enhanced Task Manager CLI (Final Version)

## 1. Introduction
This document serves as the architectural blueprint and developmental record for the **Enhanced Command-Line Interface (CLI) Task Manager Application**. Originating from the foundational design developed in Week 11, this document reflects the fully realized, tested, and validated final implementation completed for Week 12.

The application showcases the practical application of core software engineering disciplines in Python: Object-Oriented Programming (encapsulation, inheritance, polymorphism), modular software architecture, resilient JSON data persistence, robust input validation, advanced query algorithms (search, multi-criteria filtering, polymorphic sorting), and automated test-driven verification.

---

## 2. Project Objectives
- Build a modular, decoupled Python command-line utility with zero external runtime dependencies.
- Deliver specialized task domain models inheriting from a base `Task` class.
- Provide full tag categorization, keyword search, complex filtering, and dynamic multi-attribute sorting.
- Implement fail-safe JSON persistence with atomic writes and corruption prevention.
- Maintain an automated test suite achieving 100% functional test coverage.
- Prepare clear documentation, demonstration scripts, and presentation materials.

---

## 3. Functional Requirements
1. **Core Task Management (CRUD):**
   - Create standard tasks with unique auto-incrementing integer IDs and descriptions.
   - Create `DueDateTask` objects with ISO `YYYY-MM-DD` date validation.
   - Create `PriorityTask` objects with normalized priorities (`High`, `Medium`, `Low`).
   - Support optional categorization tags (normalized lowercase strings with whitespace trimming and deduplication).
   - List all tasks with clear formatted attribute representations.
   - Mark tasks as completed with status verification.
   - Delete tasks by ID with persistence updates.
2. **Advanced Task Retrieval:**
   - **Keyword Search:** Case-insensitive, partial-match search spanning both task descriptions and tag collections without duplicate entries.
   - **Multi-Criteria Filter:** Simultaneous combination of completion status, date ranges (`due_date_before`, `due_date_after`), priority levels, and tag requirements (AND logic).
   - **Dynamic Sorting:** Flexible ordering by ID, description, completion status, due date, and priority, handling mixed task types deterministically.
3. **Data Persistence:**
   - Automatic loading from `data/tasks.json` upon initialization.
   - Backward compatibility for legacy task records missing tag attributes.
   - Atomic disk writes to prevent file corruption during save operations.
   - Corrupted file backup creation (`tasks.json.corrupted.bak`).

---

## 4. Non-Functional Requirements
- **Usability:** Clean, intuitive terminal menus and explanatory prompts for invalid inputs.
- **Reliability:** Graceful handling of invalid date strings, unrecognized priorities, non-numeric task IDs, empty descriptions, and terminal interruptions (`KeyboardInterrupt`, `EOFError`).
- **Maintainability:** Adherence to PEP 8 style standards, descriptive docstrings, type annotations, and modular decoupling.
- **Extensibility:** Open for extension (e.g., adding new task types or persistence backends) without modifying core interfaces.
- **Performance:** Sub-millisecond response times for local collections.

---

## 5. System Architecture & Module Responsibilities

```text
                           +------------------+
                           |     main.py      |
                           +------------------+
                                     |
                                     v
                           +------------------+
                           |   CLIInterface   |
                           +------------------+
                                     |
                                     v
                           +------------------+
                           |   TaskManager    |
                           +------------------+
                               /            \
                              /              \
                             v                v
                 +-------------------+   +--------------------+
                 |    Task Models    |   |  DataPersistence   |
                 | Task, DueDateTask |   |  data/tasks.json   |
                 |   PriorityTask    |   +--------------------+
                 +-------------------+
```

- **`src/task.py` (Domain Layer):** Encapsulates the domain models (`Task`, `DueDateTask`, `PriorityTask`). Provides constructor validation, tag management (`add_tag`, `remove_tag`), custom string representations (`__str__`, `__repr__`), and dictionary serialization (`to_dict`).
- **`src/data_persistence.py` (Persistence Layer):** Encapsulates file I/O operations. Uses atomic writing (temporary file creation followed by `os.replace`) to safeguard storage. Protects against malformed data by backing up corrupted files.
- **`src/task_manager.py` (Business Logic Layer):** Manages the in-memory collection of tasks. Coordinates CRUD workflows, ID allocation, keyword search, multi-criteria filtering, and polymorphic sorting. Interacts with `DataPersistence` for all save/load operations.
- **`src/cli_interface.py` (Presentation Layer):** Exclusively handles terminal user interactions, menu rendering, input prompting, validation, and table formatting. Passes validated user intentions to `TaskManager`.
- **`main.py` (Application Entry Point):** Orchestrates the startup procedure, initializes dependencies, and enters the main interaction loop.

---

## 6. Week 11 to Week 12 Evolution

| Milestone / Component | Week 11 Baseline | Week 12 Final Implementation |
|---|---|---|
| **Tags Attribute** | Defined in blueprint | Fully implemented across all task subclasses with deduplication |
| **Search Engine** | Concept only | Implemented with case-insensitive partial substring matching across descriptions and tags |
| **Filtering Engine** | Single-field design | Full multi-criteria filtering combining status, date bounds, priority, and tag sets |
| **Sorting Engine** | ID sort only | 5 sorting keys, polymorphic handling for non-applicable task types, secondary ID tie-breaking |
| **Safe File I/O** | Basic `json.dump` | Atomic replacement strategy with temp files and corrupted data backup |
| **Automated Testing** | None | 39 test cases covering unit models, persistence, business logic, and CLI interactions |

---

## 7. Technical Challenges & Solutions Encountered

### 7.1 Polymorphic Sorting with Missing Attributes
- **Challenge:** When sorting a heterogeneous collection of tasks (standard `Task`, `DueDateTask`, `PriorityTask`) by `due_date` or `priority`, tasks that lack the target attribute would trigger `AttributeError` or comparison errors (e.g. comparing `None` to `datetime.date`).
- **Solution:** A composite sort key was implemented. For `due_date` sorting, `DueDateTask` instances yield `(0, t.due_date, t.id)`, while non-dated tasks yield `(1, datetime.date.max, t.id)` (or reversed values during descending sorts). Similarly, priority mapping (`High: 1, Medium: 2, Low: 3`) assigns `99` to non-prioritized tasks, keeping the collection deterministically grouped without errors.

### 7.2 Safe JSON Persistence & Atomic Replacement
- **Challenge:** Direct file writes (`open('tasks.json', 'w')`) can leave the file empty or truncated if an unexpected process termination occurs during serialization.
- **Solution:** `DataPersistence` generates a temporary file using `tempfile.mkstemp` in the same directory, flushes and syncs buffers via `os.fsync`, and then replaces the target file atomically with `os.replace`. Furthermore, corrupted JSON triggers an automated backup copy (`tasks.json.corrupted.bak`) before proceeding.

### 7.3 Multi-Criteria Filtering with AND Logic
- **Challenge:** Users may supply any combination of filter criteria (or none at all). Ensuring that only tasks satisfying *all* specified criteria are returned required careful sequential filtering and type checking.
- **Solution:** `filter_tasks` applies filters sequentially to the candidate list. Type guards (`isinstance(t, DueDateTask)`) ensure only relevant task types are evaluated for date comparisons, while tag filtering verifies that all required query tags exist in each candidate's tag set.

---

## 8. Testing & Verification Summary
- **Test Framework:** `pytest` 7.0+
- **Test Modules:**
  - `tests/test_task.py`: 12 test cases covering model initialization, field validation, tag normalization, and serialization.
  - `tests/test_data_persistence.py`: 6 test cases covering round-trip JSON serialization, atomic writes, legacy record recovery, and corrupted file safety.
  - `tests/test_task_manager.py`: 14 test cases covering CRUD operations, ID uniqueness across restarts, keyword search, complex filters, and sorting.
  - `tests/test_cli_interface.py`: 7 test cases covering menu loops, mock user input workflows, validation error handling, and graceful shutdown.
- **Total Test Cases:** 39 passed, 0 failed (100% pass rate in 0.27s).

---

## 9. Final Reflection & Lessons Learned
1. **Separation of Concerns:** Clear boundaries between CLI presentation and domain logic significantly simplified automated testing; business logic in `TaskManager` could be thoroughly tested without simulating terminal I/O.
2. **Defensive Programming:** Validating inputs at both the CLI layer (for friendly feedback) and the model layer (for data integrity) guaranteed that invalid domain entities could never be persisted.
3. **Iterative Design:** Building upon the Week 11 architectural plan allowed for a smooth, confident development cycle where each complex feature (search, filter, sort) was developed, integrated, and verified iteratively.
