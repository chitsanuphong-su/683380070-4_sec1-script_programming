import requests
import json

class APIClient:
    """A client to interact with the JSONPlaceholder API."""
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def _make_request(self, endpoint):
        url = f"{self.BASE_URL}{endpoint}"
        print(f"Fetching data from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"An unexpected error occurred: {err}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from response: {response.text[:100]}...")
        return None

    def fetch_single_todo(self, todo_id):
        """Fetches a single TODO item by its ID."""
        return self._make_request(f"/todos/{todo_id}")

    def fetch_all_posts(self):
        """Fetches a list of all posts."""
        return self._make_request("/posts")

    def fetch_user_todos(self, user_id):
        """Fetches all TODOs for a specific user ID."""
        return self._make_request(f"/todos?userId={user_id}")