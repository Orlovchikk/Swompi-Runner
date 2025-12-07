from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime

class BuildStatus(enum.Enum):
    pending = 'pending'
    running = 'running'
    success = 'success'
    failed = 'failed'

Base = declarative_base()

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/Swompi2"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Repository(Base):
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    builds = relationship("Build", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Repository(id={self.id}, name='{self.name}')>"

class Build(Base):
    __tablename__ = 'builds'
    
    id = Column(Integer, primary_key=True, index=True)
    
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    commit_sha = Column(String(40), nullable=False)
    commit_message = Column(Text, nullable=False)
    commit_author = Column(String(100), nullable=False)
    ref_name = Column(String(100), nullable=False)
    
    status = Column(Enum(BuildStatus), default=BuildStatus.pending)
    
    log_key = Column(String(255))
    artifacts_key = Column(String(255))
    
    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    repository = relationship("Repository", back_populates="builds")

    def __repr__(self):
        return f"<Build(id={self.id}, sha='{self.commit_sha}', status='{self.status.name}')>"


Base.metadata.create_all(engine)
