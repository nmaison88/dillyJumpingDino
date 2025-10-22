#!/bin/bash
# Script to disable the Halloween Scare System headless service
# This script must be run with sudo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Stop the service if it's running
echo "Stopping the Halloween Scare service..."
systemctl stop halloween-scare.service

# Disable the service so it doesn't start on boot
echo "Disabling the Halloween Scare service..."
systemctl disable halloween-scare.service

echo "Service disabled. It will no longer start on boot."
echo "To completely remove the service, also run: sudo rm /etc/systemd/system/halloween-scare.service"
