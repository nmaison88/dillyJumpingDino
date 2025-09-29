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

def disable_kiosk_mode():
    """Disable kiosk mode by removing autostart files and systemd service"""
    try:
        # Disable and remove systemd service
        print("Disabling systemd service...")
        try:
            subprocess.run(["sudo", "systemctl", "stop", "halloween-scare.service"], check=False)
            subprocess.run(["sudo", "systemctl", "disable", "halloween-scare.service"], check=False)
            subprocess.run(["sudo", "rm", "/etc/systemd/system/halloween-scare.service"], check=False)
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=False)
            print("Systemd service disabled and removed")
        except Exception as e:
            print(f"Error disabling systemd service: {e}")
        
        # Remove autostart file
        create_autostart_file(False)
        
        # Remove screen blanking script
        try:
            if os.path.exists("/usr/local/bin/screen_blanking.sh"):
                subprocess.run(["sudo", "rm", "/usr/local/bin/screen_blanking.sh"], check=False)
                print("Removed screen blanking script")
        except Exception as e:
            print(f"Error removing screen blanking script: {e}")
            
        print("\nKiosk mode has been disabled.")
        print("The Halloween Scare System will no longer start automatically on boot.")
        return True
    except Exception as e:
        print(f"Error disabling kiosk mode: {e}")
        return False

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
Exec=lxterminal -e 'bash -c "cd {PROJECT_DIR} && DISPLAY=:0 sudo python3 code/main.py; bash"'
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
        else:
            print("No autostart file found.")

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
        
        # Create scripts to disable screen blanking (try multiple locations for compatibility)
        print("Disabling screen blanking...")
        
        # Common autostart content
        autostart_content = """@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
"""
        
        # Try multiple locations for different Raspberry Pi OS versions
        autostart_paths = [
            "/etc/xdg/lxsession/LXDE-pi/autostart",
            os.path.expanduser("~/.config/lxsession/LXDE-pi/autostart"),
            "/etc/xdg/lxsession/LXDE/autostart",
            os.path.expanduser("~/.config/lxsession/LXDE/autostart")
        ]
        
        success = False
        for path in autostart_paths:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(autostart_content)
                print(f"Created autostart file at: {path}")
                success = True
            except Exception as e:
                print(f"Could not create {path}: {e}")
        
        if not success:
            print("Warning: Could not create any autostart files for screen blanking prevention.")
            
        # Also create a script in /etc/rc.local for additional screen blanking prevention
        try:
            with open("/tmp/screen_blanking.sh", "w") as f:
                f.write("""#!/bin/bash
xset s off
xset -dpms
xset s noblank
""")
            subprocess.run(["sudo", "chmod", "+x", "/tmp/screen_blanking.sh"], check=False)
            subprocess.run(["sudo", "mv", "/tmp/screen_blanking.sh", "/usr/local/bin/screen_blanking.sh"], check=False)
            print("Created screen blanking prevention script at /usr/local/bin/screen_blanking.sh")
        except Exception as e:
            print(f"Could not create screen blanking script: {e}")
            
        # Create a systemd service for more reliable startup
        try:
            service_content = f"""[Unit]
Description=Halloween Scare System
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory={PROJECT_DIR}
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 {os.path.join(PROJECT_DIR, 'code/main.py')}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
            
            with open("/tmp/halloween-scare.service", "w") as f:
                f.write(service_content)
                
            subprocess.run(["sudo", "mv", "/tmp/halloween-scare.service", "/etc/systemd/system/"], check=False)
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=False)
            subprocess.run(["sudo", "systemctl", "enable", "halloween-scare.service"], check=False)
            print("Created and enabled systemd service for Halloween Scare System")
        except Exception as e:
            print(f"Could not create systemd service: {e}")
        
        # Set up autostart
        create_autostart_file(True)
        
        print("\nKiosk mode setup complete!")
        print("The system will now boot directly into the Halloween Scare GUI.")
        print("To disable kiosk mode, run: sudo python3 kiosk_mode.py --disable")
        return True
        
    except Exception as e:
        print(f"Error setting up kiosk mode: {e}")
        return False

def check_kiosk_mode_status():
    """Check the current status of kiosk mode components"""
    print("\n=== Halloween Scare System Kiosk Mode Status ===")
    
    # Check autostart file
    autostart_file = os.path.expanduser('~/.config/autostart/halloween_scare.desktop')
    if os.path.exists(autostart_file):
        print("✓ Autostart file: ENABLED")
    else:
        print("✗ Autostart file: NOT FOUND")
    
    # Check systemd service
    try:
        result = subprocess.run(["systemctl", "is-enabled", "halloween-scare.service"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if "enabled" in result.stdout:
            print("✓ Systemd service: ENABLED")
        else:
            print("✗ Systemd service: DISABLED")
            
        result = subprocess.run(["systemctl", "is-active", "halloween-scare.service"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if "active" in result.stdout:
            print("✓ Systemd service status: RUNNING")
        else:
            print("✗ Systemd service status: NOT RUNNING")
    except Exception:
        print("? Systemd service: UNKNOWN (could not check status)")
    
    # Check screen blanking prevention
    if os.path.exists("/usr/local/bin/screen_blanking.sh"):
        print("✓ Screen blanking prevention: INSTALLED")
    else:
        print("✗ Screen blanking prevention: NOT INSTALLED")
    
    print("\nTo set up kiosk mode: sudo python3 code/kiosk_mode.py --setup")
    print("To disable kiosk mode: sudo python3 code/kiosk_mode.py --disable")

def main():
    """Main function to parse arguments and run the appropriate action"""
    parser = argparse.ArgumentParser(description="Halloween Scare System Kiosk Mode Setup")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--setup", action="store_true", help="Set up kiosk mode (requires sudo)")
    group.add_argument("--enable", action="store_true", help="Enable autostart only")
    group.add_argument("--disable", action="store_true", help="Disable kiosk mode completely (requires sudo)")
    group.add_argument("--status", action="store_true", help="Check kiosk mode status")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_kiosk_mode()
    elif args.disable:
        disable_kiosk_mode()
    elif args.enable:
        create_autostart_file(True)
    elif args.status:
        check_kiosk_mode_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
