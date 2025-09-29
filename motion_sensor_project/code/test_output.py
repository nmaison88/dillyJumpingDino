#!/usr/bin/env python3
"""
Test script for the combined output controller
Tests both GPIO and USB relay outputs
"""
import time
import argparse
import sys

def test_output(output_type=None, pin=18, usb_port=None):
    """
    Test the output controller
    
    Args:
        output_type: Type of output to test ("gpio" or "usb_relay")
        pin: GPIO pin number if using GPIO
        usb_port: USB port if using USB relay
    """
    try:
        from combined_output_control import CombinedOutputControl
        
        print("\n=== Testing Output Controller ===")
        
        # Create the output controller
        if output_type:
            print(f"Using specified output type: {output_type}")
            output = CombinedOutputControl(output_type=output_type, pin_number=pin, usb_port=usb_port)
        else:
            print("Auto-detecting output type...")
            output = CombinedOutputControl(pin_number=pin, usb_port=usb_port)
        
        # Check which output type was detected
        detected_type = output.get_output_type()
        print(f"Detected output type: {detected_type}")
        
        # Run tests
        print("\nRunning output tests:")
        
        print("\n1. Turn ON")
        output.turn_on()
        time.sleep(2)
        
        print("\n2. Turn OFF")
        output.turn_off()
        time.sleep(1)
        
        print("\n3. Pulse (2 seconds)")
        output.pulse(2.0)
        time.sleep(1)
        
        print("\n4. Blink (3 times)")
        output.blink(3, 0.5, 0.5)
        
        print("\nTests completed successfully!")
        output.cleanup()
        return True
        
    except Exception as e:
        print(f"Error during output test: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the output controller")
    parser.add_argument("--gpio", action="store_true", help="Test GPIO output")
    parser.add_argument("--usb", action="store_true", help="Test USB relay output")
    parser.add_argument("--pin", type=int, default=18, help="GPIO pin number (default: 18)")
    parser.add_argument("--port", type=str, help="USB port for relay (e.g., /dev/ttyUSB0)")
    
    args = parser.parse_args()
    
    # Determine output type based on arguments
    output_type = None
    if args.gpio:
        output_type = "gpio"
    elif args.usb:
        output_type = "usb_relay"
    
    # Run the test
    success = test_output(output_type, args.pin, args.port)
    
    # Exit with appropriate status
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
