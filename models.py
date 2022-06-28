import uuid
from sqlalchemy import Column, String, DateTime, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)
    date = Column(DateTime(timezone=True), nullable=False)
    parentId = Column(UUID(as_uuid=True), index=True)
    price = Column(Integer)
    children = Column(ARRAY(String), nullable=True)

class ItemStatistic(Base):
    __tablename__ = "item_history"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)
    date = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    parentId = Column(UUID(as_uuid=True), index=True)
    price = Column(Integer)