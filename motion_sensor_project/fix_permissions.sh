#!/bin/bash
# Script to fix permissions on the Raspberry Pi

# Configuration
PI_USER="admin"
PI_HOST="yumpi"
PI_PROJECT_DIR="~/motion_sensor_project"

echo "Fixing permissions on the Raspberry Pi..."

# Connect to the Pi and fix permissions
ssh ${PI_USER}@${PI_HOST} "
    # Create directories if they don't exist
    mkdir -p ${PI_PROJECT_DIR}/audio_files
    mkdir -p ${PI_PROJECT_DIR}/idle_sounds
    
    # Take ownership of the directories
    sudo chown -R ${PI_USER}:${PI_USER} ${PI_PROJECT_DIR}
    
    # Set proper permissions
    sudo chmod -R 755 ${PI_PROJECT_DIR}
    
    echo 'Permissions fixed!'
"

echo "Done! Now try copying your files again."
