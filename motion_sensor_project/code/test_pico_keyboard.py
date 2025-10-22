#!/usr/bin/env python3
"""
Test script for Pico keyboard input
This script is specifically designed to detect input from a Pico Pi programmed as a keyboard
"""
import time
import sys
import os

def test_callback():
    """Function called when key is pressed"""
    print("\n*** KEY PRESSED! ACTION TRIGGERED! ***\n")

def main():
    print("Pico Keyboard Input Test")
    print("=======================")
    print("This test is specifically for a Pico Pi programmed to act as a keyboard")
    print("It will detect when the Pico sends a 'w' key press")
    
    try:
        from pico_keyboard_input import PicoKeyboardInput
    except ImportError:
        print("Error: Could not import PicoKeyboardInput class.")
        print("Make sure the pico_keyboard_input.py file is in the same directory.")
        return
    
    # Ask which key to monitor
    print("\nWhich key is your Pico programmed to send?")
    key = input("Enter a key (default is 'w'): ").strip() or 'w'
    
    # Create keyboard input handler
    print(f"\nCreating PicoKeyboardInput for '{key}' key...")
    keyboard = PicoKeyboardInput(key, test_callback)
    
    # Ask which method to use
    print("\nWhich monitoring method would you like to use?")
    print("1. Monitor all input devices (recommended)")
    print("2. Monitor raw HID devices only")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == '2':
        method = "raw"
    else:
        method = "all"
    
    # Start monitoring
    print(f"\nStarting keyboard monitoring using {method} method...")
    keyboard.start(method=method)
    
    print("\nMonitoring started!")
    print(f"Trigger your Pico to send the '{key}' key.")
    print("Press Ctrl+C in this terminal to exit.")
    
    # Display additional debugging info
    print("\nDebugging information:")
    print(f"- Key to monitor: '{key}'")
    print(f"- Expected key code: {keyboard.key_code}")
    
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
