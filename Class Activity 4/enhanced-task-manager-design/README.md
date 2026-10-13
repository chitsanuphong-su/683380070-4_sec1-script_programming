# Enhanced Task Manager Design (Week 11 Scaffold)

This project serves as a conceptual and architectural scaffold for an Enhanced Task Manager CLI application.
It demonstrates **Project Planning & Design** principles, breaking down a larger application into modular components before full implementation.

This version is designed to evolve from the previous Task Manager, integrating advanced features like **tags**, **search**, **filtering**, and **sorting**.

## Key Concepts Demonstrated (Design Focus)

* **Project Planning:** The importance of defining requirements and designing architecture upfront.
* **Modular Design:** Breaking the application into logical, independent components:
  * `src/task.py`: Defines task data structures (models).
  * `src/data_persistence.py`: Handles all file I/O (loading/saving).
  * `src/task_manager.py`: Contains core business logic (managing tasks).
  * `src/cli_interface.py`: Manages all user interaction (input/output).
  * `main.py`: Orchestrates the application flow.
* **Separation of Concerns:** Each module has a single, clear responsibility.
* **Extensibility:** The design aims to make it easy to add new features or change underlying technologies (e.g., switch from JSON to a database).
* **Requirements Definition:** Outlined in `PLAN.md`.

## Features (Planned for Future Implementation)

* **Basic CRUD**: Add, list, complete, delete tasks (already functional with improved architecture).
* **Task Types**: Normal, Due Date, Priority tasks.
* **Tags**: Assign multiple customizable tags to tasks.
* **Search**: Find tasks by keywords in description or tags (Placeholder).
* **Filter**: Filter tasks by completion status, due date range, priority, or specific tags (Placeholder).
* **Sort**: Organize tasks by ID, due date, priority, or other criteria (Placeholder).
* **Persistence**: Tasks are saved to and loaded from `data/tasks.json`.

## How to Run (Skeleton)

1. **Navigate to the project root:**
   ```bash
   cd "Class Activity 4/enhanced-task-manager-design"
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```
   *(Note: Most advanced features (search, filter, sort) are placeholders in this scaffold and will print "DEBUG" messages.)*

## Project Structure

```text
enhanced-task-manager-design/
├── src/
│   ├── __init__.py        # Makes 'src' a Python package
│   ├── task.py            # Task models (includes tags field)
│   ├── data_persistence.py # Handles JSON file operations
│   ├── task_manager.py    # Core task logic (placeholder for new features)
│   └── cli_interface.py   # Handles user interaction (menu, input/output)
├── data/
│   └── tasks.json         # Stores tasks in JSON format
├── main.py                # Application entry point
├── .gitignore             # Files/folders to ignore in Git
├── README.md              # Project overview and link to PLAN.md
└── PLAN.md                # THE KEY DOCUMENT: Detailed project plan and design
```

## Future Implementation / Extension Ideas

This scaffold is designed to be built upon in future weeks. Here are some ideas:

* **Implement Search/Filter/Sort:** Fill out the placeholder methods in `task_manager.py` and integrate them fully into `cli_interface.py`.
* **Advanced Tag Management:** Add options to list all unique tags, or delete tasks by tag.
* **Priority Levels:** Implement numeric priority levels (e.g., 1-5) and allow sorting by it.
* **Reminders:** (Conceptual for CLI) - could implement a simple check for upcoming tasks on startup.
* **GUI Interface:** Explore libraries like `Tkinter`, `PyQt`, or `Kivy` to build a graphical user interface.
* **Database Integration:** Replace `data_persistence.py` with logic to use a lightweight database like SQLite.
* **Unit Testing:** Write automated tests for `task.py` and `task_manager.py` logic.

## Contributing

This project is a scaffold. Feel free to fork it and start implementing the planned features!

## License

This project is open source under the MIT License.
