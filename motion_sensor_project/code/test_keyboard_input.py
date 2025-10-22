#!/usr/bin/env python3
"""
Test script for keyboard input methods
This script tests both the advanced KeyboardTrigger and the simple SimpleKeyboardInput
"""
import time
import sys
import os

def test_callback():
    """Function called when key is pressed"""
    print("\n*** KEY PRESSED! ACTION TRIGGERED! ***\n")

def main():
    print("Keyboard Input Test Script")
    print("=========================")
    
    # Ask which method to test
    print("\nWhich keyboard input method would you like to test?")
    print("1. Advanced (raw terminal mode, no Enter key needed)")
    print("2. Simple (requires Enter key)")
    print("3. Both methods (try advanced first, fall back to simple)")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == '1':
        test_advanced()
    elif choice == '2':
        test_simple()
    elif choice == '3':
        test_both()
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

def test_advanced():
    """Test the advanced KeyboardTrigger"""
    try:
        # Import here to avoid errors if RPi.GPIO is not available
        from motion_sensor import KeyboardTrigger
        
        print("\nTesting Advanced KeyboardTrigger")
        print("===============================")
        
        # Create keyboard trigger for 'w' key
        kt = KeyboardTrigger('w', test_callback)
        
        # Start monitoring
        success = kt.start_monitoring()
        
        if not success:
            print("\nAdvanced keyboard trigger failed to initialize.")
            print("This might be because:")
            print("1. You're not running in an interactive terminal")
            print("2. The terminal doesn't support raw mode")
            print("3. There's another issue with terminal access")
            return False
        
        print("\nPress 'w' key to trigger the action (no Enter needed)")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTest terminated by user")
        finally:
            kt.stop_monitoring()
            kt.cleanup()
            
        return True
        
    except ImportError as e:
        print(f"\nError importing KeyboardTrigger: {e}")
        print("This might be because RPi.GPIO is not available on this system.")
        return False
    except Exception as e:
        print(f"\nError testing advanced keyboard input: {e}")
        return False

def test_simple():
    """Test the simple keyboard input"""
    try:
        from keyboard_input import SimpleKeyboardInput
        
        print("\nTesting Simple Keyboard Input")
        print("===========================")
        
        # Create simple keyboard input for 'w' key
        ski = SimpleKeyboardInput('w', test_callback)
        
        # Start monitoring
        ski.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTest terminated by user")
        finally:
            ski.stop()
            
        return True
        
    except ImportError as e:
        print(f"\nError importing SimpleKeyboardInput: {e}")
        return False
    except Exception as e:
        print(f"\nError testing simple keyboard input: {e}")
        return False

def test_both():
    """Test both methods with fallback"""
    advanced_success = test_advanced()
    
    if not advanced_success:
        print("\nAdvanced keyboard input failed. Trying simple keyboard input...")
        time.sleep(1)
        test_simple()

if __name__ == "__main__":
    # Check if we're running in a proper terminal
    if not sys.stdin.isatty():
        print("ERROR: This script must be run in an interactive terminal.")
        print("It cannot be run from a non-terminal environment.")
        sys.exit(1)
        
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
