import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123@localhost:5432/steamgames"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

game_tags_table = Table(
    "game_tags", Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",  Integer, ForeignKey("tags.id",  ondelete="CASCADE"), primary_key=True),
)

class Game(Base):
    __tablename__ = "games"
    id                = Column(Integer, primary_key=True)
    title             = Column(String(255), nullable=False)
    thumbnail         = Column(Text)
    short_description = Column(Text)
    game_url          = Column(Text)
    genre             = Column(String(150))
    platform          = Column(String(100))
    publisher         = Column(String(150))
    developer         = Column(String(150))
    release_date      = Column(Date)
    price             = Column(String(50))
    created_at        = Column(DateTime, server_default=func.now())

    tags = relationship("Tag", secondary=game_tags_table, back_populates="games")

class Tag(Base):
    __tablename__ = "tags"
    id   = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    games = relationship("Game", secondary=game_tags_table, back_populates="tags")