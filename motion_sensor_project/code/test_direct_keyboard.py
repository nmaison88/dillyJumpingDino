#!/usr/bin/env python3
"""
Test script for direct keyboard input with physical keyboard
This script tests the DirectKeyboardInput class with a physical keyboard plugged into the Pi
"""
import time
import sys
import os

def test_callback():
    """Function called when key is pressed"""
    print("\n*** KEY PRESSED! ACTION TRIGGERED! ***\n")

def main():
    print("Direct Keyboard Input Test")
    print("=========================")
    print("This test is specifically for physical keyboards plugged directly into the Pi")
    print("It will NOT work through SSH unless you're using X forwarding")
    
    try:
        from direct_keyboard_input import DirectKeyboardInput
    except ImportError:
        print("Error: Could not import DirectKeyboardInput class.")
        print("Make sure the direct_keyboard_input.py file is in the same directory.")
        return
    
    # Ask which key to monitor
    print("\nWhich key would you like to test?")
    key = input("Enter a key (default is 'w'): ").strip() or 'w'
    
    print(f"\nCreating DirectKeyboardInput for '{key}' key...")
    keyboard = DirectKeyboardInput(key, test_callback)
    
    print("\nStarting keyboard monitoring...")
    keyboard.start()
    
    print("\nKeyboard monitoring started!")
    print(f"Press '{key}' on the PHYSICAL KEYBOARD connected to the Pi to trigger the action.")
    print("Press Ctrl+C in this terminal to exit.")
    
    # Display additional debugging info
    print("\nDebugging information:")
    print(f"- Key to monitor: '{key}'")
    print(f"- Expected key code: {keyboard.key_code}")
    print("- Available keyboard devices:")
    
    # List potential keyboard devices
    possible_devices = [
        "/dev/input/by-path/platform-3f980000.usb-usb-0:1.2:1.0-event-kbd",
        "/dev/input/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-event-kbd",
        "/dev/input/by-id/usb-Generic_USB_Keyboard-event-kbd"
    ]
    
    # Add event devices to the list
    for i in range(10):
        possible_devices.append(f"/dev/input/event{i}")
    
    # Check which devices exist
    for device in possible_devices:
        if os.path.exists(device):
            try:
                # Try to open the device for reading
                fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
                os.close(fd)
                print(f"  ✓ {device} (accessible)")
            except PermissionError:
                print(f"  ✗ {device} (permission denied - try running with sudo)")
            except Exception as e:
                print(f"  ✗ {device} (error: {e})")
        else:
            print(f"  - {device} (not found)")
    
    # Main loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    finally:
        keyboard.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
