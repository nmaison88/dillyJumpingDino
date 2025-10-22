#!/bin/bash
# Script to transfer updated main.py and required keyboard input files to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Files to transfer
FILES=(
    "code/main.py"
    "code/direct_keyboard_input.py"
    "code/pico_keyboard_input.py"
)

# Transfer each file
echo "Transferring updated files to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}..."
for file in "${FILES[@]}"; do
    echo "Copying ${file}..."
    scp "${LOCAL_PROJECT_DIR}/${file}" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/${file}
    
    # Make Python files executable
    if [[ "$file" == *.py ]]; then
        echo "Making ${file} executable..."
        ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_PROJECT_DIR}/${file}"
    fi
done

echo "Done! Files transferred to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
echo ""
echo "The main.py file has been updated to support all keyboard input methods, including your Pico Pi."
echo "Your existing service that runs on boot should now work with the Pico keyboard."
echo ""
echo "To test the updated system:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the program: sudo python3 code/main.py"
echo ""
echo "Note: 'sudo' is required to access the keyboard devices directly."
