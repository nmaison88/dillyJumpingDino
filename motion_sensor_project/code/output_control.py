"""
Output Control Module for Raspberry Pi 5
This module handles controlling output devices like LEDs or relays.
"""
import RPi.GPIO as GPIO
import time

class OutputDevice:
    def __init__(self, pin_number=18, active_high=True):
        """
        Initialize the output device.
        
        Args:
            pin_number: GPIO pin number connected to the output device (BCM numbering)
            active_high: True if the device is active when the pin is high,
                         False if active when the pin is low
        """
        # Use BCM pin numbering
        GPIO.setmode(GPIO.BCM)
        
        self.pin_number = pin_number
        self.active_high = active_high
        self.is_on = False
        
        # Set up the GPIO pin as output
        GPIO.setup(self.pin_number, GPIO.OUT)
        
        self.turn_off()  # Ensure the device starts in the off state
    
    def turn_on(self):
        """Turn on the output device."""
        GPIO.output(self.pin_number, GPIO.HIGH if self.active_high else GPIO.LOW)
        self.is_on = True
        print(f"Output device on pin {self.pin_number} turned ON")
    
    def turn_off(self):
        """Turn off the output device."""
        GPIO.output(self.pin_number, GPIO.LOW if self.active_high else GPIO.HIGH)
        self.is_on = False
        print(f"Output device on pin {self.pin_number} turned OFF")
    
    def toggle(self):
        """Toggle the output device state."""
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()
    
    def blink(self, times=3, on_time=0.2, off_time=0.2):
        """
        Blink the output device.
        
        Args:
            times: Number of blinks
            on_time: Time in seconds to stay on
            off_time: Time in seconds to stay off
        """
        original_state = self.is_on
        
        for _ in range(times):
            self.turn_on()
            time.sleep(on_time)
            self.turn_off()
            time.sleep(off_time)
        
        # Restore original state if it was on
        if original_state:
            self.turn_on()
    
    def pulse(self, duration=1.0):
        """
        Turn on the output device for a specified duration.
        
        Args:
            duration: Time in seconds to keep the device on
        """
        self.turn_on()
        time.sleep(duration)
        self.turn_off()


    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup(self.pin_number)
        print(f"Output device resources on pin {self.pin_number} cleaned up")


# Example usage
if __name__ == "__main__":
    try:
        # Create an LED on pin 18 (BCM numbering)
        led = OutputDevice(18)
        
        # Test different functions
        print("Testing LED blink...")
        led.blink(5)
        
        print("Testing LED pulse...")
        led.pulse(2)
        
        print("Testing LED toggle...")
        led.toggle()  # Turn on
        time.sleep(1)
        led.toggle()  # Turn off
        
    except KeyboardInterrupt:
        print("Program terminated by user")
        
    finally:
        # Clean up GPIO
        GPIO.cleanup()
        print("GPIO cleanup complete")
