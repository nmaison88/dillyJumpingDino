"""
Button Input Module for Raspberry Pi 5
This module handles button press detection for triggering Halloween scares.
"""
import RPi.GPIO as GPIO
import time

class ButtonTrigger:
    def __init__(self, pin_number=17, callback=None, pull_up=True):
        """
        Initialize the button trigger.
        
        Args:
            pin_number: GPIO pin number connected to the button (BCM numbering)
            callback: Function to call when button is pressed
            pull_up: Whether to use internal pull-up resistor (True) or external pull-down (False)
        """
        # Use BCM pin numbering
        GPIO.setmode(GPIO.BCM)
        
        self.pin_number = pin_number
        self.callback = callback
        self.last_press_time = 0
        self.debounce_time = 0.3  # 300ms debounce to avoid button bounce
        self.pull_up = pull_up
        
        # Set up the GPIO pin as input with pull-up or pull-down
        if pull_up:
            # When using pull-up, button should connect pin to ground when pressed
            # Button press will read as LOW (0)
            GPIO.setup(self.pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            # When using pull-down, button should connect pin to 3.3V when pressed
            # Button press will read as HIGH (1)
            GPIO.setup(self.pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def is_button_pressed(self):
        """
        Check if button is currently pressed.
        Returns True if button is pressed, False otherwise.
        """
        if self.pull_up:
            # When using pull-up, button press reads as LOW (0)
            return GPIO.input(self.pin_number) == 0
        else:
            # When using pull-down, button press reads as HIGH (1)
            return GPIO.input(self.pin_number) == 1
    
    def monitor(self, polling_interval=0.05):
        """
        Continuously monitor for button presses.
        
        Args:
            polling_interval: Time in seconds between checks
        """
        try:
            print("Monitoring for button presses...")
            while True:
                if self.is_button_pressed():
                    current_time = time.time()
                    if current_time - self.last_press_time > self.debounce_time:
                        print("Button pressed! Triggering scare...")
                        self.last_press_time = current_time
                        if self.callback:
                            self.callback()
                    # Wait until button is released to avoid multiple triggers
                    while self.is_button_pressed():
                        time.sleep(0.01)
                time.sleep(polling_interval)
        except KeyboardInterrupt:
            print("Button monitoring stopped.")
        finally:
            self.cleanup()
    
    def setup_interrupt(self):
        """
        Set up an interrupt to detect button presses.
        This is more efficient than polling.
        If interrupt setup fails, falls back to polling mode.
        """
        def handle_interrupt(channel):
            current_time = time.time()
            if current_time - self.last_press_time > self.debounce_time:
                self.last_press_time = current_time
                print("Button pressed! Triggering scare... (Interrupt)")
                if self.callback:
                    self.callback()
        
        try:
            # Remove any existing event detection on this pin
            try:
                GPIO.remove_event_detect(self.pin_number)
            except:
                pass  # It's okay if there was no event detection to remove
            
            # Set up event detection based on pull-up/down configuration
            if self.pull_up:
                # When using pull-up, detect falling edge (button press pulls to ground)
                GPIO.add_event_detect(self.pin_number, GPIO.FALLING, callback=handle_interrupt, bouncetime=int(self.debounce_time * 1000))
            else:
                # When using pull-down, detect rising edge (button press pulls to 3.3V)
                GPIO.add_event_detect(self.pin_number, GPIO.RISING, callback=handle_interrupt, bouncetime=int(self.debounce_time * 1000))
                
            print(f"Button interrupt set up on pin {self.pin_number}")
            return True
            
        except RuntimeError as e:
            print(f"Warning: Could not set up interrupt: {e}")
            print("Falling back to polling mode for button detection.")
            
            # Start polling in a separate thread
            import threading
            self.polling_thread = threading.Thread(target=self._polling_loop)
            self.polling_thread.daemon = True  # Thread will exit when main program exits
            self.polling_thread.start()
            return False
    
    def _polling_loop(self):
        """
        Internal polling loop used as fallback if interrupts fail.
        """
        print("Starting button polling loop...")
        try:
            while True:
                if self.is_button_pressed():
                    current_time = time.time()
                    if current_time - self.last_press_time > self.debounce_time:
                        print("Button pressed! Triggering scare... (Polling)")
                        self.last_press_time = current_time
                        if self.callback:
                            self.callback()
                    # Wait until button is released to avoid multiple triggers
                    while self.is_button_pressed():
                        time.sleep(0.01)
                time.sleep(0.05)  # Check every 50ms
        except Exception as e:
            print(f"Polling loop error: {e}")
            # Continue running even if there's an error


# Example usage
if __name__ == "__main__":
    def on_button_press():
        print("Halloween scare triggered!")
    
    try:
        # Create a button trigger on pin 17 (BCM numbering) with pull-up resistor
        button = ButtonTrigger(17, callback=on_button_press, pull_up=True)
        
        # Method 1: Use polling
        # button.monitor()
        
        # Method 2: Use interrupts (more efficient)
        button.setup_interrupt()
        
        # Keep the program running
        print("Waiting for button press to trigger Halloween scare...")
        print("Press Ctrl+C to exit")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Program terminated by user")
        
    finally:
        # Clean up GPIO
        GPIO.cleanup()
        print("GPIO cleanup complete")
