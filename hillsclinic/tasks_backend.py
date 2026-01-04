"""
Custom django_tasks backend to work around Python 3.12 typing bug.
"""
from django_tasks.backends.base import BaseTaskBackend


class SafeDummyBackend(BaseTaskBackend):
    """
    A dummy backend that simply does nothing, avoiding the Python 3.12 typing bug.
    """
    supports_defer = False
    supports_async_task = False

    def enqueue(self, task, args, kwargs):
        # Simply do nothing - skip the task entirely
        # This avoids the TaskResult[T] typing bug
        return None
    
    async def aenqueue(self, task, args, kwargs):
        return None
