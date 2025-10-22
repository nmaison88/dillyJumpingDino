#!/usr/bin/env python3
"""
Test script for the improved keyboard input implementation
"""
import time
import sys
from fixed_keyboard_input import ImprovedKeyboardTrigger

def test_callback():
    """Function called when key is pressed"""
    print("\n*** W KEY PRESSED! ACTION TRIGGERED! ***\n")

def main():
    print("Improved Keyboard Input Test")
    print("===========================")
    
    # Ask which method to use
    print("\nWhich keyboard monitoring method would you like to use?")
    print("1. Standard input (stdin) - works in most terminals")
    print("2. Direct device access - may require sudo")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == '2':
        method = "direct"
        print("\nNote: Direct device access may require running with sudo")
        print("If it doesn't work, try: sudo python3 test_fixed_keyboard.py")
    else:
        method = "stdin"
    
    # Create keyboard trigger for 'w' key
    print("\nCreating ImprovedKeyboardTrigger for 'w' key...")
    keyboard = ImprovedKeyboardTrigger('w', test_callback)
    
    # Start monitoring
    print(f"Starting keyboard monitoring using {method} method...")
    success = keyboard.start_monitoring(method=method)
    
    if not success:
        print("\nFailed to start keyboard monitoring.")
        print("Try the other method or run with sudo.")
        return
    
    print("\nKeyboard monitoring started successfully!")
    print("Press 'w' key to trigger the callback")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    finally:
        keyboard.stop_monitoring()
        keyboard.cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
