#backend/app/collectors/austria/_init__.py

from .ams import AMSCollector
from .karriere_at import KarriereATCollector
from .willhaben import WillhabenCollector

__all__ = [
    "AMSCollector",
    "KarriereATCollector",
    "WillhabenCollector",
]