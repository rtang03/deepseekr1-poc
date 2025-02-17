#!/bin/sh

sleep 3

# Function to start ollama service with retries
start_ollama_service() {
  local retries=3
  local count=0

  while [ $count -lt $retries ]; do
    systemctl start ollama
    if [ $? -eq 0 ]; then
      return 0
    fi
    count=$((count + 1))
    echo "Retrying to start ollama service ($count/$retries)..."
    sleep 3
  done

  return 1
}

# Start ollama service with retries
start_ollama_service
if [ $? -ne 0 ]; then
  echo "Failed to start ollama service after 3 attempts. Stopping the container."
  systemctl status ollama
  exit 1
fi

# Show the status of ollama service
systemctl status ollama

# Start the uvicorn server
exec uvicorn --port=$PORT main:app --reload --log-config=log_conf.yaml