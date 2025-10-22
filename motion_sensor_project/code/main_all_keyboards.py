#!/usr/bin/env python3
"""
Main Program for Halloween Scare with Complete Keyboard Support
This version supports all types of keyboard input:
1. Physical keyboards plugged into the Pi
2. Pico Pi programmed as a keyboard
3. SSH terminal keyboard input
"""
from motion_sensor import ButtonTrigger
from output_control import OutputDevice
from audio_output import AudioOutput
import time
import sys
import os

# Import all keyboard input handlers
keyboard_handlers = []

# 1. Try Pico keyboard input
try:
    from pico_keyboard_input import PicoKeyboardInput
    PICO_KEYBOARD_AVAILABLE = True
except ImportError:
    PICO_KEYBOARD_AVAILABLE = False

# 2. Try direct keyboard input
try:
    from direct_keyboard_input import DirectKeyboardInput
    DIRECT_KEYBOARD_AVAILABLE = True
except ImportError:
    DIRECT_KEYBOARD_AVAILABLE = False

# 3. Try advanced keyboard trigger
try:
    from motion_sensor import KeyboardTrigger
    KEYBOARD_TRIGGER_AVAILABLE = True
except ImportError:
    KEYBOARD_TRIGGER_AVAILABLE = False

# 4. Try simple keyboard input
try:
    from keyboard_input import SimpleKeyboardInput
    SIMPLE_KEYBOARD_AVAILABLE = True
except ImportError:
    SIMPLE_KEYBOARD_AVAILABLE = False

# Configuration
BUTTON_PIN = 17      # Button pin (BCM numbering)
OUTPUT_PIN = 18      # LED/Relay pin (BCM numbering)
KEYBOARD_KEY = 'w'   # Keyboard key to trigger the scare

# Use audio files from the project directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio_files")  # Audio files in project directory

USE_PULLUP = True    # Set to True if using internal pull-up resistor

