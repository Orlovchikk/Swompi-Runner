from flask import Flask, request, abort
from sqlalchemy.orm import scoped_session
import subprocess
from swompi.session import engine, SessionLocal as db_session_factory
from swompi.functions import get_repo_by_url, create_build, create_repo, initialize_database
from swompi.storage import FileStorageRepository
from swompi.executor import Executor
from swompi.config import AppConfig
from swompi.functions import Base
import threading
import sys
import os
from bot import *
import asyncio

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

def run_bot_subprocess():
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(current_dir, "bot.py")
    
    try:
        process = subprocess.Popen(
            [sys.executable, bot_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        def read_output():
            while True:
                line = process.stdout.readline()
                if line:
                    print(f"[BOT] {line.strip()}")
                if process.poll() is not None:
                    break
    
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        process.wait()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    initialize_database()
    
    bot_thread = threading.Thread(target=run_bot_subprocess, daemon=True)
    bot_thread.start()
    
    app.run(host="0.0.0.0", port=25851, debug=False, use_reloader=False)