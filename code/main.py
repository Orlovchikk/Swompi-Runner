from flask import Flask, request, abort
from sqlalchemy.orm import scoped_session

from session import SessionLocal as db_session_factory
from functions import get_repo_by_url, create_build
# from .s3 import create_s3_client
from executor import Executor
from config import AppConfig

app = Flask(__name__)

config = AppConfig()
# s3_client = create_s3_client(config)
s3_client = None
executor = Executor(db_session_factory, s3_client, config)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        repo_url = request_json['repository']['clone_url']
        commit_sha = request_json['after']
        commit_message = request_json['head_commit']['message']
        commit_author = request_json['head_commit']['author']['username']
        ref_name = executor._parse_ref(request_json['ref'])
        repository_id = get_repo_by_url(repo_url)

        with db_session_factory() as db_session:
            new_build = create_build(db, repository_id, commit_sha, commit_message, commit_author, ref_name)

        print(f"Build {new_build['id']} has been queued")
        
        executor.run_build(build_id=new_build["id"], request_json=request.json)

        return "success", 200
    else:
        abort(400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25851)
