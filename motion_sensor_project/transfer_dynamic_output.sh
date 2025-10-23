#!/bin/bash
# Script to transfer the updated main.py with dynamic output toggling to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Transfer the file
echo "Transferring updated main.py with dynamic output toggling to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/..."
scp "${LOCAL_PROJECT_DIR}/code/main.py" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/

# Make it executable
echo "Making main.py executable..."
ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_PROJECT_DIR}/code/main.py"

echo "Done! Updated main.py transferred to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/"
echo ""
echo "The pneumatic cylinder will now toggle dynamically during audio playback:"
echo "1. It will always start ON when the audio begins"
echo "2. It will toggle randomly during playback (minimum 500ms between toggles)"
echo "3. It will always end OFF when the audio finishes"
echo ""
echo "You can adjust the toggling behavior by modifying these variables in main.py:"
echo "- MIN_TOGGLE_DURATION: Minimum time between toggles (currently 0.5 seconds)"
echo "- MAX_TOGGLE_DURATION: Maximum time between toggles (currently 2.0 seconds)"
echo "- TOGGLE_PROBABILITY: Chance of toggling at each interval (currently 0.7 or 70%)"
echo ""
echo "Run the program with: sudo python3 ~/motion_sensor_project/code/main.py"
