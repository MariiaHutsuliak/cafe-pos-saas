from sqlalchemy import Column, Integer, String

from cafe_pos.database import Base


class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="Europe/Kyiv")
