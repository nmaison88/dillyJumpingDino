#!/usr/bin/env python3
"""
Keyboard Diagnostic Tool for Halloween Scare System
This script helps diagnose issues with keyboard input on the Raspberry Pi.
"""
import sys
import time
import os
import termios
import tty
import select
import threading

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60 + "\n")

def test_raw_key_input():
    """Test raw key input without any wrappers"""
    print_header("RAW KEYBOARD INPUT TEST")
    print("This test will capture raw keyboard input and show key codes.")
    print("Press any keys to see their codes. Press Ctrl+C to exit.")
    
    fd = sys.stdin.fileno()
    old_settings = None
    
    try:
        # Save terminal settings
        old_settings = termios.tcgetattr(fd)
        
        # Set terminal to raw mode
        tty.setraw(fd)
        
        print("\nTerminal set to raw mode successfully!")
        print("Now press keys (including 'w') to see their codes...")
        print("Press Ctrl+C to exit")
        
        while True:
            # Wait for input with timeout
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                char = sys.stdin.read(1)
                key_code = ord(char)
                
                # Print the key info
                if key_code == 119 or key_code == 87:  # 'w' or 'W'
                    print(f"\n>>> KEY PRESSED: '{char}' (ASCII: {key_code}) - THIS IS THE W KEY! <<<")
                elif key_code < 32:
                    print(f"Key pressed: Control character (ASCII: {key_code})")
                    if key_code == 3:  # Ctrl+C
                        print("Ctrl+C detected, exiting...")
                        break
                else:
                    print(f"Key pressed: '{char}' (ASCII: {key_code})")
                    
    except Exception as e:
        print(f"\nError in raw keyboard test: {e}")
    finally:
        # Restore terminal settings
        if old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("\nTerminal settings restored.")

def test_keyboard_trigger():
    """Test the KeyboardTrigger class"""
    print_header("KEYBOARD TRIGGER CLASS TEST")
    
    try:
        # Import the KeyboardTrigger class
        from motion_sensor import KeyboardTrigger
        
        # Define a simple callback
        def key_callback():
            print("\n>>> W KEY DETECTED! CALLBACK TRIGGERED! <<<\n")
        
        # Create a keyboard trigger for 'w' key
        print("Creating KeyboardTrigger for 'w' key...")
        kt = KeyboardTrigger('w', callback=key_callback)
        
        # Start monitoring
        print("Starting keyboard monitoring...")
        success = kt.start_monitoring()
        
        if not success:
            print("\nFailed to initialize keyboard monitoring.")
            print("This might be because:")
            print("1. Terminal doesn't support raw mode")
            print("2. Another process is using the terminal")
            print("3. There's an issue with terminal access permissions")
            return False
        
        print("\nKeyboard monitoring started successfully!")
        print("Press 'w' key to trigger the callback")
        print("Press Ctrl+C to exit")
        
        # Add a debug loop to check key presses
        print("\nStarting debug loop to check key presses...")
        try:
            while True:
                time.sleep(0.1)
                if kt.is_key_pressed():
                    print("Key press detected in debug loop!")
        except KeyboardInterrupt:
            print("\nTest terminated by user")
        finally:
            kt.stop_monitoring()
            kt.cleanup()
            
        return True
        
    except ImportError as e:
        print(f"\nError importing KeyboardTrigger: {e}")
        return False
    except Exception as e:
        print(f"\nError in KeyboardTrigger test: {e}")
        return False

def test_simple_keyboard():
    """Test the SimpleKeyboardInput class"""
    print_header("SIMPLE KEYBOARD INPUT TEST")
    
    try:
        # Import the SimpleKeyboardInput class
        from keyboard_input import SimpleKeyboardInput
        
        # Define a simple callback
        def key_callback():
            print("\n>>> W KEY DETECTED! CALLBACK TRIGGERED! <<<\n")
        
        # Create a simple keyboard input for 'w' key
        print("Creating SimpleKeyboardInput for 'w' key...")
        ski = SimpleKeyboardInput('w', callback=key_callback)
        
        # Start monitoring
        print("Starting simple keyboard input...")
        ski.start()
        
        print("\nSimple keyboard input started!")
        print("Type 'w' and press Enter to trigger the callback")
        print("Type 'exit' to quit")
        print("Press Ctrl+C to exit")
        
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
        print(f"\nError in SimpleKeyboardInput test: {e}")
        return False

def check_environment():
    """Check the environment for potential issues"""
    print_header("ENVIRONMENT CHECK")
    
    # Check if running in an interactive terminal
    print("Checking if running in an interactive terminal...")
    if sys.stdin.isatty():
        print("✓ Running in an interactive terminal")
    else:
        print("✗ Not running in an interactive terminal - keyboard input may not work")
    
    # Check if TERM environment variable is set
    print("\nChecking TERM environment variable...")
    term = os.environ.get('TERM')
    if term:
        print(f"✓ TERM is set to: {term}")
    else:
        print("✗ TERM environment variable not set - terminal capabilities may be limited")
    
    # Check for DISPLAY (for GUI)
    print("\nChecking DISPLAY environment variable...")
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✓ DISPLAY is set to: {display}")
    else:
        print("✗ DISPLAY environment variable not set - GUI may not work")
        
    # Check if we can access the terminal settings
    print("\nChecking terminal settings access...")
    try:
        fd = sys.stdin.fileno()
        settings = termios.tcgetattr(fd)
        print("✓ Successfully accessed terminal settings")
    except Exception as e:
        print(f"✗ Failed to access terminal settings: {e}")
    
    # Check Python version
    print("\nChecking Python version...")
    print(f"✓ Python version: {sys.version}")
    
    # Check for required modules
    print("\nChecking for required modules...")
    required_modules = ['termios', 'tty', 'select', 'threading', 'time']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ Module '{module}' is available")
        except ImportError:
            print(f"✗ Module '{module}' is not available")

def main():
    print_header("KEYBOARD DIAGNOSTIC TOOL")
    print("This tool will help diagnose issues with the 'w' key on your Raspberry Pi.")
    
    # Check environment first
    check_environment()
    
    # Menu
    while True:
        print_header("DIAGNOSTIC MENU")
        print("1. Test raw keyboard input (most basic test)")
        print("2. Test KeyboardTrigger class (used in main.py)")
        print("3. Test SimpleKeyboardInput class (fallback method)")
        print("4. Check environment (terminal settings, etc.)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            test_raw_key_input()
        elif choice == '2':
            test_keyboard_trigger()
        elif choice == '3':
            test_simple_keyboard()
        elif choice == '4':
            check_environment()
        elif choice == '5':
            print("\nExiting keyboard diagnostic tool.")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostic tool terminated by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
