#!/bin/bash
set -e

ENV_FILE="/app/swompi/shared_data/.garage.env"
PROFILE_FILE="/etc/bash.bashrc" 
LOAD_COMMAND="source ${ENV_FILE}"

echo "Container entrypoint started. Waiting for 30 seconds before launching the application..."
sleep 30

echo "Wait finished. Starting application..."

if ! grep -qF "$LOAD_COMMAND" "$PROFILE_FILE"; then
  echo "Adding environment loader to ${PROFILE_FILE}"
  echo -e "\n# Load Swompi environment variables from shared volume\nif [ -f \"$ENV_FILE\" ]; then\n  set -a\n  . \"$ENV_FILE\"\n  set +a\nfi" >> "$PROFILE_FILE"
  echo "Loader added."
else
  echo "Environment loader already present in ${PROFILE_FILE}."
fi

set -a
. "/app/swompi/shared_data/.garage.env"
set +a
echo "Variables loaded."

exec python /app/swompi/main.py