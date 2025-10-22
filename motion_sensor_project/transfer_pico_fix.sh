#!/bin/bash
# Script to transfer Pico keyboard fix files to the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Files to transfer
FILES=(
    "code/pico_keyboard_input.py"
    "code/test_pico_keyboard.py"
    "code/main_all_keyboards.py"
)

# Transfer each file
echo "Transferring Pico keyboard fix files to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}..."
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
echo "To test the Pico keyboard input:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the test script: sudo python3 code/test_pico_keyboard.py"
echo ""
echo "To run the main program with all keyboard support:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the program: sudo python3 code/main_all_keyboards.py"
echo ""
echo "Note: 'sudo' is required to access the keyboard devices directly."
