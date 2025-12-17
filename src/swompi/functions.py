from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from typing import List, Optional
from swompi.models import *

def create_repo(db: Session, url: str, name: str) -> None:
    new_repo = Repository(
        url=url, 
        name=name, 
        created_at=datetime.now().replace(microsecond=0)
    )
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

def delete_repo(db: Session, url: str) -> bool:
    repo_to_delete = db.scalars(select(Repository).where(Repository.url == url)).first()
    if not repo_to_delete:
        return False

    db.delete(repo_to_delete)
    db.commit()
    return True

def get_all_repos(db: Session) -> List[Repository]:
    stmt = select(Repository)
    result = db.execute(stmt)
    return list(result.scalars().all())

def get_repo_by_url(db: Session, url: str) -> Optional[Repository]:
    stmt = select(Repository).where(Repository.url == url)
    result = db.execute(stmt)
    return result.scalar_one_or_none()
    
def create_build(
    db: Session,
    repository_id: int,
    commit_sha: str,
    commit_message: str,
    commit_author: str,
    ref_name: str
) -> int:
    new_build = Build(
        repository_id=repository_id,
        commit_sha=commit_sha,
        commit_message=commit_message,
        commit_author=commit_author,
        ref_name=ref_name,
        status=BuildStatus.pending,
        created_at=datetime.now().replace(microsecond=0)
    )
    db.add(new_build)
    db.commit()
    db.refresh(new_build)
    return new_build.id 

def update_build_status_to_running(db: Session, build_id: int) -> None:
    stmt = update(Build).where(Build.id == build_id).values(
        status=BuildStatus.running,
        started_at=datetime.now().replace(microsecond=0)
    )
    db.execute(stmt)
    db.commit()

def finalize_build(
    db: Session,
    build_id: int,
    status: BuildStatus, 
    log_key: str,
    artifacts_key: Optional[str] = None
) -> None:
    stmt = update(Build).where(Build.id == build_id).values(
        status=status,
        log_key=log_key,
        artifacts_key=artifacts_key,
        finished_at=datetime.now().replace(microsecond=0)
    )
    db.execute(stmt)
    db.commit()    