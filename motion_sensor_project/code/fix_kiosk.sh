#!/bin/sh
# Fix Kiosk Mode Script for Halloween Scare System
# This script helps troubleshoot and fix common kiosk mode issues

# Simple output without colors for maximum compatibility
echo "========================================="
echo "   Halloween Scare System Fix Tool    "
echo "========================================="
echo

# Check if running as root
if [ "$(id -u)" != "0" ]; then
  echo "Please run as root (sudo)"
  echo "Usage: sudo sh fix_kiosk.sh"
  exit 1
fi

# Get project directory - compatible with sh
SCRIPT_PATH="$0"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo "Project directory: $PROJECT_DIR"

# Function to check if a package is installed
check_package() {
  if dpkg -s "$1" >/dev/null 2>&1; then
    echo "✓ $1 is installed"
    return 0
  else
    echo "✗ $1 is not installed"
    return 1
  fi
}

# Check required packages
echo "
Checking required packages..."
MISSING_PACKAGES=""

# Check each package individually (no arrays in sh)
check_pkg() {
  if ! check_package "$1"; then
    MISSING_PACKAGES="$MISSING_PACKAGES $1"
  fi
}

check_pkg "xserver-xorg"
check_pkg "x11-xserver-utils"
check_pkg "lightdm"
check_pkg "unclutter"
check_pkg "python3-tk"
check_pkg "python3-pip"
check_pkg "python3-pygame"

# Install missing packages
if [ -n "$MISSING_PACKAGES" ]; then
  echo "
Installing missing packages..."
  apt-get update
  # Use xargs to handle the package list
  echo $MISSING_PACKAGES | xargs apt-get install -y
  echo "Package installation complete"
fi

# Fix permissions
echo "
Fixing permissions..."
chmod +x "$PROJECT_DIR/code/main.py"
chmod +x "$PROJECT_DIR/code/gui_interface.py"
chmod +x "$PROJECT_DIR/code/kiosk_mode.py"
echo "Permissions fixed"

# Create systemd service
echo "
Creating systemd service..."
cat > /etc/systemd/system/halloween-scare.service << EOF
[Unit]
Description=Halloween Scare System
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 $PROJECT_DIR/code/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable halloween-scare.service
echo "Systemd service created and enabled"

# Fix screen blanking
echo "
Fixing screen blanking..."
mkdir -p /etc/xdg/lxsession/LXDE-pi
cat > /etc/xdg/lxsession/LXDE-pi/autostart << EOF
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
EOF

# Create screen blanking prevention script
cat > /usr/local/bin/screen_blanking.sh << EOF
#!/bin/sh
xset s off
xset -dpms
xset s noblank
EOF
chmod +x /usr/local/bin/screen_blanking.sh
echo "Screen blanking prevention configured"

# Create user autostart directory
# Get the home directory of the user who ran sudo
if [ -n "$SUDO_USER" ]; then
  USER_HOME="/home/$SUDO_USER"
else
  USER_HOME="/home/pi"
fi

mkdir -p "$USER_HOME/.config/autostart"
cat > "$USER_HOME/.config/autostart/halloween_scare.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Halloween Scare System
Comment=Starts the Halloween Scare System in kiosk mode
Exec=lxterminal -e 'sh -c "cd $PROJECT_DIR && DISPLAY=:0 sudo python3 code/main.py; sh"'
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Set correct ownership
if [ -n "$SUDO_USER" ]; then
  chown -R "$SUDO_USER:$SUDO_USER" "$USER_HOME/.config/autostart"
fi
echo "User autostart file created"

# Fix display environment
echo "
Setting up display environment..."
if ! grep -q "export DISPLAY=:0" /etc/profile; then
  echo "export DISPLAY=:0" >> /etc/profile
  echo "Added DISPLAY=:0 to /etc/profile"
else
  echo "DISPLAY environment variable already configured"
fi

# Fix audio
echo "
Configuring audio..."
amixer cset numid=3 1 >/dev/null 2>&1
amixer set Master 100% >/dev/null 2>&1
echo "Audio configured to use headphone jack"

echo "
All fixes applied!"
echo "Reboot the system to apply all changes: sudo reboot"
echo
echo "If issues persist after reboot, try:"
echo "1. Check logs: sudo journalctl -u halloween-scare.service"
echo "2. Test GUI manually: python3 $PROJECT_DIR/code/run_gui.py"
echo "3. Test the full system: sudo python3 $PROJECT_DIR/code/main.py"
echo
