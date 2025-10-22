#!/usr/bin/env python3
"""
Fixed keyboard input module for Halloween Scare System
This module provides an improved keyboard input implementation that addresses
potential issues with the 'w' key not working on Raspberry Pi.
"""
import sys
import time
import threading
import select
import os

class ImprovedKeyboardTrigger:
    def __init__(self, key='w', callback=None):
        """
        Initialize the keyboard trigger with improved detection.
        
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
        
        # Store both lowercase and uppercase versions of the key
        self.key_lower = key.lower()
        self.key_upper = key.upper()
        
        # Store ASCII codes for the key
        self.key_code_lower = ord(self.key_lower) if len(self.key_lower) == 1 else None
        self.key_code_upper = ord(self.key_upper) if len(self.key_upper) == 1 else None
    
    def _monitor_keyboard_direct(self):
        """
        Internal method to monitor keyboard using direct file reading.
        This is an alternative approach that might work better on some systems.
        """
        try:
            # Try to open the keyboard device directly
            # This requires appropriate permissions
            keyboard_device = None
            
            # Try different possible keyboard devices
            possible_devices = [
                "/dev/input/by-path/platform-3f980000.usb-usb-0:1.2:1.0-event-kbd",  # Common Pi keyboard path
                "/dev/input/event0",  # First input event device
                "/dev/input/event1",  # Second input event device
                "/dev/input/event2",  # Third input event device
            ]
            
            for device in possible_devices:
                try:
                    if os.path.exists(device):
                        keyboard_device = open(device, "rb")
                        print(f"Successfully opened keyboard device: {device}")
                        break
                except (IOError, PermissionError) as e:
                    print(f"Could not open {device}: {e}")
            
            if keyboard_device is None:
                self.error_message = "Could not open any keyboard device. Try running with sudo."
                print(self.error_message)
                return
            
            print(f"Monitoring for '{self.key}' key presses using direct device access...")
            print(f"Press '{self.key}' to trigger the action or Ctrl+C to exit")
            
            # Simple parsing of keyboard events
            # This is a simplified version and may need adjustment for different keyboards
            while self.running:
                try:
                    # Read event (this is a simplified approach)
                    event = keyboard_device.read(16)  # Basic event size
                    if event:
                        # Very basic parsing - this is just for demonstration
                        # A real implementation would properly parse the input event structure
                        if len(event) >= 16:  # Ensure we have enough data
                            # Extract key code (very simplified)
                            key_code = event[10]  # This position may vary
                            
                            # Check if it's our target key
                            # This is a simplified check and may need adjustment
                            if key_code == self.key_code_lower or key_code == self.key_code_upper:
                                current_time = time.time()
                                if current_time - self.last_press_time > self.debounce_time:
                                    print(f"Key '{self.key}' pressed! Triggering action...")
                                    self.last_press_time = current_time
                                    if self.callback:
                                        try:
                                            self.callback()
                                        except Exception as e:
                                            print(f"Error in key callback: {e}")
                except Exception as e:
                    print(f"Error reading keyboard device: {e}")
                    time.sleep(1)  # Avoid tight loop if there's an error
        except Exception as e:
            self.error_message = f"Error in direct keyboard monitoring: {e}"
            print(self.error_message)
        finally:
            if keyboard_device:
                keyboard_device.close()
    
    def _monitor_keyboard_stdin(self):
        """
        Internal method to monitor keyboard using stdin.
        This is the traditional approach but may have issues on some systems.
        """
        try:
            # Get the file descriptor for stdin
            self.fd = sys.stdin.fileno()
            
            # Save the current terminal settings
            try:
                import termios
                import tty
                
                self.old_settings = termios.tcgetattr(self.fd)
                # Set terminal to raw mode
                tty.setraw(self.fd)
                self.initialized = True
                print(f"Keyboard monitoring initialized successfully for key '{self.key}'")
            except ImportError:
                self.error_message = "termios and tty modules not available. Cannot monitor keyboard."
                print(self.error_message)
                return
            except Exception as e:
                self.error_message = f"Failed to set terminal mode: {e}"
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
                        else:
                            print(f"Debug: Key pressed: '{char}' (code: {key_code})")
                        
                        # Check for both lowercase and uppercase versions of the key
                        if char.lower() == self.key_lower:
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
    
    def start_monitoring(self, method="stdin"):
        """
        Start monitoring for keyboard input in a separate thread.
        
        Args:
            method: The method to use for keyboard monitoring.
                   "stdin" uses the standard input approach.
                   "direct" tries to access the keyboard device directly.
        
        Returns True if monitoring started successfully, False otherwise.
        """
        if self.thread is not None and self.thread.is_alive():
            print("Keyboard monitoring is already running.")
            return True
            
        self.running = True
        self.error_message = None
        self.initialized = False
        
        # Create and start the monitoring thread
        if method == "direct":
            self.thread = threading.Thread(target=self._monitor_keyboard_direct)
        else:
            self.thread = threading.Thread(target=self._monitor_keyboard_stdin)
            
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
                import termios
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
                print("Terminal settings restored.")
            except ImportError:
                pass  # termios not available
            except Exception as e:
                print(f"Error restoring terminal settings: {e}")
        
        # Reset state variables
        self.initialized = False

# Example usage
if __name__ == "__main__":
    def test_callback():
        print("\n*** KEY PRESSED! ACTION TRIGGERED! ***\n")
    
    # Create keyboard trigger for 'w' key
    print("Testing ImprovedKeyboardTrigger...")
    keyboard = ImprovedKeyboardTrigger('w', test_callback)
    
    # Ask which method to use
    print("\nWhich keyboard monitoring method would you like to use?")
    print("1. Standard input (stdin) - works in most terminals")
    print("2. Direct device access - may require sudo")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == '2':
        method = "direct"
    else:
        method = "stdin"
    
    # Start monitoring
    keyboard.start_monitoring(method=method)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        keyboard.stop_monitoring()
        keyboard.cleanup()
