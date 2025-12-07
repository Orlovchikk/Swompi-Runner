from sqlalchemy.orm import Session
from typing import List, Optional
from lab6 import *

ses=SessionLocal()

# ?????????? ?????? ???????????
def create_repo(db: Session, url: str, name: str) -> None:
    new_repo = Repository(url=url, name=name, created_at=datetime.now().replace(microsecond=0))
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

# ???????? ???????????
def delete_repo(db: Session, url: str) -> None:
    db.query(Repository).filter(Repository.url == url).delete()
    db.commit()

# ????????? ?????? ???? ????????????
def get_all_repos(db: Session) -> List[Repository]:
    return db.query(Repository).all()

# ???????? ??????????? ? ??????? repositories
def get_repo_by_url(db: Session, url: str) -> Optional[Repository]:
    return db.query(Repository).filter(Repository.url == url).first()
    
# ?????????? ?????? ?????
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

# ?????????? ??????? ????? ?? "running"
def update_build_status_to_running(db: Session, build_id: int) -> None:
    db.query(Build).filter(Build.id == build_id).update({
        Build.status: BuildStatus.running,
        Build.started_at: datetime.now().replace(microsecond=0)
    })
    db.commit()

# ?????????? ???????? ????? ?????????? ?????
def finalize_build(
    db: Session,
    build_id: int,
    status: BuildStatus, # ????????? ?????? BuildStatus (success ??? failed)
    log_key: str,
    artifacts_key: Optional[str] = None
) -> None:
    db.query(Build).filter(Build.id == build_id).update({
        Build.status: status,
        Build.log_key: log_key,
        Build.artifacts_key: artifacts_key,
        Build.finished_at: datetime.now().replace(microsecond=0)
    })
    db.commit()