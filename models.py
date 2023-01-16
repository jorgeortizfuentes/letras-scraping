from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from config import DB_PATH

# Create a connection to the database
engine = create_engine(f"sqlite:///{DB_PATH}")

# Declare a Base for the models
Base = declarative_base()


class Artists(Base):
    __tablename__ = "artists"
    url = Column(String, primary_key=True)
    name = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Songs(Base):
    __tablename__ = "songs"
    url = Column(String, primary_key=True)
    main_artist = Column(String)
    title = Column(String)
    featuring_artists = Column(String)
    lyrics = Column(String)
    language = Column(String)


if __name__ == "__main__":
    # If the database does not exist, create it
    Base.metadata.create_all(engine)
