from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from record_catalog.database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    artist = Column(String, nullable=False, index=True)
    album = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=True)
    genre = Column(String, nullable=True, index=True)
    label = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    tracks = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (UniqueConstraint("artist", "album", name="uq_artist_album"),)

    def __repr__(self) -> str:
        return f"<Record(artist={self.artist!r}, album={self.album!r})>"
