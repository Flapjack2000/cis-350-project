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
        self._pool: list[str] = initial_tasks
        self.tasks: dict[str, bool] = {}
        self._cycle: int = 1

        self.__load_phase_tasks()

    @property
    def is_day(self) -> bool:
        return self._cycle % 2 == 1

    @property
    def day_count(self) -> int:
        return (self._cycle + 1) // 2

    def complete_task(self, task: str):
        if task in self.tasks:
            self.tasks[task] = True
            if self.is_phase_complete():
                self.__advance_cycle()

    def is_phase_complete(self) -> bool:
        tasks_required = self.DAY_TASKS_REQUIRED if self.is_day else self.NIGHT_TASKS_REQUIRED
        return sum(self.tasks.values()) >= tasks_required

    def get_available_tasks(self) -> list[str]:
        return [task for task, done in self.tasks.items() if not done]

    def __set_pool(self, tasks: list[str]):
        self._pool = tasks
        self.__load_phase_tasks()

    def __get_day_night_split(self) -> tuple[list[str], list[str]]:
        # use the day number as seed so both phases of the same day share a split
        rng = random.Random(self.day_count + self.SEED_OFFSET)
        shuffled = rng.sample(self._pool, len(self._pool))
        day_tasks = shuffled[:self.DAY_TASKS_REQUIRED]
        night_tasks = shuffled[self.DAY_TASKS_REQUIRED:self.DAY_TASKS_REQUIRED + self.NIGHT_TASKS_REQUIRED]
        return day_tasks, night_tasks

    def __load_phase_tasks(self):
        day_tasks, night_tasks = self.__get_day_night_split()
        tasks = day_tasks if self.is_day else night_tasks
        self.tasks = {task: False for task in tasks}

    def __advance_cycle(self):
        self._cycle += 1
        self.__load_phase_tasks()
