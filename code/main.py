from flask import Flask, request, abort

# from .database import create_db_session_factory
# from .s3 import create_s3_client
from executor import Executor
from config import AppConfig

app = Flask(__name__)
config = AppConfig()
# db_session_factory = create_db_session_factory(config.DATABASE_URL)
# s3_client = create_s3_client(config)
db_session_factory = None
s3_client = None
executor = Executor(db_session_factory, s3_client, config)


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        repo_url = request.json['repository']['clone_url']
        commit_sha = request.json['after']

        # db: Session = next(db_session_factory())

        # new_build = create_build_record(db, repo_url=repo_url, commit_sha=commit_sha)
        # db.close()
        new_build = {"id": 1}
        print(f"Build {new_build['id']} has been queued")
        
        executor.run_build(build_id=new_build["id"], repo_url=repo_url, commit_sha=commit_sha)

        return "success", 200
    else:
        abort(400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25851)
