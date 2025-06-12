#!/bin/bash

# Note: run this script from the root directory of the project

# Create data directory if it doesn't exist
mkdir -p data

# Check if Redis is running locally
if ! command -v redis-cli &> /dev/null; then
    echo "Redis is not installed. Please install Redis first."
    exit 1
fi

redis-cli ping &> /dev/null
if [ $? -ne 0 ]; then
    echo "Redis server is not running. Please start Redis first."
    exit 1
fi

# Function to run a service in the background
run_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    PYTHONPATH=. python "$service_path" &
    echo "$service_name PID: $!"
}

# Export environment variables
export REDIS_URL="redis://localhost:6379"
export DATABASE_URL="./data/twitter.db"

# Run each service in the background
run_service "Read Service" "services/read/main.py" 8000
run_service "Write Service" "services/write/main.py" 8001
run_service "DB Updater" "services/db-updater/main.py" "N/A"

echo "All services are running!"
echo "Read Service: http://localhost:8000"
echo "Write Service: http://localhost:8001"
echo ""
echo "To stop all services, press Ctrl+C"

# Wait for Ctrl+C
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
wait 