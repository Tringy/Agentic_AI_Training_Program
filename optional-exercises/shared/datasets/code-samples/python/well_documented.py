"""
Example of well-documented Python code following best practices.

This module demonstrates proper documentation structure including:
- Module-level docstrings
- Function docstrings with parameters and return types
- Type hints
- Clear variable names
- Inline comments for complex logic
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    """
    Represents a task in a task management system.

    Attributes:
        id: Unique identifier for the task
        title: Brief description of the task
        description: Detailed task information
        status: Current task status (pending, in_progress, completed)
        priority: Task priority level (1-5, where 5 is highest)
        created_at: Timestamp when task was created
        completed_at: Timestamp when task was completed (None if not completed)
    """
    id: int
    title: str
    description: str
    status: str = "pending"
    priority: int = 3
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize created_at timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()


class TaskManager:
    """
    Manages a collection of tasks with operations for CRUD and filtering.

    This class provides a simple interface for managing tasks in memory.
    For production use, consider adding database persistence.

    Example:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Review PR", "Review pull request #123")
        >>> manager.complete_task(task.id)
        >>> high_priority = manager.get_tasks_by_priority(min_priority=4)
    """

    def __init__(self):
        """Initialize an empty task manager."""
        self.tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(
        self,
        title: str,
        description: str,
        priority: int = 3
    ) -> Task:
        """
        Add a new task to the manager.

        Args:
            title: Brief task description (required)
            description: Detailed task information (required)
            priority: Priority level from 1-5, default is 3

        Returns:
            The newly created Task object

        Raises:
            ValueError: If priority is not between 1 and 5

        Example:
            >>> task = manager.add_task("Fix bug", "Fix login issue", priority=5)
        """
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority
        )
        self.tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task object if found, None otherwise
        """
        return self.tasks.get(task_id)

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete

        Returns:
            True if task was found and completed, False otherwise
        """
        task = self.tasks.get(task_id)
        if task:
            task.status = "completed"
            task.completed_at = datetime.now()
            return True
        return False

    def get_tasks_by_priority(
        self,
        min_priority: int = 1,
        max_priority: int = 5
    ) -> List[Task]:
        """
        Get all tasks within a priority range.

        Args:
            min_priority: Minimum priority level (inclusive), default 1
            max_priority: Maximum priority level (inclusive), default 5

        Returns:
            List of tasks matching the priority criteria, sorted by priority
            (highest first)

        Example:
            >>> high_priority_tasks = manager.get_tasks_by_priority(min_priority=4)
        """
        filtered_tasks = [
            task for task in self.tasks.values()
            if min_priority <= task.priority <= max_priority
        ]
        # Sort by priority (descending) and then by created_at (ascending)
        return sorted(
            filtered_tasks,
            key=lambda t: (-t.priority, t.created_at)
        )

    def get_statistics(self) -> Dict[str, int]:
        """
        Calculate statistics about current tasks.

        Returns:
            Dictionary containing:
                - total: Total number of tasks
                - completed: Number of completed tasks
                - pending: Number of pending tasks
                - in_progress: Number of in-progress tasks

        Example:
            >>> stats = manager.get_statistics()
            >>> print(f"Completion rate: {stats['completed'] / stats['total']:.1%}")
        """
        stats = {
            "total": len(self.tasks),
            "completed": 0,
            "pending": 0,
            "in_progress": 0
        }

        for task in self.tasks.values():
            stats[task.status] = stats.get(task.status, 0) + 1

        return stats
