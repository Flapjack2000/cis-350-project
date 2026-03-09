from global_settings import Settings

settings = Settings()

class Minigame:
    def __init__(self, is_day: bool):
        if not isinstance(is_day, bool):
            raise ValueError
        else:
            self._is_day = is_day

        self._is_complete = False

    @property
    def is_day(self) -> bool:
        return self._is_day

    @is_day.setter
    def is_day(self, is_day: bool):
        if not isinstance(is_day, bool):
            raise ValueError
        else:
            self._is_day = is_day

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    @is_complete.setter
    def is_complete(self, complete: bool):
        if not isinstance(complete, bool):
            raise ValueError
        else:
            self._is_complete = complete
