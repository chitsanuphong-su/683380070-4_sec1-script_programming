import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import task_data
import task_logic

def display_menu():
    print("\n--- Task Manager Menu ---")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Exit")
    print("-------------------------")

def main():
    tasks = task_data.load_tasks()
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        if choice == '1':
            description = input("Enter task description: ").strip()
            if description:
                tasks = task_logic.add_task(tasks, description)
            else:
                print("Task description cannot be empty.")
        elif choice == '2':
            task_logic.list_tasks(tasks)
        elif choice == '3':
            task_id_str = input("Enter ID of task to complete: ").strip()
            try:
                task_id = int(task_id_str)
                tasks = task_logic.complete_task(tasks, task_id)
            except ValueError:
                print("Invalid input. Please enter a number for Task ID.")
        elif choice == '4':
            task_id_str = input("Enter ID of task to delete: ").strip()
            try:
                task_id = int(task_id_str)
                tasks = task_logic.delete_task(tasks, task_id)
            except ValueError:
                print("Invalid input. Please enter a number for Task ID.")
        elif choice == '5':
            print("Saving tasks and exiting. Goodbye!")
            task_data.save_tasks(tasks)
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()