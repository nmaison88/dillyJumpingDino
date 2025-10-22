#!/usr/bin/env python3
"""
Test script for keyboard input methods with mocked GPIO
"""
import sys
import time
import threading
import termios
import tty
import select

class KeyboardTrigger:
    def __init__(self, key='w', callback=None):
        """
        Initialize the keyboard trigger.
        
        Args:
            key: Key to trigger the action (default is 'w')
            callback: Function to call when key is pressed
        """
        self.key = key
        self.callback = callback
        self.last_press_time = 0
        self.debounce_time = 0.3  # 300ms debounce to avoid multiple triggers
        self.running = False
        self.thread = None
        self.old_settings = None
        self.fd = None
        self.initialized = False
        self.error_message = None
    
    def is_key_pressed(self):
        """
        Check if the target key is currently pressed.
        This is a non-blocking check.
        
        Returns True if key is pressed, False otherwise.
        """
        if self.fd is None or not self.initialized:
            return False
            
        try:
            r, _, _ = select.select([self.fd], [], [], 0)
            if r:
                char = sys.stdin.read(1)
                # Put the character back for the next read
                termios.tcflush(self.fd, termios.TCIFLUSH)
                return char.lower() == self.key.lower()
        except Exception as e:
            print(f"Error checking key press: {e}")
        return False
    
    def _monitor_keyboard(self):
        """
        Internal method to monitor keyboard in a separate thread.
        """
        try:
            # Get the file descriptor for stdin
            self.fd = sys.stdin.fileno()
            
            # Save the current terminal settings
            try:
                self.old_settings = termios.tcgetattr(self.fd)
                # Set terminal to raw mode
                tty.setraw(self.fd)
                self.initialized = True
                print(f"Keyboard monitoring initialized successfully for key '{self.key}'")
            except termios.error as e:
                self.error_message = f"Failed to set terminal mode: {e}. Make sure you're running in an interactive terminal."
                print(self.error_message)
                return
            except Exception as e:
                self.error_message = f"Unexpected error setting up terminal: {e}"
                print(self.error_message)
                return
            
            print(f"Monitoring for '{self.key}' key presses...")
            print(f"Press '{self.key}' to trigger the action or Ctrl+C to exit")
            
            while self.running:
                try:
                    # Wait for input with timeout
                    r, _, _ = select.select([self.fd], [], [], 0.1)
                    if r:
                        char = sys.stdin.read(1)
                        
                        # Debug output to see what key was pressed
                        key_code = ord(char)
                        if key_code < 32 or key_code > 126:
                            print(f"Debug: Non-printable key pressed, code: {key_code}")
                        
                        if char.lower() == self.key.lower():
                            current_time = time.time()
                            if current_time - self.last_press_time > self.debounce_time:
                                print(f"Key '{self.key}' pressed! Triggering action...")
                                self.last_press_time = current_time
                                if self.callback:
                                    try:
                                        self.callback()
                                    except Exception as e:
                                        print(f"Error in key callback: {e}")
                        
                        # Exit if Ctrl+C is pressed
                        if char == '\x03':
                            print("Keyboard monitoring stopped (Ctrl+C).")
                            self.running = False
                            break
                except Exception as e:
                    print(f"Error reading keyboard input: {e}")
                    time.sleep(1)  # Avoid tight loop if there's an error
        except Exception as e:
            self.error_message = f"Error in keyboard monitoring thread: {e}"
            print(self.error_message)
        finally:
            self.cleanup()
    
    def start_monitoring(self):
        """
        Start monitoring for keyboard input in a separate thread.
        Returns True if monitoring started successfully, False otherwise.
        """
        if self.thread is not None and self.thread.is_alive():
            print("Keyboard monitoring is already running.")
            return True
            
        self.running = True
        self.error_message = None
        self.initialized = False
        
        # Create and start the monitoring thread
        self.thread = threading.Thread(target=self._monitor_keyboard)
        self.thread.daemon = True
        self.thread.start()
        
        # Give the thread a moment to initialize
        time.sleep(0.5)
        
        # Check if initialization was successful
        if self.error_message is not None:
            print(f"Failed to start keyboard monitoring: {self.error_message}")
            return False
            
        # Provide clear instructions to the user
        print("\nKeyboard input is now active!")
        print(f"Make sure this terminal window has focus when pressing the '{self.key}' key.")
        print("If keyboard input doesn't work, try running the program in a different terminal.\n")
        
        return True
    
    def stop_monitoring(self):
        """
        Stop monitoring for keyboard input.
        """
        if not self.running:
            return
            
        print("Stopping keyboard monitoring...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=1.0)
                if self.thread.is_alive():
                    print("Warning: Keyboard monitoring thread did not exit cleanly.")
                else:
                    print("Keyboard monitoring stopped successfully.")
            except Exception as e:
                print(f"Error stopping keyboard thread: {e}")
    
    def cleanup(self):
        """
        Restore terminal settings.
        """
        if self.fd is not None and self.old_settings is not None:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
                print("Terminal settings restored.")
            except Exception as e:
                print(f"Error restoring terminal settings: {e}")
        
        # Reset state variables
        self.initialized = False

class SimpleKeyboardInput:
    def __init__(self, key='w', callback=None):
        """
        Initialize the keyboard input handler.
        
        Args:
            key: Key to trigger the action (default is 'w')
            callback: Function to call when key is pressed
        """
        self.key = key
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_press_time = 0
        self.debounce_time = 0.3  # 300ms debounce
    
    def _input_loop(self):
        """
        Internal method to monitor for keyboard input in a separate thread.
        Uses standard input() which works in more environments but requires Enter key.
        """
        print(f"\nSimple keyboard input is now active!")
        print(f"Type '{self.key}' and press Enter to trigger the action.")
        print("Type 'exit' to quit.\n")
        
        while self.running:
            try:
                user_input = input(f"Press '{self.key}' and Enter to trigger (or 'exit'): ")
                
                # Check for exit command
                if user_input.lower() == 'exit':
                    print("Keyboard input stopped.")
                    self.running = False
                    break
                
                # Check for trigger key
                if self.key.lower() in user_input.lower():
                    current_time = time.time()
                    if current_time - self.last_press_time > self.debounce_time:
                        print(f"Key '{self.key}' detected! Triggering action...")
                        self.last_press_time = current_time
                        if self.callback:
                            try:
                                self.callback()
                            except Exception as e:
                                print(f"Error in key callback: {e}")
            except KeyboardInterrupt:
                print("\nKeyboard input stopped (Ctrl+C).")
                self.running = False
                break
            except Exception as e:
                print(f"Error reading input: {e}")
                time.sleep(1)  # Avoid tight loop if there's an error
    
    def start(self):
        """
        Start monitoring for keyboard input in a separate thread.
        """
        if self.thread is not None and self.thread.is_alive():
            print("Keyboard input is already running.")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._input_loop)
        self.thread.daemon = True
        self.thread.start()
        return self.thread
    
    def stop(self):
        """
        Stop monitoring for keyboard input.
        """
        self.running = False
        if self.thread and self.thread.is_alive():
            print("Waiting for keyboard input thread to exit...")
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                print("Warning: Keyboard input thread did not exit cleanly.")
            else:
                print("Keyboard input stopped successfully.")

def test_callback():
    print('\n*** KEY PRESSED! CALLBACK TRIGGERED! ***\n')

def main():
    print("Keyboard Input Test Script")
    print("==========================")
    
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

def test_simple():
    """Test the simple keyboard input"""
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
