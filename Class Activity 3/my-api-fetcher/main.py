import sys
import os

# Ensure src directory is accessible in Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api_client import APIClient

def display_menu():
    print("\n--- API Data Fetcher Menu ---")
    print("1. Fetch a Single TODO Item")
    print("2. Fetch All Posts")
    print("3. Fetch TODOs by User ID")
    print("4. Exit")
    print("----------------------------")

def main():
    client = APIClient()

    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            try:
                todo_id = int(input("Enter TODO ID (e.g., 1, 5, 10): ").strip())
                if todo_id <= 0:
                    print("TODO ID must be a positive number.")
                    continue
                todo_item = client.fetch_single_todo(todo_id)
                if todo_item:
                    print("\n--- TODO Item Details ---")
                    print(f"ID: {todo_item.get('id')}")
                    print(f"User ID: {todo_item.get('userId')}")
                    print(f"Title: {todo_item.get('title')}")
                    print(f"Completed: {todo_item.get('completed')}")
                    print("------------------------")
            except ValueError:
                print("Invalid input. Please enter a valid number for TODO ID.")
        elif choice == '2':
            posts = client.fetch_all_posts()
            if posts:
                print("\n--- First 5 Posts ---")
                for i, post in enumerate(posts[:5]):
                    print(f"Post ID: {post.get('id')}")
                    print(f"Title: {post.get('title')}")
                    print(f"Body: {post.get('body')[:50]}...")
                    print("---")
                if len(posts) > 5:
                    print(f"... and {len(posts) - 5} more posts.")
                print("---------------------")
        elif choice == '3':
            try:
                user_id = int(input("Enter User ID (e.g., 1, 2, 3): ").strip())
                if user_id <= 0:
                    print("User ID must be a positive number.")
                    continue
                user_todos = client.fetch_user_todos(user_id)
                if user_todos:
                    print(f"\n--- TODOs for User ID {user_id} ---")
                    for todo in user_todos:
                        status = "Completed" if todo.get('completed') else "Pending"
                        print(f"ID: {todo.get('id')} | Title: {todo.get('title')} | Status: {status}")
                    print("-----------------------------")
            except ValueError:
                print("Invalid input. Please enter a valid number for User ID.")
        elif choice == '4':
            print("Exiting API Data Fetcher. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()