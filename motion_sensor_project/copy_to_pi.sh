#!/bin/bash
# Script to copy the Halloween scare project to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Create directories on the Pi
echo "Creating directories on the Raspberry Pi..."
ssh ${PI_USER}@${PI_HOST} "mkdir -p ${PI_PROJECT_DIR}/code ${PI_PROJECT_DIR}/docs ${PI_PROJECT_DIR}/audio_files"

# Copy code files
echo "Copying code files..."
scp /Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project/code/*.py ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/

# Copy documentation
echo "Copying documentation..."
scp /Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project/docs/circuit_diagram.md ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/docs/
scp /Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project/README.md ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/

# Copy audio files (if they exist)
echo "Copying audio files..."
scp -r "${LOCAL_PROJECT_DIR}/audio_files" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/

echo "Done! Files copied to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
echo ""
echo "To run the Halloween scare system:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the program: sudo python3 code/main.py"
echo ""
echo "Audio files location:"
echo "  - Local: ${LOCAL_PROJECT_DIR}/audio_files"
echo "  - On Raspberry Pi: ${PI_PROJECT_DIR}/audio_files"
echo ""
echo "To add more audio files:"
echo "  1. Add files to ${LOCAL_PROJECT_DIR}/audio_files"
echo "  2. Run this script again to copy them to the Raspberry Pi"
