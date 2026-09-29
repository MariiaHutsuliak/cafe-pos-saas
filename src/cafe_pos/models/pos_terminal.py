import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey

from cafe_pos.database import Base


class TerminalStatus(str, enum.Enum):
    online = "online"
    offline = "offline"


class PosTerminal(Base):
    __tablename__ = "pos_terminals"

    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"), nullable=False)
    device_id = Column(String, nullable=False, unique=True)
    status = Column(Enum(TerminalStatus), nullable=False, default=TerminalStatus.online)
