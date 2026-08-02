#backend/app/collectors/belgien/_init_py


# backend/app/collectors/belgien/__init__.py

from .eURES import EURESCollector
from .indeedBelgien import IndeedBelgiumCollector
from .stepStoneBelgien import StepStoneBelgiumCollector

__all__ = [
    "EURESCollector",
    "IndeedBelgiumCollector",
    "StepStoneBelgiumCollector",
]