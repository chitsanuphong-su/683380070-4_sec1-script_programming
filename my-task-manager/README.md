# My Simple Task Manager CLI

A lightweight, interactive Command-Line Interface (CLI) application built with Python to manage daily tasks efficiently. All task data is automatically persisted using JSON format.

## Features

* **Add Tasks**: Add new tasks with descriptions and automatically assigned unique IDs.
* **List Tasks**: View all recorded tasks along with their ID, description, and status (Pending / Completed).
* **Complete Tasks**: Mark specific tasks as completed by entering their Task ID.
* **Delete Tasks**: Safely remove unwanted tasks by their Task ID.
* **Data Persistence**: Tasks are saved to `data/tasks.json` upon exit and loaded automatically on startup.
* **Robust Error Handling**: Handles invalid menu selections, non-numeric inputs, and missing/corrupted data files without crashing.

## Project Structure

```text
my-task-manager/
├── src/
│   ├── __init__.py      # Marks 'src' directory as a Python package
│   ├── task_data.py     # Handles reading and writing tasks to JSON
│   └── task_logic.py    # Implements core task management operations
├── data/
│   └── tasks.json       # Stores task data (created automatically)
├── main.py              # Main application entry point and user interaction loop
├── .gitignore           # Specifies untracked files for Git to ignore
└── README.md            # Project documentation