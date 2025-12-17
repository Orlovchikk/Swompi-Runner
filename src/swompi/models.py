from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from typing import Optional
import enum
from datetime import datetime
from swompi.session import engine

class BuildStatus(enum.Enum):
    pending = 'pending'
    running = 'running'
    success = 'success'
    failed = 'failed'

Base = declarative_base()

class Repository(Base):
    __tablename__ = 'repositories'
    id: Mapped[int] =  mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped [DateTime] = mapped_column(DateTime, nullable=False)
    
    builds = relationship("Build", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Repository(id={self.id}, name='{self.name}')>"

class Build(Base):
    __tablename__ = 'builds'
    
    id: Mapped[int] =  mapped_column(Integer, primary_key=True, index=True)
    repository_id: Mapped[int] = mapped_column(Integer, ForeignKey('repositories.id'), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    commit_message: Mapped[Text] = mapped_column(Text, nullable=False)
    commit_author: Mapped[str] = mapped_column(String(100), nullable=False)
    ref_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    status: Mapped[BuildStatus] = mapped_column(Enum(BuildStatus), default=BuildStatus.pending)
    
    log_key: Mapped[Optional[str]] = mapped_column(String(255))
    artifacts_key: Mapped[Optional[str]] = mapped_column(String(255))
    
    created_at: Mapped [Optional[DateTime]] = mapped_column(DateTime, nullable=False)
    started_at: Mapped [Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped [Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    
    repository = relationship("Repository", back_populates="builds")

    def __repr__(self):
        return f"<Build(id={self.id}, sha='{self.commit_sha}', status='{self.status.name}')>"