# Define the response to button press
def button_pressed():
    """Function called when button is pressed to trigger Halloween scare"""
    print("Button/Key pressed! Activating Halloween scare...")
    
    # Turn on output device (LED or relay) first
    output.turn_on()  # Turn on immediately
    print("Output device activated")
    
    try:
        # Check for custom audio files
        audio_files = audio.list_audio_files()
        if audio_files:
            # Play a random audio file if available
            import random
            import os
            import time
            
            # Filter for common audio formats
            valid_audio_files = [f for f in audio_files if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
            
            if valid_audio_files:
                random_file = random.choice(valid_audio_files)
                audio_path = os.path.join(audio.audio_dir, random_file)
                print(f"Playing Halloween audio: {random_file}")
                
                # Stop any currently playing audio first
                audio.stop_audio()
                
                # Play the audio file
                success = audio.play_audio_file(audio_path)
                
                if success:
                    # For WAV files, we'll use a blocking approach
                    if random_file.lower().endswith('.wav'):
                        # For WAV files, play_audio_file is already blocking, so we don't need to wait
                        # The function will return when playback is complete
                        print("WAV playback complete, continuing...")
                    # For MP3 files, we can estimate duration
                    elif random_file.lower().endswith('.mp3'):
                        try:
                            # Try to get duration info using a subprocess
                            import subprocess
                            result = subprocess.run(["mpg123", "--skip", "0", "--test", audio_path], 
                                                  capture_output=True, text=True, check=False)
                            
                            # Look for duration in output
                            import re
                            duration_match = re.search(r'(\d+):(\d+)\.(\d+)', result.stderr)
                            if duration_match:
                                mins, secs, _ = duration_match.groups()
                                duration = int(mins) * 60 + int(secs)
                                print(f"Audio duration: approximately {duration} seconds")
                                
                                # Wait for audio to finish (with a safety margin)
                                time.sleep(min(duration + 1, 30))  # Cap at 30 seconds max
                            else:
                                # Default wait time if we can't determine duration
                                time.sleep(10)  # Wait 10 seconds for audio to play
                        except Exception as e:
                            print(f"Error determining audio duration: {e}")
                            time.sleep(10)  # Default wait time
                    else:
                        # For other formats, wait a default time
                        time.sleep(10)  # Wait 10 seconds for audio to play
                else:
                    print("Failed to play audio file, falling back to default sounds")
                    # Fall back to default sounds
                    audio.play_alarm(1.0)
                    time.sleep(2)  # Wait for alarm to finish
            else:
                print("No valid audio files found, using default sounds")
                audio.play_alarm(1.0)
                time.sleep(2)  # Wait for alarm to finish
        else:
            # No audio files available, play default scary sounds
            print("No audio files found, playing default scary sounds")
            
            # Play a spooky alarm sound
            audio.play_alarm(1.0)
            time.sleep(2)  # Wait for alarm to finish
            
            # Play an eerie melody
            notes = [196, 147, 196, 220, 196, 147, 110]  # Spooky low notes
            durations = [0.3, 0.3, 0.3, 0.5, 0.3, 0.3, 0.8]
            audio.play_melody(notes, durations)
            time.sleep(3)  # Wait for melody to finish
    
    finally:
        # Always turn off the output device when done, regardless of errors
        print("Turning off output device")
        output.turn_off()
        
    print("Halloween scare complete")


# Initialize components
print("Initializing Halloween scare components...")
try:
    # Set up GPIO
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)  # Disable warnings
    
    # Initialize output device (GPIO or USB relay)
    from combined_output_control import CombinedOutputControl
    
    # You can specify the output type or let it auto-detect
    # output = CombinedOutputControl(output_type="gpio", pin_number=OUTPUT_PIN)  # Force GPIO
    # output = CombinedOutputControl(output_type="usb_relay")  # Force USB relay
    output = CombinedOutputControl(pin_number=OUTPUT_PIN)  # Auto-detect
    
    output_type = output.get_output_type()
    if output_type == "gpio":
        print(f"1. Output device initialized using GPIO on pin {OUTPUT_PIN}")
    else:
        print(f"1. Output device initialized using USB relay")
        
    # Initialize button trigger
    button = ButtonTrigger(BUTTON_PIN, callback=button_pressed, pull_up=USE_PULLUP)
    print(f"2. Button trigger initialized on pin {BUTTON_PIN}")
    
    # Initialize all available keyboard handlers
    active_keyboard_handlers = []
    
    # 1. Try Pico keyboard input (highest priority)
    pico_keyboard = None
    if PICO_KEYBOARD_AVAILABLE:
        pico_keyboard = PicoKeyboardInput(KEYBOARD_KEY, callback=button_pressed)
        keyboard_handlers.append(("Pico Keyboard", pico_keyboard))
        print(f"3a. Pico keyboard input initialized for key '{KEYBOARD_KEY}'")
    
    # 2. Try direct keyboard input (for physical keyboard)
    direct_keyboard = None
    if DIRECT_KEYBOARD_AVAILABLE:
        direct_keyboard = DirectKeyboardInput(KEYBOARD_KEY, callback=button_pressed)
        keyboard_handlers.append(("Direct Keyboard", direct_keyboard))
        print(f"3b. Direct keyboard input initialized for key '{KEYBOARD_KEY}'")
    
    # 3. Try advanced keyboard trigger (for SSH terminal)
    advanced_keyboard = None
    if KEYBOARD_TRIGGER_AVAILABLE:
        advanced_keyboard = KeyboardTrigger(KEYBOARD_KEY, callback=button_pressed)
        keyboard_handlers.append(("Advanced Keyboard", advanced_keyboard))
        print(f"3c. Advanced keyboard trigger initialized for key '{KEYBOARD_KEY}'")
    
    # 4. Try simple keyboard input (fallback)
    simple_keyboard = None
    if SIMPLE_KEYBOARD_AVAILABLE:
        simple_keyboard = SimpleKeyboardInput(KEYBOARD_KEY, callback=button_pressed)
        keyboard_handlers.append(("Simple Keyboard", simple_keyboard))
        print(f"3d. Simple keyboard input initialized as fallback")
    
    # Initialize audio output
    from audio_output import AudioOutput
    audio = AudioOutput(AUDIO_DIR)
    print(f"4. Audio output initialized with directory: {AUDIO_DIR}")
    
    print("All Halloween scare components initialized successfully")
except Exception as e:
    print(f"Error initializing components: {e}")
    sys.exit(1)

# Test components on startup
print("\nTesting components:")
print("1. Testing output device...")
output.blink(2, 0.2, 0.2)

print("2. Testing audio output...")
audio.play_tone(440, 0.5)  # Play A4 note

# Setup button detection
print("\nSetting up button trigger...")
interrupt_success = button.setup_interrupt()
if not interrupt_success:
    print("Note: Using polling mode instead of interrupts. This will still work fine.")
    print("The button will be checked continuously in the background.")

# Setup all keyboard handlers
print("\nSetting up keyboard handlers...")

# Start Pico keyboard input (highest priority)
if pico_keyboard:
    print("Starting Pico keyboard input...")
    pico_keyboard.start()
    active_keyboard_handlers.append(("Pico Keyboard", pico_keyboard))
    print(f"Pico keyboard input started for key '{KEYBOARD_KEY}'")

