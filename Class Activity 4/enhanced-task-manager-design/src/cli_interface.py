# enhanced-task-manager-design/src/cli_interface.py
import datetime


class CLIInterface:
    """
    Handles all command-line interface interactions: displaying menus,
    taking user input, and displaying output.
    Does NOT contain business logic directly; calls methods on TaskManager.
    """

    def __init__(self, task_manager):
        self.manager = task_manager

    def display_menu(self):
        print("\n--- Enhanced Task Manager Menu ---")
        print("1. Add Normal Task")
        print("2. Add Due Date Task")
        print("3. Add Priority Task")
        print("4. List All Tasks")
        print("5. Complete Task")
        print("6. Delete Task")
        print("7. Search Tasks (Placeholder)")
        print("8. Filter Tasks (Placeholder)")
        print("9. Sort Tasks (Placeholder)")
        print("0. Exit")
        print("----------------------------------")

    def get_user_choice(self):
        return input("Enter your choice (0-9): ").strip()

    def get_task_description(self):
        while True:
            description = input("Enter task description: ").strip()
            if description:
                return description
            print("Task description cannot be empty. Please try again.")

    def get_due_date_input(self):
        while True:
            due_date_str = input("Enter due date (YYYY-MM-DD): ").strip()
            try:
                # Validate date format; TaskManager's DueDateTask will handle parsing to datetime object
                datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                return due_date_str
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD (e.g., 2024-12-31).")

    def get_priority_input(self):
        while True:
            priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
            if priority in ["High", "Medium", "Low"]:
                return priority
            print("Invalid priority. Please enter 'High', 'Medium', or 'Low'.")

    def get_tags_input(self):
        tags_str = input("Enter tags (comma-separated, e.g., work,urgent,home - optional): ").strip()
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

    def run(self):
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == '1':
                description = self.get_task_description()
                tags = self.get_tags_input()
                new_task = self.manager.add_normal_task(description, tags=tags)
                print(f"Normal Task '{new_task.description}' added with ID {new_task.id}.")
            elif choice == '2':
                description = self.get_task_description()
                due_date_str = self.get_due_date_input()
                tags = self.get_tags_input()
                new_task = self.manager.add_due_date_task(description, due_date_str, tags=tags)
                print(f"Due Date Task '{new_task.description}' (Due: {new_task.due_date.strftime('%Y-%m-%d')}) added with ID {new_task.id}.")
            elif choice == '3':
                description = self.get_task_description()
                priority = self.get_priority_input()
                tags = self.get_tags_input()
                new_task = self.manager.add_priority_task(description, priority, tags=tags)
                print(f"Priority Task '{new_task.description}' (Priority: {new_task.priority}) added with ID {new_task.id}.")
            elif choice == '4':
                tasks = self.manager.get_all_tasks()
                if not tasks:
                    print("No tasks found.")
                    continue
                print("\n--- Your Tasks ---")
                for task in tasks:
                    print(task)
                print("------------------")
            elif choice == '5':
                try:
                    task_id = int(input("Enter ID of task to complete: ").strip())
                    success, message = self.manager.complete_task(task_id)
                    print(message)
                except ValueError:
                    print("Invalid input. Please enter a number for Task ID.")
            elif choice == '6':
                try:
                    task_id = int(input("Enter ID of task to delete: ").strip())
                    success, message = self.manager.delete_task(task_id)
                    print(message)
                except ValueError:
                    print("Invalid input. Please enter a number for Task ID.")
            elif choice == '7':
                keyword = input("Enter search keyword: ").strip()
                found_tasks = self.manager.search_tasks(keyword)  # Placeholder call
                if found_tasks:
                    print("\n--- Search Results ---")
                    for task in found_tasks:
                        print(task)
                    print("----------------------")
                else:
                    print(f"No tasks found matching '{keyword}'.")
            elif choice == '8':
                print("Options for filtering: completed (true/false), due_date_before (YYYY-MM-DD), priority (High/Medium/Low), tag (single tag)")
                self.manager.filter_tasks()  # Placeholder call
                print("Filtering not fully implemented yet. See PLAN.md for details.")
            elif choice == '9':
                criterion = input("Sort by (id, due_date, priority - default: id): ").strip().lower() or "id"
                reverse_str = input("Reverse order (yes/no - default: no): ").strip().lower()
                reverse = (reverse_str == 'yes')
                sorted_tasks = self.manager.sort_tasks(criterion, reverse)  # Placeholder call
                if sorted_tasks:
                    print("\n--- Sorted Tasks ---")
                    for task in sorted_tasks:
                        print(task)
                    print("--------------------")
            elif choice == '0':
                print("Exiting Task Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 0 and 9.")
