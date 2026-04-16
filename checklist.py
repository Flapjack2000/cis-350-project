import random


class Checklist:
    """
        Manages a day/night task checklist that cycles deterministically.

        Tasks are drawn from a pool and split between day and night phases with no
        overlap. Day gets DAY_TASKS_REQUIRED tasks, night gets NIGHT_TASKS_REQUIRED.

        Both phases of the same day share a seeded shuffle (seeded by day number +
        SEED_OFFSET), so the split is always the same for a given day but differs
        across days. Adjusting SEED_OFFSET produces a completely different but still
        deterministic game.

        A phase completes when enough tasks are marked done, automatically advancing
        to the next phase and loading a fresh task set.
    """

    DAY_TASKS_REQUIRED = 4
    NIGHT_TASKS_REQUIRED = 3
    SEED_OFFSET = 1

    def __init__(self, initial_tasks: list[str]):
        """Load the tasks and create the checklist dictionary.

        Args:
            initial_tasks (list[str]): The pool of task names to draw from each day/night cycle.

        Raises:
            ValueError: If fewer tasks are provided than DAY_TASKS_REQUIRED + NIGHT_TASKS_REQUIRED.
        """

        tasks_length = len(initial_tasks)
        req_tasks_length = self.DAY_TASKS_REQUIRED + self.NIGHT_TASKS_REQUIRED
        if tasks_length < req_tasks_length:
            raise ValueError(
                f"Checklist initialized with {tasks_length} tasks. Requires at least {req_tasks_length} tasks.")

        self.__pool: list[str] = initial_tasks
        self.__tasks: dict[str, bool] = {}
        self.__cycle: int = 1

        self.__load_phase_tasks()

    @property
    def is_day(self) -> bool:
        """Return whether it is daytime."""
        return self.__cycle % 2 == 1

    @property
    def day_count(self) -> int:
        """Return the number of days that have elapsed (including the current day)."""
        return (self.__cycle + 1) // 2

    def complete_task(self, task: str):
        """Mark a task as complete.

        Args:
            task (str): The name of the task to be marked complete.
        """
        if task in self.__tasks:
            self.__tasks[task] = True
            if self.is_phase_complete():
                self.__advance_cycle()

    def is_phase_complete(self) -> bool:
        """Return whether the player has completed the tasks for the part of the day it is."""
        tasks_required = self.DAY_TASKS_REQUIRED if self.is_day else self.NIGHT_TASKS_REQUIRED
        return sum(self.__tasks.values()) >= tasks_required

    def get_incomplete_tasks(self) -> list[str]:
        """Return the tasks on the checklist that have not been done yet."""
        return [task for task, done in self.__tasks.items() if not done]

    def get_completed_tasks(self) -> list[str]:
        """Return the tasks on the checklist that have been done."""
        return [task for task, done in self.__tasks.items() if done]

    def get_all_tasks(self) -> list[str]:
        """Return all the tasks on the checklist."""
        return [task for task in self.__tasks.keys()]

    def __set_pool(self, tasks: list[str]):
        """Stores the pool of tasks.

        Args:
            tasks (list[str]): The names of the tasks.
        """
        self.__pool = tasks
        self.__load_phase_tasks()

    def __get_day_night_split(self) -> tuple[list[str], list[str]]:
        """Partition tasks between day and night.

        Returns:
            tuple[list[str], list[str]]: A tuple of (day_tasks, night_tasks), each a
                deterministically shuffled subset of the pool for the current day.
        """
        rng = random.Random(self.day_count + self.SEED_OFFSET)
        shuffled = rng.sample(self.__pool, len(self.__pool))
        day_tasks = shuffled[:self.DAY_TASKS_REQUIRED]
        night_tasks = shuffled[self.DAY_TASKS_REQUIRED:self.DAY_TASKS_REQUIRED + self.NIGHT_TASKS_REQUIRED]
        return day_tasks, night_tasks

    def __load_phase_tasks(self):
        """Load the tasks for the time of day."""
        day_tasks, night_tasks = self.__get_day_night_split()
        tasks = day_tasks if self.is_day else night_tasks
        self.__tasks = {task: False for task in tasks}

    def __advance_cycle(self):
        """Move to the next cycle and load tasks."""
        self.__cycle += 1
        self.__load_phase_tasks()
