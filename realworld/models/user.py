import datetime as dt
import uuid

from sqlalchemy import Column, DateTime, String, Uuid

from realworld.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, index=True, default=uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Assume bio is empty by default since the RealWorld spec doesn't mention it.
    bio = Column(String, nullable=False, default="")
    image = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=dt.datetime.utcnow)
