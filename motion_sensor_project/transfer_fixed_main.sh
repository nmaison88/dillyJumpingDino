#!/bin/bash
# Script to transfer just the fixed main.py file to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Transfer the file
echo "Transferring fixed main.py to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/..."
scp "${LOCAL_PROJECT_DIR}/code/main.py" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/

# Make it executable
echo "Making main.py executable..."
ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_PROJECT_DIR}/code/main.py"

echo "Done! Fixed main.py transferred to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/"
echo ""
echo "The syntax error has been fixed. You can now run the program with:"
echo "  sudo python3 ~/motion_sensor_project/code/main.py"
