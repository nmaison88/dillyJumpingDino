#!/usr/bin/env python3
"""
Standalone script to run just the GUI interface for testing
"""
import os
import sys
import time

# Add the current directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the GUI module
import gui_interface

def test_callback():
    """Test callback function for the GUI button"""
    print("\n[TEST] Button pressed! Feeding the beast...")
    print("[TEST] Activating output device...")
    time.sleep(1)
    print("[TEST] Playing beast feeding sounds...")
    time.sleep(2)
    print("[TEST] Deactivating output device...")
    print("[TEST] Beast feeding complete!")

if __name__ == "__main__":
    print("Starting 'Feed the Beast' GUI in test mode...")
    print("This is a standalone test. The physical hardware will not be activated.")
    
    # Check if display is available
    if not gui_interface.is_display_available():
        print("\nERROR: No display available for GUI!")
        print("To run the GUI, you need one of the following:")
        print("  1. Run this on the Raspberry Pi with a desktop environment")
        print("  2. Use SSH with X11 forwarding: ssh -X admin@yumpi")
        print("  3. Set the DISPLAY environment variable: export DISPLAY=:0")
        print("\nTrying to auto-detect and set display...")
        
        # Try to auto-detect display
        import os
        if os.path.exists('/dev/fb0'):
            print("Framebuffer detected. Trying to set DISPLAY=:0")
            os.environ['DISPLAY'] = ':0'
            if gui_interface.is_display_available():
                print("Display connection successful!")
            else:
                print("Still no display available. Exiting.")
                sys.exit(1)
        else:
            print("No framebuffer detected. Exiting.")
            sys.exit(1)
    
    print("Press the 'FEED BEAST' button to simulate feeding the beast.")
    
    # Run the GUI with our test callback
    success = gui_interface.run_gui(test_callback)
    
    if not success:
        print("Failed to start GUI. Exiting.")
        sys.exit(1)
