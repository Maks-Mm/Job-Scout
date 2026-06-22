from sqlalchemy import Column, Integer, String, DateTime
from app.api.core.database import Base
from datetime import datetime


class Job(Base):

	__tablename__ = "jobs"


	id = Column(
		Integer,
		primary_key=True
	)


	title = Column(
		String
	)


	company = Column(
		String
	)


	city = Column(
		String
	)


	salary = Column(
		String
	)


	url = Column(
		String,
		unique=True
	)


	source = Column(
		String
	)


	created_at = Column(
		DateTime,
		default=datetime.utcnow
	)