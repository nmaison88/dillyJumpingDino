#!/usr/bin/env python3
"""
Test script for KeyboardTrigger class
"""
from motion_sensor import KeyboardTrigger
import time

def test_callback():
    print('Key pressed! Callback triggered!')

def main():
    # Create a keyboard trigger for the 'w' key
    kt = KeyboardTrigger('w', test_callback)
    
    # Start monitoring for key presses
    kt.start_monitoring()
    
    print('Press the "w" key to trigger the callback or Ctrl+C to exit')
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        kt.stop_monitoring()
        kt.cleanup()

if __name__ == "__main__":
    main()
