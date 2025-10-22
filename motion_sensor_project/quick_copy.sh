#!/bin/bash
# Script to quickly copy specific files to the Raspberry Pi without transferring the entire project

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Error handling
set -e

# Check if files are provided as arguments
if [ $# -eq 0 ]; then
  echo "Usage: $0 file1 [file2 ...]"
  echo "Example: $0 code/main.py code/motion_sensor.py"
  exit 1
fi

# Process each file
for file in "$@"; do
  # Get the directory part of the file path
  dir_path=$(dirname "$file")
  
  # Create the directory on the Pi if it doesn't exist
  echo "Creating directory $dir_path on Pi..."
  ssh ${PI_USER}@${PI_HOST} "mkdir -p ${PI_PROJECT_DIR}/$dir_path"
  
  # Copy the file
  echo "Copying $file..."
  scp "${LOCAL_PROJECT_DIR}/$file" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/$file
  
  # Make Python files executable if they're in the code directory
  if [[ "$file" == code/*.py ]]; then
    echo "Making $file executable..."
    ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_PROJECT_DIR}/$file"
  fi
done

echo "Done! Files copied to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
