#!/usr/bin/env python3
"""
Pico Keyboard Input Module for Raspberry Pi
This module is specifically designed to detect keyboard input from a Pico Pi
programmed to act as a keyboard device.
"""
import threading
import time
import os
import struct
import select
import sys
import glob

class PicoKeyboardInput:
    def __init__(self, key='w', callback=None):
        """
        Initialize the Pico keyboard input handler.
        
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
        self.device_paths = []
        
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
    
    def _find_input_devices(self):
        """Find all possible input devices"""
        # This will find ALL input devices, not just keyboards
        devices = []
        
        # Check by-path devices (often used for USB devices)
        by_path_devices = glob.glob("/dev/input/by-path/*-kbd")
        for device in by_path_devices:
            devices.append(device)
        
        # Check by-id devices (more stable names for USB devices)
        by_id_devices = glob.glob("/dev/input/by-id/*-kbd")
        for device in by_id_devices:
            devices.append(device)
            
        # Also check all event devices
        event_devices = glob.glob("/dev/input/event*")
        for device in event_devices:
            devices.append(device)
        
        # Add some common Pico device paths
        pico_devices = [
            "/dev/input/by-id/usb-Raspberry_Pi_Pico_*",
            "/dev/input/by-id/usb-Arduino_LLC_*",  # Some Pico boards identify as Arduino
            "/dev/hidraw*"  # HID raw devices
        ]
        
        for pattern in pico_devices:
            matching_devices = glob.glob(pattern)
            for device in matching_devices:
                if device not in devices:
                    devices.append(device)
        
        return devices
    
    def _monitor_all_devices(self):
        """
        Monitor all input devices simultaneously for key presses.
        This approach is more robust as it doesn't require knowing exactly which device is the Pico.
        """
        # Find all possible input devices
        self.device_paths = self._find_input_devices()
        
        if not self.device_paths:
            print("Error: No input devices found. Try running with sudo.")
            return
        
        print(f"Found {len(self.device_paths)} input devices to monitor")
        for i, device in enumerate(self.device_paths):
            print(f"  {i+1}. {device}")
        
        # Open all devices
        open_devices = []
        for device_path in self.device_paths:
            try:
                device = open(device_path, "rb")
                open_devices.append((device_path, device))
                print(f"Successfully opened device: {device_path}")
            except (IOError, PermissionError) as e:
                print(f"Could not open {device_path}: {e}")
        
        if not open_devices:
            print("Error: Could not open any input devices. Try running with sudo.")
            return
        
        print(f"Monitoring {len(open_devices)} devices for '{self.key}' key presses...")
        print(f"Key code to detect: {self.key_code}")
        
        # Event format: long int, long int, unsigned short, unsigned short, unsigned int
        event_size = struct.calcsize("llHHI")
        event_format = "llHHI"
        
        try:
            while self.running:
                # Create a list of file descriptors to monitor
                read_list = [device for _, device in open_devices]
                
                # Use select to wait for input on any device
                r, _, _ = select.select(read_list, [], [], 0.1)
                
                for device in r:
                    # Find which device this is
                    device_info = next((info for info in open_devices if info[1] == device), None)
                    if device_info:
                        device_path, _ = device_info
                    else:
                        device_path = "Unknown device"
                    
                    try:
                        event = device.read(event_size)
                        if event:
                            # Parse the event
                            (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(event_format, event)
                            
                            # EV_KEY event type is 1, value=1 means key press (0=release, 2=repeat)
                            if ev_type == 1 and value == 1:  # Key press event
                                print(f"Key pressed on {device_path}: code={code}, value={value}")
                                
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
                    except Exception as e:
                        print(f"Error reading from {device_path}: {e}")
        except Exception as e:
            print(f"Error in device monitoring: {e}")
        finally:
            # Close all devices
            for _, device in open_devices:
                try:
                    device.close()
                except:
                    pass
    
    def _monitor_raw_input(self):
        """
        Alternative method to monitor for raw HID input.
        This might work better for some Pico devices that don't register as standard keyboards.
        """
        # Find all hidraw devices
        hidraw_devices = glob.glob("/dev/hidraw*")
        
        if not hidraw_devices:
            print("No HID raw devices found.")
            return
        
        print(f"Found {len(hidraw_devices)} HID raw devices to monitor")
        for i, device in enumerate(hidraw_devices):
            print(f"  {i+1}. {device}")
        
        # Open all hidraw devices
        open_devices = []
        for device_path in hidraw_devices:
            try:
                device = open(device_path, "rb")
                open_devices.append((device_path, device))
                print(f"Successfully opened HID device: {device_path}")
            except (IOError, PermissionError) as e:
                print(f"Could not open {device_path}: {e}")
        
        if not open_devices:
            print("Error: Could not open any HID devices. Try running with sudo.")
            return
        
        print(f"Monitoring {len(open_devices)} HID devices for input...")
        
        try:
            while self.running:
                # Create a list of file descriptors to monitor
                read_list = [device for _, device in open_devices]
                
                # Use select to wait for input on any device
                r, _, _ = select.select(read_list, [], [], 0.1)
                
                for device in r:
                    # Find which device this is
                    device_info = next((info for info in open_devices if info[1] == device), None)
                    if device_info:
                        device_path, _ = device_info
                    else:
                        device_path = "Unknown device"
                    
                    try:
                        # Read raw data (8 bytes is common for keyboard HID reports)
                        data = device.read(8)
                        if data:
                            # Print the raw data for debugging
                            hex_data = ' '.join(f'{b:02x}' for b in data)
                            print(f"Raw data from {device_path}: {hex_data}")
                            
                            # For many keyboards, the third byte (index 2) contains the key code
                            # This is a simplification and may need adjustment for your specific Pico
                            if len(data) > 2:
                                key_code = data[2]
                                print(f"Possible key code: {key_code}")
                                
                                # Check if it's our target key
                                # For 'w', the HID usage code is often 26 (0x1A)
                                # But we'll check both the standard Linux input code (17) and the HID usage code (26)
                                if key_code == 17 or key_code == 26:
                                    current_time = time.time()
                                    if current_time - self.last_press_time > self.debounce_time:
                                        print(f"Detected possible 'w' key press! Triggering action...")
                                        self.last_press_time = current_time
                                        if self.callback:
                                            try:
                                                self.callback()
                                            except Exception as e:
                                                print(f"Error in key callback: {e}")
                    except Exception as e:
                        print(f"Error reading from {device_path}: {e}")
        except Exception as e:
            print(f"Error in HID monitoring: {e}")
        finally:
            # Close all devices
            for _, device in open_devices:
                try:
                    device.close()
                except:
                    pass
    
    def start(self, method="all"):
        """
        Start monitoring for keyboard input in a separate thread.
        
        Args:
            method: The method to use for keyboard monitoring.
                   "all" monitors all input devices.
                   "raw" monitors raw HID devices.
        """
        if self.thread is not None and self.thread.is_alive():
            print("Keyboard monitoring is already running.")
            return
        
        self.running = True
        
        if method == "raw":
            self.thread = threading.Thread(target=self._monitor_raw_input)
        else:
            self.thread = threading.Thread(target=self._monitor_all_devices)
            
        self.thread.daemon = True
        self.thread.start()
        
        # Give the thread a moment to initialize
        time.sleep(0.5)
        
        print("\nPico keyboard input monitoring is now active!")
        print(f"Press '{self.key}' on any connected keyboard or trigger the Pico to send '{self.key}'")
        
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
    
    print("Pico Keyboard Input Test")
    print("=======================")
    
    # Ask which key to monitor
    key = input("Enter the key to monitor (default is 'w'): ").strip() or 'w'
    
    # Create keyboard input handler
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
    keyboard.start(method=method)
    
    print("\nMonitoring started. Trigger your Pico to send the key.")
    print("Press Ctrl+C in this terminal to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        keyboard.stop()
