#!/bin/bash
# Script to set up the Halloween Scare System to run headless on boot
# This script must be run with sudo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Copy the service file to systemd directory
echo "Installing systemd service..."
cp "$SCRIPT_DIR/halloween-scare.service" /etc/systemd/system/

# Reload systemd to recognize the new service
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable halloween-scare.service
echo "Service enabled to start on boot"

# Ask if user wants to start the service now
read -p "Do you want to start the Halloween Scare System now? (y/n): " START_NOW
if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    systemctl start halloween-scare.service
    echo "Service started. Check status with: sudo systemctl status halloween-scare.service"
else
    echo "Service not started. You can start it manually with: sudo systemctl start halloween-scare.service"
    echo "Or reboot to have it start automatically"
fi

echo ""
echo "Headless setup complete! The Halloween Scare System will now run on boot."
echo "You can control it with these commands:"
echo "  - Check status: sudo systemctl status halloween-scare.service"
echo "  - Start service: sudo systemctl start halloween-scare.service"
echo "  - Stop service:  sudo systemctl stop halloween-scare.service"
echo "  - View logs:     sudo journalctl -u halloween-scare.service"
