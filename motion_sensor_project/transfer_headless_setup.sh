#!/bin/bash
# Script to transfer headless setup files to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Files to transfer
FILES=(
    "code/halloween-scare.service"
    "code/setup_headless.sh"
    "code/disable_headless.sh"
)

# Transfer each file
echo "Transferring headless setup files to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}..."
for file in "${FILES[@]}"; do
    echo "Copying ${file}..."
    scp "${LOCAL_PROJECT_DIR}/${file}" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/${file}
    
    # Make shell scripts executable
    if [[ "$file" == *.sh ]]; then
        echo "Making ${file} executable..."
        ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_PROJECT_DIR}/${file}"
    fi
done

echo "Done! Files transferred to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
echo ""
echo "To set up headless mode:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the setup script: sudo ./code/setup_headless.sh"
echo ""
echo "To disable headless mode later:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the disable script: sudo ./code/disable_headless.sh"
