#!/bin/bash
# Script to clean up __pycache__ directories before transferring to Raspberry Pi

# Configuration
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

echo "Cleaning up __pycache__ directories..."

# Find and remove all __pycache__ directories
find "${LOCAL_PROJECT_DIR}" -type d -name "__pycache__" -exec rm -rf {} +

# Find and remove all .pyc files
find "${LOCAL_PROJECT_DIR}" -type f -name "*.pyc" -delete

echo "Done! All __pycache__ directories and .pyc files have been removed."
