from flask import Flask, request, abort
from sqlalchemy.orm import scoped_session

from swompi.session import engine, SessionLocal as db_session_factory
from swompi.functions import get_repo_by_url, create_build, create_repo
from swompi.storage import FileStorageRepository
from swompi.executor import Executor
from swompi.config import AppConfig
from swompi.functions import Base

app = Flask(__name__)

config = AppConfig()
file_storage_repo = FileStorageRepository(config)
executor = Executor(db_session_factory, file_storage_repo, config)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        repo_url = request.json['repository']['clone_url']
        commit_sha = request.json['after']
        commit_message = request.json['head_commit']['message']
        commit_author = request.json['head_commit']['author']['username']
        ref_name = executor._parse_ref(request.json['ref'])

        with db_session_factory() as db_session:
            repository = get_repo_by_url(db_session, repo_url)
            if repository:
                new_build = create_build(db_session, repository.id, commit_sha, commit_message, commit_author, ref_name)
                print(f"Build {new_build} has been queued")
                
                executor.run_build(build_id=new_build, request_json=request.json)

                return "success", 200
            else:
                print(f"Repository {repo_url} not found. Cannot start build")
                abort(403)
    else:
        abort(400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25851)