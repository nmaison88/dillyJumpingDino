#!/usr/bin/env python3
"""
Combined Output Control Module
Provides a unified interface for controlling outputs via GPIO or USB relay
"""
import os
import time
import logging
import sys  # Add sys import for error handling
from output_control import OutputDevice  # Fix: Use OutputDevice instead of OutputControl
from usb_relay_control import USBRelay

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CombinedOutputControl:
    """
    Combined output controller that can use either GPIO or USB relay.
    Provides a unified interface regardless of the underlying hardware.
    """
    
    # Output types
    GPIO = "gpio"
    USB_RELAY = "usb_relay"
    
    def __init__(self, output_type=None, pin_number=18, active_high=True, usb_port=None):
        """
        Initialize the combined output controller.
        
        Args:
            output_type: Type of output to use ("gpio" or "usb_relay"). 
                        If None, will auto-detect.
            pin_number: GPIO pin number if using GPIO output
            active_high: True if GPIO device is active when pin is high
            usb_port: Serial port for USB relay if using USB relay
        """
        self.output_type = output_type
        self.gpio_controller = None
        self.usb_controller = None
        self.is_on = False
        
        # Auto-detect output type if not specified
        if self.output_type is None:
            self.output_type = self._auto_detect_output_type()
        
        # Initialize the appropriate controller
        if self.output_type == self.GPIO:
            try:
                self.gpio_controller = OutputDevice(pin_number, active_high)
                logger.info(f"Using GPIO output on pin {pin_number}")
            except Exception as e:
                logger.error(f"Failed to initialize GPIO output: {e}")
                # Fall back to USB relay if GPIO fails
                self.output_type = self.USB_RELAY
        
        if self.output_type == self.USB_RELAY:
            self.usb_controller = USBRelay(port=usb_port)
            if self.usb_controller.is_connected():
                logger.info("Using USB relay output")
            else:
                logger.warning("USB relay not connected")
                # Fall back to GPIO if USB fails and GPIO wasn't already tried
                if self.gpio_controller is None:
                    try:
                        self.gpio_controller = OutputControl(pin_number, active_high)
                        self.output_type = self.GPIO
                        logger.info(f"Falling back to GPIO output on pin {pin_number}")
                    except Exception as e:
                        logger.error(f"Failed to initialize GPIO fallback: {e}")
    
    def _auto_detect_output_type(self):
        """
        Auto-detect which output type to use.
        First tries USB relay, then falls back to GPIO.
        """
        # Try to detect USB relay first
        temp_usb = USBRelay()
        if temp_usb.is_connected():
            temp_usb.cleanup()
            return self.USB_RELAY
        
        # Fall back to GPIO
        return self.GPIO
    
    def turn_on(self):
        """Turn on the output device"""
        if self.output_type == self.GPIO and self.gpio_controller:
            self.gpio_controller.turn_on()
            self.is_on = True
            return True
        elif self.output_type == self.USB_RELAY and self.usb_controller:
            success = self.usb_controller.turn_on()
            self.is_on = success
            return success
        else:
            logger.error("No output controller available")
            return False
    
    def turn_off(self):
        """Turn off the output device"""
        if self.output_type == self.GPIO and self.gpio_controller:
            self.gpio_controller.turn_off()
            self.is_on = False
            return True
        elif self.output_type == self.USB_RELAY and self.usb_controller:
            success = self.usb_controller.turn_off()
            self.is_on = not success  # Only set to False if turn_off was successful
            return success
        else:
            logger.error("No output controller available")
            return False
    
    def pulse(self, duration=1.0):
        """
        Turn on the output for a specified duration, then turn it off.
        
        Args:
            duration: Time in seconds to keep the output on
        """
        if self.output_type == self.GPIO and self.gpio_controller:
            self.gpio_controller.pulse(duration)
            return True
        elif self.output_type == self.USB_RELAY and self.usb_controller:
            return self.usb_controller.pulse(duration)
        else:
            logger.error("No output controller available")
            return False
    
    def blink(self, count=3, on_time=0.5, off_time=0.5):
        """
        Blink the output a specified number of times.
        
        Args:
            count: Number of blinks
            on_time: Time in seconds to keep the output on during each blink
            off_time: Time in seconds to keep the output off between blinks
        """
        if self.output_type == self.GPIO and self.gpio_controller:
            self.gpio_controller.blink(count, on_time, off_time)
            return True
        elif self.output_type == self.USB_RELAY and self.usb_controller:
            return self.usb_controller.blink(count, on_time, off_time)
        else:
            logger.error("No output controller available")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.output_type == self.GPIO and self.gpio_controller:
            self.gpio_controller.cleanup()
        elif self.output_type == self.USB_RELAY and self.usb_controller:
            self.usb_controller.cleanup()

    def get_output_type(self):
        """Get the current output type being used"""
        return self.output_type


# Test function
def test_combined_output():
    """Test the combined output controller"""
    print("Testing Combined Output Controller")
    
    # Test with auto-detection
    output = CombinedOutputControl()
    print(f"Using output type: {output.get_output_type()}")
    
    print("Turning ON")
    output.turn_on()
    time.sleep(2)
    
    print("Turning OFF")
    output.turn_off()
    time.sleep(1)
    
    print("Pulsing")
    output.pulse(1.0)
    time.sleep(1)
    
    print("Blinking")
    output.blink(3, 0.3, 0.3)
    
    print("Test complete")
    output.cleanup()

if __name__ == "__main__":
    test_combined_output()
