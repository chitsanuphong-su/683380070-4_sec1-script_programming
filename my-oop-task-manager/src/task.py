class Task:
    """Represents a single task in the task manager."""
    def __init__(self, id, description, completed=False):
        self.id = id
        self.description = description
        self.completed = completed

    def mark_complete(self):
        self.completed = True

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed
        }

    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        return f"ID: {self.id} | Description: {self.description} | Status: {status}"

    def __repr__(self):
        return f"Task(id={self.id}, description='{self.description}', completed={self.completed})"