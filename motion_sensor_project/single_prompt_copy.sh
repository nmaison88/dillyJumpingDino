#!/bin/bash
# Improved script to copy the Halloween scare project to the Raspberry Pi
# with only a single password prompt

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Error handling
set -e

echo "=== Halloween Scare System Deployment ==="
echo "This script will copy files to the Raspberry Pi with a single password prompt"

# Start SSH agent if not already running
eval $(ssh-agent) > /dev/null

# Add identity to SSH agent (this will prompt for password once)
echo "Please enter your Raspberry Pi password (you'll only be asked once):"
ssh-add ~/.ssh/id_rsa 2>/dev/null || echo "No default SSH key found, will use password authentication"

# Step 1: Fix permissions on the Pi first
echo "Step 1: Fixing permissions on the Raspberry Pi..."
ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes ${PI_USER}@${PI_HOST} "
    # Create directories if they don't exist
    mkdir -p ${PI_PROJECT_DIR}/code
    mkdir -p ${PI_PROJECT_DIR}/docs
    mkdir -p ${PI_PROJECT_DIR}/audio_files
    mkdir -p ${PI_PROJECT_DIR}/idle_sounds
    
    # Take ownership of the directories
    sudo chown -R ${PI_USER}:${PI_USER} ${PI_PROJECT_DIR}
    
    # Set proper permissions
    sudo chmod -R 755 ${PI_PROJECT_DIR}
"

# Step 2: Copy Python files
echo "Step 2: Copying Python files..."
rsync -avz --exclude="__pycache__" --exclude="*.pyc" --exclude=".DS_Store" \
    -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes" \
    "${LOCAL_PROJECT_DIR}/code/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/

# Step 3: Copy audio files
echo "Step 3: Copying audio files..."
rsync -avz --exclude=".DS_Store" \
    -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes" \
    "${LOCAL_PROJECT_DIR}/audio_files/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/audio_files/

# Step 4: Copy idle sounds
echo "Step 4: Copying idle sounds..."
rsync -avz --exclude=".DS_Store" \
    -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes" \
    "${LOCAL_PROJECT_DIR}/idle_sounds/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/idle_sounds/

# Step 5: Copy documentation
echo "Step 5: Copying documentation..."
rsync -avz --exclude=".DS_Store" \
    -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes" \
    "${LOCAL_PROJECT_DIR}/docs/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/docs/ 2>/dev/null || echo "No docs directory found, skipping"
rsync -avz \
    -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes" \
    "${LOCAL_PROJECT_DIR}/README.md" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/ 2>/dev/null || echo "No README.md found, skipping"

# Step 6: Make scripts executable
echo "Step 6: Setting executable permissions..."
ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p -o ControlPersist=yes ${PI_USER}@${PI_HOST} "
    chmod +x ${PI_PROJECT_DIR}/code/*.sh 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/gui_interface.py 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/usb_relay_control.py 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/test_output.py 2>/dev/null || true
"

# Close the SSH control connection
ssh -O exit -o ControlPath=~/.ssh/control-%r@%h:%p ${PI_USER}@${PI_HOST} 2>/dev/null || true

# Kill the SSH agent
ssh-agent -k > /dev/null

echo "=== Deployment Complete! ==="
echo "Files copied to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
echo ""
echo "To run the Halloween scare system:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the program: sudo python3 code/main.py"
