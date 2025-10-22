#!/usr/bin/env python3
"""
Direct Keyboard Input Module for Raspberry Pi
This module provides keyboard input detection that works with a physical keyboard
plugged directly into the Raspberry Pi, without requiring SSH or terminal access.
"""
import threading
import time
import os
import struct
import select
import sys

class DirectKeyboardInput:
    def __init__(self, key='w', callback=None):
        """
        Initialize the direct keyboard input handler.
        
        Args:
            key: Key to trigger the action (default is 'w')
            callback: Function to call when key is pressed
        """
        self.key = key.lower()
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_press_time = 0
        self.debounce_time = 0.3  # 300ms debounce
        self.key_mapping = self._create_key_mapping()
        self.key_code = self.key_mapping.get(self.key)
        
        if self.key_code is None:
            print(f"Warning: No key code mapping found for '{self.key}'. Key detection may not work.")
    
    def _create_key_mapping(self):
        """Create a mapping of characters to Linux input event codes"""
        # This is a basic mapping of common keys to their event codes
        # These codes are standard for most keyboards on Linux
        return {
            'a': 30, 'b': 48, 'c': 46, 'd': 32, 'e': 18, 'f': 33, 'g': 34, 'h': 35, 'i': 23,
            'j': 36, 'k': 37, 'l': 38, 'm': 50, 'n': 49, 'o': 24, 'p': 25, 'q': 16, 'r': 19,
            's': 31, 't': 20, 'u': 22, 'v': 47, 'w': 17, 'x': 45, 'y': 21, 'z': 44,
            '0': 11, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10,
            'space': 57, 'return': 28, 'enter': 28, 'esc': 1, 'escape': 1,
            'backspace': 14, 'tab': 15, 'caps': 58, 'capslock': 58,
            'f1': 59, 'f2': 60, 'f3': 61, 'f4': 62, 'f5': 63,
            'f6': 64, 'f7': 65, 'f8': 66, 'f9': 67, 'f10': 68
        }
    
    def _find_keyboard_device(self):
        """Find a keyboard input device"""
        # Common locations for keyboard devices
        possible_devices = [
            "/dev/input/by-path/platform-3f980000.usb-usb-0:1.2:1.0-event-kbd",  # Common Pi keyboard path
            "/dev/input/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-event-kbd",  # Pi 4 path
            "/dev/input/by-id/usb-Generic_USB_Keyboard-event-kbd",  # Generic USB keyboard
        ]
        
        # Also try event devices
        for i in range(10):  # Check event0 through event9
            possible_devices.append(f"/dev/input/event{i}")
        
        # Try to open each device
        for device in possible_devices:
            try:
                if os.path.exists(device):
                    # Try to open the device for reading
                    fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
                    os.close(fd)  # Close it immediately, we just wanted to test
                    return device
            except (IOError, PermissionError) as e:
                continue
        
        return None
    
    def _monitor_keyboard(self):
        """
        Internal method to monitor keyboard in a separate thread.
        Uses direct access to input device files.
        """
        # Find a keyboard device
        keyboard_device = self._find_keyboard_device()
        
        if keyboard_device is None:
            print("Error: Could not find a keyboard device. Try running with sudo.")
            return
        
        print(f"Using keyboard device: {keyboard_device}")
        
        try:
            # Open the keyboard device
            with open(keyboard_device, "rb") as device:
                # Event format: long int, long int, unsigned short, unsigned short, unsigned int
                # See https://www.kernel.org/doc/html/v4.12/input/input.html
                event_size = struct.calcsize("llHHI")
                event_format = "llHHI"
                
                print(f"Monitoring for '{self.key}' key presses...")
                print(f"Key code to detect: {self.key_code}")
                
                while self.running:
                    # Use select to check if there's data to read
                    r, _, _ = select.select([device], [], [], 0.1)
                    if r:
                        event = device.read(event_size)
                        if event:
                            # Parse the event
                            (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(event_format, event)
                            
                            # EV_KEY event type is 1, value=1 means key press (0=release, 2=repeat)
                            if ev_type == 1 and value == 1:  # Key press event
                                print(f"Key pressed: code={code}, value={value}")
                                
                                # Check if it's our target key
                                if code == self.key_code:
                                    current_time = time.time()
                                    if current_time - self.last_press_time > self.debounce_time:
                                        print(f"Key '{self.key}' pressed! Triggering action...")
                                        self.last_press_time = current_time
                                        if self.callback:
                                            try:
                                                self.callback()
                                            except Exception as e:
                                                print(f"Error in key callback: {e}")
        except PermissionError:
            print("Permission denied accessing keyboard device.")
            print("Try running the script with sudo: sudo python3 direct_keyboard_input.py")
        except Exception as e:
            print(f"Error monitoring keyboard: {e}")
    
    def start(self):
        """
        Start monitoring for keyboard input in a separate thread.
        """
        if self.thread is not None and self.thread.is_alive():
            print("Keyboard monitoring is already running.")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_keyboard)
        self.thread.daemon = True
        self.thread.start()
        
        # Give the thread a moment to initialize
        time.sleep(0.5)
        
        print("\nDirect keyboard input is now active!")
        print(f"Press '{self.key}' on the physical keyboard connected to the Pi to trigger the action.")
        
        return self.thread
    
    def stop(self):
        """
        Stop monitoring for keyboard input.
        """
        if not self.running:
            return
            
        print("Stopping keyboard monitoring...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=2.0)
                if self.thread.is_alive():
                    print("Warning: Keyboard monitoring thread did not exit cleanly.")
                else:
                    print("Keyboard monitoring stopped successfully.")
            except Exception as e:
                print(f"Error stopping keyboard thread: {e}")

# Example usage
if __name__ == "__main__":
    def test_callback():
        print("\n*** KEY PRESSED! ACTION TRIGGERED! ***\n")
    
    print("Direct Keyboard Input Test")
    print("=========================")
    
    # Ask which key to monitor
    key = input("Enter the key to monitor (default is 'w'): ").strip() or 'w'
    
    # Create keyboard input handler
    keyboard = DirectKeyboardInput(key, test_callback)
    
    # Start monitoring
    keyboard.start()
    
    print("\nMonitoring started. Press the key on your physical keyboard.")
    print("Press Ctrl+C in this terminal to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        keyboard.stop()
