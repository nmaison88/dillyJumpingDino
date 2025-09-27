#!/usr/bin/env python3
"""
Kiosk Mode for Halloween Scare System
This script sets up the Raspberry Pi to run the GUI in kiosk mode on startup
"""
import os
import sys
import subprocess
import argparse

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

def create_autostart_file(enable=True):
    """Create or remove the autostart file for the kiosk mode"""
    # Define the autostart directory and file
    autostart_dir = os.path.expanduser('~/.config/autostart')
    autostart_file = os.path.join(autostart_dir, 'halloween_scare.desktop')
    
    if enable:
        # Create the autostart directory if it doesn't exist
        os.makedirs(autostart_dir, exist_ok=True)
        
        # Create the desktop file content
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Halloween Scare System
Comment=Starts the Halloween Scare System in kiosk mode
Exec=sudo python3 {os.path.join(PROJECT_DIR, 'code/main.py')}
Terminal=false
X-GNOME-Autostart-enabled=true
"""
        
        # Write the desktop file
        with open(autostart_file, 'w') as f:
            f.write(desktop_content)
        
        print(f"Autostart file created at: {autostart_file}")
        print("The Halloween Scare System will now start automatically on boot.")
    else:
        # Remove the autostart file if it exists
        if os.path.exists(autostart_file):
            os.remove(autostart_file)
            print(f"Autostart file removed: {autostart_file}")
            print("The Halloween Scare System will no longer start automatically on boot.")
        else:
            print("No autostart file found. Nothing to disable.")

def setup_kiosk_mode():
    """Set up the Raspberry Pi for kiosk mode"""
    # Check if running as root
    if os.geteuid() != 0:
        print("This script must be run as root (sudo) to set up kiosk mode.")
        print("Please run: sudo python3 kiosk_mode.py --setup")
        return False
    
    try:
        # Install required packages
        print("Installing required packages...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "xserver-xorg", "x11-xserver-utils", 
                       "lightdm", "unclutter", "python3-tk"], check=True)
        
        # Create a script to disable screen blanking
        print("Disabling screen blanking...")
        with open("/etc/xdg/lxsession/LXDE-pi/autostart", "w") as f:
            f.write("""@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
""")
        
        # Set up autostart
        create_autostart_file(True)
        
        print("\nKiosk mode setup complete!")
        print("The system will now boot directly into the Halloween Scare GUI.")
        print("To disable kiosk mode, run: sudo python3 kiosk_mode.py --disable")
        return True
        
    except Exception as e:
        print(f"Error setting up kiosk mode: {e}")
        return False

def main():
    """Main function to parse arguments and run the appropriate action"""
    parser = argparse.ArgumentParser(description="Halloween Scare System Kiosk Mode Setup")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--setup", action="store_true", help="Set up kiosk mode")
    group.add_argument("--enable", action="store_true", help="Enable autostart")
    group.add_argument("--disable", action="store_true", help="Disable autostart")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_kiosk_mode()
    elif args.disable:
        create_autostart_file(False)
    elif args.enable:
        create_autostart_file(True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
