"""
Input Module for Raspberry Pi 5
This module handles button press and keyboard input detection for triggering Halloween scares.
"""
import RPi.GPIO as GPIO
import time
import threading
import sys
import termios
import tty
import select

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
        # Import all necessary modules locally to avoid any conflicts
        import sys
        import time as polling_time
        import traceback
        
        print("Starting button polling loop with isolated imports...")
        
        # Function to safely sleep without crashing if time module fails
        def safe_sleep(seconds):
            try:
                polling_time.sleep(seconds)
            except Exception as sleep_error:
                # If sleep fails, use a simple CPU-bound delay as fallback
                print(f"Sleep error: {sleep_error}, using fallback delay")
                start = polling_time.time() if 'polling_time' in locals() else 0
                while (polling_time.time() if 'polling_time' in locals() else 1) - start < seconds:
                    pass  # Simple busy-wait as fallback
        
        # Main polling loop with multiple layers of error handling
        while True:  # Outermost loop - never exit
            try:
                while True:  # Main work loop
                    try:
                        # Check if button is pressed
                        if self.is_button_pressed():
                            try:
                                # Get current time safely
                                try:
                                    current_time = polling_time.time()
                                except Exception as time_error:
                                    print(f"Time error: {time_error}, using fallback")
                                    current_time = 0  # Fallback value
                                    
                                # Check debounce
                                if current_time - self.last_press_time > self.debounce_time:
                                    print("Button pressed! Triggering scare... (Polling)")
                                    self.last_press_time = current_time
                                    
                                    # Call the callback if available
                                    if self.callback:
                                        try:
                                            self.callback()
                                        except Exception as callback_error:
                                            print(f"Callback error: {callback_error}")
                                            traceback.print_exc()
                            except Exception as press_error:
                                print(f"Button press handling error: {press_error}")
                            
                            # Wait until button is released
                            try:
                                while self.is_button_pressed():
                                    safe_sleep(0.01)
                            except Exception as release_error:
                                print(f"Button release error: {release_error}")
                                safe_sleep(0.1)  # Sleep a bit anyway
                    except Exception as inner_error:
                        print(f"Inner loop error: {inner_error}")
                    
                    # Sleep between checks
                    safe_sleep(0.05)
            except Exception as outer_error:
                print(f"Outer loop error: {outer_error}")
                print("Full traceback:")
                traceback.print_exc()
                safe_sleep(1)  # Avoid tight loop on persistent errors
    
    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        try:
            # Remove event detection if it exists
            try:
                GPIO.remove_event_detect(self.pin_number)
            except:
                pass  # It's okay if there was no event detection to remove
            
            print("Button resources cleaned up")
        except Exception as e:
            print(f"Error during button cleanup: {e}")


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


# Example usage
if __name__ == "__main__":
    def on_input_trigger():
        print("Halloween scare triggered!")
    
    try:
        # Create a button trigger on pin 17 (BCM numbering) with pull-up resistor
        button = ButtonTrigger(17, callback=on_input_trigger, pull_up=True)
        
        # Method 1: Use polling
        # button.monitor()
        
        # Method 2: Use interrupts (more efficient)
        button.setup_interrupt()
        
        # Create a keyboard trigger for the 'w' key
        keyboard = KeyboardTrigger('w', callback=on_input_trigger)
        keyboard.start_monitoring()
        
        # Keep the program running
        print("Waiting for button press or 'w' key to trigger Halloween scare...")
        print("Press Ctrl+C to exit")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Program terminated by user")
        
    finally:
        # Clean up resources
        GPIO.cleanup()
        print("GPIO cleanup complete")