# Start direct keyboard input (for physical keyboard)
if direct_keyboard:
    print("Starting direct keyboard input for physical keyboard...")
    direct_keyboard.start()
    active_keyboard_handlers.append(("Direct Keyboard", direct_keyboard))
    print(f"Direct keyboard input started for key '{KEYBOARD_KEY}'")

# Start advanced keyboard trigger (for SSH terminal)
if advanced_keyboard:
    print("Starting advanced keyboard trigger for SSH terminal...")
    keyboard_success = advanced_keyboard.start_monitoring()
    if keyboard_success:
        active_keyboard_handlers.append(("Advanced Keyboard", advanced_keyboard))
        print(f"Advanced keyboard monitoring started for key '{KEYBOARD_KEY}'")

# If advanced keyboard monitoring fails, try the simple method
if advanced_keyboard and not keyboard_success and simple_keyboard:
    print("Advanced keyboard monitoring failed. Falling back to simple keyboard input...")
    simple_keyboard.start()
    active_keyboard_handlers.append(("Simple Keyboard", simple_keyboard))
    print(f"Simple keyboard input started for key '{KEYBOARD_KEY}'")

if not active_keyboard_handlers:
    print("Warning: No keyboard input methods were successfully started.")
    print("The system will only respond to button presses.")
else:
    print(f"Successfully started {len(active_keyboard_handlers)} keyboard input methods:")
    for name, _ in active_keyboard_handlers:
        print(f"- {name}")

# Initialize GUI if enabled
USE_GUI = True  # Set to False to disable GUI
GUI_DISPLAY_AVAILABLE = False  # Will be set to True if display is available

if USE_GUI:
    try:
        print("\nInitializing GUI interface...")
        import gui_callback
        import gui_interface
        import threading
        import os
        
        # Check if we're running in a desktop environment
        if 'DISPLAY' not in os.environ and os.path.exists('/dev/fb0'):
            # If framebuffer is available but no DISPLAY, try to set it
            print("Framebuffer detected but no DISPLAY set. Trying to set DISPLAY=:0")
            os.environ['DISPLAY'] = ':0'
        
        # Register the button_pressed callback with the GUI
        gui_callback.register_callback(button_pressed)
        
        # Check if display is available before starting GUI thread
        if gui_interface.is_display_available():
            # Start the GUI in a separate thread
            def start_gui():
                success = gui_interface.run_gui(gui_callback.button_callback)
                if not success:
                    print("Failed to start GUI. Continuing with physical button only.")
                    
            gui_thread = threading.Thread(target=start_gui, daemon=True)
            gui_thread.start()
            print("GUI interface thread started")
            GUI_DISPLAY_AVAILABLE = True
        else:
            print("No display available for GUI. Continuing with physical button only.")
            print("To use the GUI, make sure you're running in a desktop environment.")
            print("If using SSH, try: ssh -X admin@yumpi")
    except Exception as e:
        print(f"Error initializing GUI: {e}")
        print("Continuing without GUI")
        USE_GUI = False

# Main loop
print("\nHalloween scare system ready!")
print(f"Press the button or the '{KEYBOARD_KEY}' key to trigger...")
print("The system will respond to:")
print("1. Physical button press on GPIO pin")
print("2. Pico Pi programmed as a keyboard")
print("3. Physical keyboard 'w' key press")
print("4. SSH terminal keyboard input")
print("5. GUI button click (if GUI is enabled)")

try:
    # Blink LED to indicate system is ready
    output.blink(3, 0.1, 0.1)
    
    print("Press Ctrl+C to exit")
    while True:
        # Main program can do other things here if needed
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nProgram terminated by user")
    
finally:
    # Clean up
    try:
        print("\nCleaning up resources...")
        output.turn_off()
        output.cleanup()  # This will handle both GPIO and USB relay cleanup
        audio.stop_audio()
        
        # Clean up all keyboard handlers
        for name, handler in active_keyboard_handlers:
            try:
                if hasattr(handler, 'stop_monitoring'):
                    handler.stop_monitoring()
                elif hasattr(handler, 'stop'):
                    handler.stop()
                
                if hasattr(handler, 'cleanup'):
                    handler.cleanup()
                    
                print(f"{name} stopped and cleaned up")
            except Exception as e:
                print(f"Error cleaning up {name}: {e}")
        
        # Additional GPIO cleanup just to be safe
        try:
            GPIO.cleanup()  # Clean up any remaining GPIO resources
        except:
            pass  # Ignore errors if GPIO was already cleaned up
            
        print("Halloween scare system shutdown complete - all resources cleaned up")
    except Exception as e:
        print(f"Error during cleanup: {e}")
