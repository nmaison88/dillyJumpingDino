#!/bin/bash
# Script to copy the Halloween scare project to the Raspberry Pi using sshpass
# This requires sshpass to be installed: brew install esolitos/ipa/sshpass

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"
LOCAL_PROJECT_DIR="/Users/nethmaison/dev/dillyJumpingDino/motion_sensor_project"

# Error handling
set -e

echo "=== Halloween Scare System Deployment using sshpass ==="
echo "This script will copy files to the Raspberry Pi with a single password prompt"

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "sshpass is not installed. Please install it first:"
    echo "  brew install esolitos/ipa/sshpass"
    exit 1
fi

# Ask for password once
read -sp "Enter your Raspberry Pi password: " PI_PASSWORD
echo ""

# Step 1: Fix permissions on the Pi first
echo "Step 1: Fixing permissions on the Raspberry Pi..."
sshpass -p "$PI_PASSWORD" ssh ${PI_USER}@${PI_HOST} "
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
sshpass -p "$PI_PASSWORD" rsync -avz --exclude="__pycache__" --exclude="*.pyc" --exclude=".DS_Store" \
    "${LOCAL_PROJECT_DIR}/code/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/code/

# Step 3: Copy audio files
echo "Step 3: Copying audio files..."
sshpass -p "$PI_PASSWORD" rsync -avz --exclude=".DS_Store" \
    "${LOCAL_PROJECT_DIR}/audio_files/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/audio_files/

# Step 4: Copy idle sounds
echo "Step 4: Copying idle sounds..."
sshpass -p "$PI_PASSWORD" rsync -avz --exclude=".DS_Store" \
    "${LOCAL_PROJECT_DIR}/idle_sounds/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/idle_sounds/

# Step 5: Copy documentation
echo "Step 5: Copying documentation..."
sshpass -p "$PI_PASSWORD" rsync -avz --exclude=".DS_Store" \
    "${LOCAL_PROJECT_DIR}/docs/" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/docs/ 2>/dev/null || echo "No docs directory found, skipping"
sshpass -p "$PI_PASSWORD" rsync -avz \
    "${LOCAL_PROJECT_DIR}/README.md" ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}/ 2>/dev/null || echo "No README.md found, skipping"

# Step 6: Make scripts executable
echo "Step 6: Setting executable permissions..."
sshpass -p "$PI_PASSWORD" ssh ${PI_USER}@${PI_HOST} "
    chmod +x ${PI_PROJECT_DIR}/code/*.sh 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/gui_interface.py 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/usb_relay_control.py 2>/dev/null || true
    chmod +x ${PI_PROJECT_DIR}/code/test_output.py 2>/dev/null || true
"

echo "=== Deployment Complete! ==="
echo "Files copied to ${PI_USER}@${PI_HOST}:${PI_PROJECT_DIR}"
echo ""
echo "To run the Halloween scare system:"
echo "  1. SSH into your Raspberry Pi: ssh ${PI_USER}@${PI_HOST}"
echo "  2. Navigate to the project directory: cd ${PI_PROJECT_DIR}"
echo "  3. Run the program: sudo python3 code/main.py"
