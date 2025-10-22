#!/usr/bin/env python3
"""
Alternative keyboard input module for Halloween Scare System
This module provides a simpler keyboard input method that works in more environments
"""
import threading
import time

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

# Example usage
if __name__ == "__main__":
    def test_callback():
        print("Action triggered!")
    
    keyboard = SimpleKeyboardInput('w', test_callback)
    keyboard.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        keyboard.stop()
