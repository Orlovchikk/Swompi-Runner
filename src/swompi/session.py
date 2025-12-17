from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from swompi.config import AppConfig

config = AppConfig()

engine = create_engine(f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@database/{config.POSTGRES_DB}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)