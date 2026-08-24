# backend/app/models/_init_.py
# CRITICAL: All models must be imported here so SQLAlchemy's mapper
# can resolve cross-model relationships like User→UserJob and Job→UserJob.
# Missing an import here = "failed to locate a name 'UserJob'" error.

from app.models.user import User          # noqa: F401
from app.models.job import Job            # noqa: F401
from app.models.user_job import UserJob   # noqa: F401