#backend/app/collectors/base.py

from abc import ABC, abstractmethod


class JobCollector(ABC):
    def __init__(self, source: str | None = None):
        self.source = source or self.__class__.__name__

    @abstractmethod
    def fetch_jobs(self, filter):
        pass