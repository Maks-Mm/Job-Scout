#backend/app/collectors/base.py

from abc import ABC, abstractmethod


class JobCollector(ABC):

    @abstractmethod
    def fetch_jobs(self, city: str):
        pass