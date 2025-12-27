# Swompi-Runner

A simple, lightweight, self-hosted CI runner designed for educational purposes and small projects. Swompi-Runner listens for Git webhooks, runs your build and test pipelines inside isolated Docker containers, and notifies you via Telegram.

## ✨ Features

* **Configuration as Code:** CI pipeline in a `.swompi.yml` file, versioned alongside code.
* **Docker-based Execution:** Every job runs in a Docker container.
* **Artifacts:** Save and retrieve build artifacts using S3-compatible storage Garage.
* **Telegram Notifications:** Real-time notifications about the status of builds in Telegram chat.
* **GitHub:** Works with GitHub.
* **CLI for Administration:** Manage the list of tracked repositories from the command line.

## 🏛️ Architecture

The system is designed as a set of microservices orchestrated by Docker Compose:

1. **Swompi-Runner:** The main application written in Python (Flask) that listens for webhooks and orchestrates the builds.
2. **Executor:** An internal component that manages the entire lifecycle of a build pipeline within Docker containers.
3. **PostgreSQL Database:** Stores metadata about repositories, builds, and their statuses.
4. **Garage (S3 Storage):** Stores build logs and artifacts.
5. **Admin CLI:** A `click`-based command-line tool for managing the system.
6. **Telegram Bot:** Provides a user-facing interface for checking build status and retrieving artifacts.

## 📋 Requirements

* Docker
* Docker Compose

## 🚀 Getting Started

Follow these steps to get Swompi-Runner instance up and running.

1. Clone the Repository.

    ```bash
    git clone git@github.com:Orlovchikk/Swompi-Runner.git
    cd swompi-runner
    ```

2. Create `.env` file with following variables.

    ```text
    POSTGRES_USER="<postgres_user>"
    POSTGRES_PASSWORD="<postgres_password>"
    TELEGRAM_BOT_TOKEN="<telegram_bot_token>"
    ```

3. Run the Services.

    ```bash
    docker-compose up -d --build
    ```

4. Add a Repository to Track.

    ```bash
    docker compose exec -it swompi-runner bash
    swompi create <github_repo_url> <comment>
    exit
    ```

5. Create `.swompi.yml` file in the root of the repository

6. Set up Github webhook:

    1. Go to your GitHub repository -> Settings -> Webhooks.
    2. Click *Add webhook*.  
    3. In the Payload URL field, enter http://<your_server_public_ip>:25851/webhook (port 25851 must be open on the machine).
    4. For Content type, select *application/json*.
    5. Under "Which events would you like to trigger this webhook?", you can select "Just the push event".
    6. Click *Add webhook*

7. Trigger a Build

    Commit and push a change to your repository. See activity in the logs `docker compose logs -f`

## Pipeline Configuration (.swompi.yml)

Example `example.swompi.yml`

```text
# 1. Define the Docker image for the build environment
image: python:3.10-slim

# 2. Define environment variables available in the build
variables:
  DATABASE_URL: "postgresql://user:password@test-db/test_db"

# 3. Define commands to run before the main scripts
before_script:
  - pip install -r requirements.txt

# 4. Define the main build
scripts:
  - flake8 .
  - pytest --cov=my_app --cov-report=html
  - echo "Build finished successfully!"

# 5. Define commands after scripts
after_script:
  - echo "Cleaning up..."

# 6. Define files or directories to save as artifacts
artifacts:
  paths:
    - htmlcov/
```

Structure Reference

* image (Required): The Docker image to use for the job.

* variables (Optional): A map of environment variables to set.

* before_script (Optional): A list of commands to run before the main scripts.

* scripts (Required): The main list of commands to execute. The pipeline will fail if any of these commands exit with a non-zero status.

* after_script (Optional): A list of commands that run after scripts.

* artifacts (Optional): Defines files and directories to be saved as artifacts upon successful completion of the job.

## Usage

### Admin CLI

The command-line interface is used to manage which repositories Swompi-Runner tracks.

```bash
# List all tacked repos
swompi ls

# Add a repo to track
swompi add <git_ssh_url> <short_name>

# Delete a repo from track
swompi delete <git_ssh_url>
```
