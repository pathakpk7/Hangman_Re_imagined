import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Portable PostgreSQL / SQLite database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hangman_game.db")

# Normalize dialect prefix for Neon / PostgreSQL URLs (SQLAlchemy requires postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite vs Cloud PostgreSQL connection settings
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Engine configuration with pre-ping to handle serverless pool timeouts (e.g. Neon)
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
