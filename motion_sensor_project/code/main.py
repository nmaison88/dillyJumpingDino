"""
Main Program for Button-Activated Halloween Scare with Raspberry Pi 5
This program integrates button detection, keyboard input, output control, and audio output for Halloween scares.
"""
from motion_sensor import ButtonTrigger, KeyboardTrigger
from output_control import OutputDevice
from audio_output import AudioOutput
import time
import sys

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

# 3. Try simple keyboard input
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
import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio_files")  # Audio files in project directory

# Global flags to track system state
SCARE_IN_PROGRESS = False
# We're using a simplified approach now with no audio state tracking

# Idle sounds configuration
IDLE_SOUNDS_DIR = os.path.join(PROJECT_DIR, "idle_sounds")  # Directory for idle sounds
STANDBY_TIMEOUT = 120  # Time in seconds (4 minutes) before playing idle sound
IDLE_REPEAT_INTERVAL = 120  # Time in seconds before playing another idle sound
LAST_ACTIVITY_TIME = time.time()  # Track when the last activity occurred
LAST_IDLE_SOUND_TIME = 0  # Track when the last idle sound was played
IDLE_SOUND_PLAYED = False  # Track if idle sound has been played
LAST_IDLE_SOUND = ""  # Track the last idle sound played to avoid repetition

# Output toggle configuration
MIN_TOGGLE_DURATION = 0.1  # Minimum duration for output to stay on/off (in seconds)
MAX_TOGGLE_DURATION = 0.3  # Maximum duration for output to stay on/off (in seconds)
# No longer using probability - we'll toggle every time for more consistent behavior

# Simple function to toggle output for a fixed number of times
def _toggle_output_fixed_count(count, duration=0.2):
    """Toggle the output on and off a fixed number of times
    
    Args:
        count: Number of toggles to perform
        duration: Duration in seconds for each toggle state (on or off)
    """
    import time
    
    print(f"\n[TOGGLE] Starting output toggling for {count} toggles (duration: {duration:.1f}s)")
    
    # Always start with output on
    output.turn_on()
    print("\n[TOGGLE] Output ON")
    time.sleep(duration)
    
    # Do a fixed number of toggles
    for i in range(count):
        # Toggle off
        output.turn_off()
        print(f"\n[TOGGLE] Toggle {i+1}/{count}: Output OFF")
        time.sleep(duration)
        
        # Toggle on
        output.turn_on()
        print(f"\n[TOGGLE] Toggle {i+1}/{count}: Output ON")
        time.sleep(duration)
    
    # Always end with output off
    output.turn_off()
    print("\n[TOGGLE] Output OFF at end")
    
    print(f"\n[TOGGLE] Completed {count} toggles")

# Function to do a simple scare sequence with audio
def do_simple_scare_with_audio(audio_path=None):
    """Perform a simple scare sequence with toggling and audio"""
    import threading
    import time
    import queue
    
    # Turn on output
    output.turn_on()
    print("\n[SCARE] Output activated for scare")
    
    # Create a queue for communication between threads
    audio_done_queue = queue.Queue()
    
    # Determine toggle count based on audio file type and size
    toggle_count = 10  # Default toggle count
    toggle_duration = 0.2  # Default toggle duration (seconds)
    
    if audio_path:
        # Get a more accurate estimate of audio duration
        if audio_path.lower().endswith('.wav'):
            # For WAV files, use file size for estimation
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 176400 bytes per second for 44.1kHz stereo
            estimated_duration = file_size / 176400
            
            # For very short WAV files, use fewer toggles but make them slower
            if estimated_duration < 1.0:
                toggle_count = 5
                toggle_duration = 0.3  # Slower toggles for short files
                print(f"\n[AUDIO] Very short WAV detected: {estimated_duration:.1f} seconds, using {toggle_count} slow toggles")
            else:
                # Calculate toggle count based on duration (2.5 toggles per second)
                toggle_count = max(5, min(20, int(estimated_duration * 2.5)))
                print(f"\n[AUDIO] Estimated WAV duration: {estimated_duration:.1f} seconds, using {toggle_count} toggles")
        elif audio_path.lower().endswith('.mp3'):
            # MP3 files are typically longer
            toggle_count = 15  # Use more toggles for MP3 files
            print(f"\n[AUDIO] Using {toggle_count} toggles for MP3 file")
    
    # For WAV files less than 100KB, play the audio first, then do the toggling
    if audio_path and audio_path.lower().endswith('.wav') and os.path.getsize(audio_path) < 100000:
        print(f"\n[AUDIO] Playing audio first for short WAV file: {os.path.basename(audio_path)}")
        # Play audio in blocking mode
        audio.play_audio_file(audio_path, blocking=True)
        print("\n[AUDIO] Audio playback complete, now starting toggling")
        
        # Now do the toggling
        _toggle_output_fixed_count(toggle_count, toggle_duration)
    else:
        # For MP3 files and longer WAV files, use parallel approach
        if audio_path:
            # Define a wrapper function that signals when audio is done
            def play_audio_and_signal():
                import time
                start_time = time.time()
                
                # Play the audio file
                audio.play_audio_file(audio_path, blocking=True)
                
                # For MP3 files, ensure a minimum playback time of 1.5 seconds
                # This is because some MP3 files might finish too quickly due to Pygame issues
                if audio_path.lower().endswith('.mp3'):
                    elapsed = time.time() - start_time
                    min_playback_time = 1.5  # Minimum playback time in seconds
                    if elapsed < min_playback_time:
                        print(f"\n[AUDIO] Ensuring minimum playback time for MP3 file ({min_playback_time:.1f}s)")
                        time.sleep(min_playback_time - elapsed)
                
                # Signal that audio is done
                audio_done_queue.put(True)
                print("\n[AUDIO] Audio playback complete")
            
            print(f"\n[AUDIO] Starting audio playback in parallel with toggling: {os.path.basename(audio_path)}")
            audio_thread = threading.Thread(target=play_audio_and_signal)
            audio_thread.daemon = True
            audio_thread.start()
            
            # Give audio a small head start
            time.sleep(0.1)
        
        # Toggle the output with monitoring for audio completion
        # Pass is_mp3=True if it's an MP3 file so we can check pygame.mixer.music.get_busy()
        is_mp3 = audio_path and audio_path.lower().endswith('.mp3')
        _toggle_output_with_audio_sync(toggle_count, toggle_duration, audio_done_queue, is_mp3)
    
    # Turn off output at the end
    output.turn_off()

USE_PULLUP = True    # Set to True if using internal pull-up resistor

# Function to toggle output while monitoring audio completion
def _toggle_output_with_audio_sync(count, duration=0.2, audio_done_queue=None, is_mp3=False):
    """Toggle the output while monitoring audio completion
    
    Args:
        count: Number of toggles to perform (maximum)
        duration: Duration in seconds for each toggle state (on or off)
        audio_done_queue: Queue to check for audio completion signal
        is_mp3: Whether the audio file is an MP3 (to check pygame.mixer.music.get_busy())
    """
    import time
    import pygame
    
    print(f"\n[TOGGLE] Starting output toggling for up to {count} toggles (duration: {duration:.1f}s)")
    
    # Always start with output on
    output.turn_on()
    print("\n[TOGGLE] Output ON")
    time.sleep(duration)
    
    # Check if audio is already done before we even start toggling
    audio_done = False
    try:
        if audio_done_queue and not audio_done_queue.empty():
            audio_done = audio_done_queue.get_nowait()
        # For MP3 files, also check pygame.mixer.music.get_busy()
        elif is_mp3 and 'pygame' in sys.modules and hasattr(pygame.mixer.music, 'get_busy'):
            if not pygame.mixer.music.get_busy():
                audio_done = True
                print("\n[TOGGLE] Audio playback already complete (detected by pygame)")
    except Exception as e:
        print(f"\n[TOGGLE] Error checking audio status: {e}")
    
    # Do a fixed number of toggles or until audio is done
    for i in range(count):
        # If audio is done, stop toggling
        if audio_done:
            print("\n[TOGGLE] Audio playback complete, stopping toggle early")
            break
            
        # Toggle off
        output.turn_off()
        print(f"\n[TOGGLE] Toggle {i+1}/{count}: Output OFF")
        time.sleep(duration)
        
        # Check if audio is done
        try:
            if audio_done_queue and not audio_done_queue.empty():
                audio_done = audio_done_queue.get_nowait()
                if audio_done:
                    print("\n[TOGGLE] Audio playback complete, stopping toggle immediately")
                    # Break immediately - don't complete this cycle
                    break
            # For MP3 files, also check pygame.mixer.music.get_busy()
            elif is_mp3 and 'pygame' in sys.modules and hasattr(pygame.mixer.music, 'get_busy'):
                if not pygame.mixer.music.get_busy():
                    audio_done = True
                    print("\n[TOGGLE] Audio playback complete (detected by pygame), stopping toggle immediately")
                    # Break immediately - don't complete this cycle
                    break
        except Exception as e:
            print(f"\n[TOGGLE] Error checking audio status: {e}")
        
        # Toggle on
        output.turn_on()
        print(f"\n[TOGGLE] Toggle {i+1}/{count}: Output ON")
        time.sleep(duration)
        
        # Check if audio is done again
        try:
            if audio_done_queue and not audio_done_queue.empty():
                audio_done = audio_done_queue.get_nowait()
                if audio_done:
                    print("\n[TOGGLE] Audio playback complete, stopping toggle immediately")
                    # Break immediately - don't complete this cycle
                    break
            # For MP3 files, also check pygame.mixer.music.get_busy()
            elif is_mp3 and 'pygame' in sys.modules and hasattr(pygame.mixer.music, 'get_busy'):
                if not pygame.mixer.music.get_busy():
                    audio_done = True
                    print("\n[TOGGLE] Audio playback complete (detected by pygame), stopping toggle immediately")
                    # Break immediately - don't complete this cycle
                    break
        except Exception as e:
            print(f"\n[TOGGLE] Error checking audio status: {e}")
    
    # Always end with output off (if it's not already off)
    output.turn_off()
    if audio_done:
        print("\n[TOGGLE] Output turned OFF - audio complete")
    else:
        print("\n[TOGGLE] Output OFF at end")
    
    print(f"\n[TOGGLE] Completed toggling")

# Original toggle function kept for short WAV files

# Define the response to button press
def button_pressed():
    """Function called when button is pressed to trigger Halloween scare"""
    global SCARE_IN_PROGRESS, LAST_ACTIVITY_TIME, IDLE_SOUND_PLAYED
    
    # Update the last activity time - with error handling
    try:
        import time as button_time  # Local import to avoid any shadowing issues
        LAST_ACTIVITY_TIME = button_time.time()
    except Exception as e:
        print(f"\n[ERROR] Error updating activity time: {e}")
        # Use a fallback value if time module fails
        LAST_ACTIVITY_TIME = LAST_ACTIVITY_TIME + 1 if 'LAST_ACTIVITY_TIME' in globals() else 0
    
    IDLE_SOUND_PLAYED = False
    
    # Check if a scare is already in progress
    if SCARE_IN_PROGRESS:
        print("\n[SYSTEM] Scare already in progress. Ignoring trigger.")
        return
    
    # Set the flag to indicate a scare is in progress
    SCARE_IN_PROGRESS = True
    
    print("\n[SYSTEM] Button pressed! Activating Halloween scare...")
    
    try:
        # Check if audio files are available
        audio_files = os.listdir(audio.audio_dir)
        audio_path = None
        
        # Stop any currently playing audio first
        audio.stop_audio()
        
        # Select an audio file if available
        if audio_files:
            # Filter for valid audio files
            valid_audio_files = [f for f in audio_files if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
            
            if valid_audio_files:
                import random
                random_file = random.choice(valid_audio_files)
                audio_path = os.path.join(audio.audio_dir, random_file)
                print(f"\n[AUDIO] Selected Halloween audio: {random_file}")
        
        # Do the scare sequence with audio playing simultaneously
        print("\n[SYSTEM] Starting scare sequence with synchronized audio")
        do_simple_scare_with_audio(audio_path)
        
        # If no audio was played (or if it failed), play a default sound
        if not audio_path:
            print("\n[AUDIO] No audio files found, playing default scary sounds")
            audio.play_alarm(1.0)
            
            # Play an eerie melody
            notes = [196, 147, 196, 220, 196, 147, 110]  # Spooky low notes
            durations = [0.3, 0.3, 0.3, 0.5, 0.3, 0.3, 0.8]
            print("\n[AUDIO] Playing eerie melody")
            audio.play_melody(notes, durations)
    
    finally:
        # Always turn off the output device when done, regardless of errors
        print("\n[SYSTEM] Turning off output device")
        output.turn_off()
        
        # Reset the flags to allow new scares and update activity time
        SCARE_IN_PROGRESS = False
        try:
            import time as cleanup_time
            LAST_ACTIVITY_TIME = cleanup_time.time()  # Reset activity timer after scare completes
        except Exception as e:
            print(f"\n[ERROR] Error updating activity time during cleanup: {e}")
            # Use a fallback value if time module fails
            LAST_ACTIVITY_TIME = LAST_ACTIVITY_TIME + 1 if 'LAST_ACTIVITY_TIME' in globals() else 0
        IDLE_SOUND_PLAYED = False  # Reset idle sound flag
        
    print("\n[SYSTEM] Halloween scare complete")


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
    from motion_sensor import ButtonTrigger, KeyboardTrigger
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

# Reset activity timer at startup
try:
    LAST_ACTIVITY_TIME = time.time()
except Exception as e:
    print(f"Error setting initial activity time: {e}")
    LAST_ACTIVITY_TIME = 0
LAST_IDLE_SOUND_TIME = 0  # Initialize to 0 so idle sounds can play immediately
IDLE_SOUND_PLAYED = False

# Test components on startup
print("\nTesting components:")
print("1. Testing output device...")
output.blink(2, 0.2, 0.2)

print("2. Testing audio output...")
audio.play_tone(440, 0.5)  # Play A4 note

# Check audio system and files
print("3. Checking audio system...")
audio.check_audio_system()

# Test audio playback if files exist
audio_files = audio.list_audio_files()
if audio_files:
    print("\nWould you like to test audio playback with synchronized output? (y/n)")
    print("(This will play a short clip from one of your audio files and activate the output)")
    print("Press Enter to skip the test...")
    
    # Note: In a real deployment, you'd use input() here, but for this code example
    # we'll just simulate a 'yes' response
    test_audio = True
    
    if test_audio:
        import random
        import os
        # Choose a random audio file
        test_file = random.choice(audio_files)
        test_path = os.path.join(audio.audio_dir, test_file)
        print(f"\nTesting synchronized output with audio: {test_file}")
        
        # Turn on the output device
        print("Activating output device...")
        output.turn_on()
        
        try:
            # Play just the first few seconds for testing
            print("Playing short audio clip for testing...")
            
            # For WAV files, we'll use a simpler approach
            if test_file.lower().endswith('.wav'):
                import subprocess
                try:
                    # Use sox to play just the first 3 seconds if available
                    try:
                        # Check if sox is installed
                        subprocess.run(["which", "sox"], check=True, capture_output=True)
                        # Use sox to trim the audio
                        print("Using sox to play trimmed WAV file...")
                        subprocess.run(["play", "-q", test_path, "trim", "0", "3"], check=False)
                    except:
                        # Fall back to aplay if sox is not available
                        print("Sox not available, using aplay...")
                        # Just play the file and manually stop after 3 seconds
                        proc = subprocess.Popen(["aplay", "-q", test_path])
                        import time
                        time.sleep(3)  # Play for 3 seconds
                        proc.terminate()  # Then stop
                        time.sleep(0.1)  # Give it time to clean up
                        if proc.poll() is None:
                            proc.kill()  # Force kill if still running
                    print("Audio test complete")
                except Exception as e:
                    print(f"Error during WAV audio test: {e}")
            # For MP3 files
            elif test_file.lower().endswith('.mp3'):
                import subprocess
                print("Playing short MP3 clip for testing...")
                try:
                    # Play for 3 seconds
                    subprocess.run(["mpg123", "-q", "--skip", "0", "--end", "3", test_path], check=False)
                    print("Audio test complete")
                except Exception as e:
                    print(f"Error during MP3 audio test: {e}")
            # For other formats
            else:
                print("Playing generic audio format...")
                try:
                    # Just play and stop after 3 seconds
                    audio.play_audio_file(test_path)
                    import time
                    time.sleep(3)
                    audio.stop_audio()
                    print("Audio test complete")
                except Exception as e:
                    print(f"Error during audio test: {e}")
        finally:
            # Always turn off the output when done
            print("Deactivating output device...")
            output.turn_off()
            
        print("Synchronized output and audio test complete")
    else:
        print("Skipping audio test")
else:
    print("\nNo audio files found for testing.")
    print(f"You can add .wav, .mp3, or .ogg files to: {audio.audio_dir}")

# Setup button detection
print("\nSetting up button trigger...")
interrupt_success = button.setup_interrupt()
if not interrupt_success:
    print("Note: Using polling mode instead of interrupts. This will still work fine.")
    print("The button will be checked continuously in the background.")

# Setup all keyboard handlers
print("\nSetting up keyboard handlers...")
active_keyboard_handlers = []

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
print("Starting advanced keyboard trigger for SSH terminal...")
keyboard_success = advanced_keyboard.start_monitoring()
if keyboard_success:
    active_keyboard_handlers.append(("Advanced Keyboard", advanced_keyboard))
    print(f"Advanced keyboard monitoring started for key '{KEYBOARD_KEY}'")

# If advanced keyboard monitoring fails, try the simple method
if not keyboard_success and simple_keyboard is not None:
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

# Function to play a random idle sound
def play_idle_sound():
    """Play a random idle sound when there has been no activity for a while"""
    global IDLE_SOUND_PLAYED, LAST_IDLE_SOUND, LAST_IDLE_SOUND_TIME
    
    # Create idle sounds directory if it doesn't exist
    os.makedirs(IDLE_SOUNDS_DIR, exist_ok=True)
    
    # Get list of idle sound files
    idle_files = [f for f in os.listdir(IDLE_SOUNDS_DIR) 
                 if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
    
    # If no idle sounds in the dedicated directory, try using a sound from the main audio directory
    if not idle_files:
        # Check if we have the default "Snarl new.wav" in the audio directory
        default_sound = os.path.join(AUDIO_DIR, "Snarl new.wav")
        if os.path.exists(default_sound):
            if not IDLE_SOUND_PLAYED:
                print(f"No activity for {STANDBY_TIMEOUT} seconds. Playing default idle sound at 70% volume...")
                audio.play_audio_file(default_sound, volume=0.7)
                IDLE_SOUND_PLAYED = True
                LAST_IDLE_SOUND = default_sound
                try:
                    import time as idle_time
                    LAST_IDLE_SOUND_TIME = idle_time.time()  # Record when the idle sound was played
                except Exception as e:
                    print(f"Error updating idle sound time: {e}")
                    LAST_IDLE_SOUND_TIME = LAST_ACTIVITY_TIME  # Use activity time as fallback
                print("Default idle sound played at 70% volume")
        else:
            print(f"Warning: No idle sounds found in {IDLE_SOUNDS_DIR}")
            print(f"Add .wav, .mp3, or .ogg files to this directory for idle sounds")
    else:
        if not IDLE_SOUND_PLAYED:
            # Select a random idle sound, avoiding the last one played if possible
            import random
            available_files = [f for f in idle_files if os.path.join(IDLE_SOUNDS_DIR, f) != LAST_IDLE_SOUND]
            
            # If all files have been played or only one file exists, use all files
            if not available_files:
                available_files = idle_files
                
            selected_file = random.choice(available_files)
            idle_sound_path = os.path.join(IDLE_SOUNDS_DIR, selected_file)
            
            print(f"No activity for {STANDBY_TIMEOUT} seconds. Playing idle sound: {selected_file} at 70% volume")
            audio.play_audio_file(idle_sound_path, volume=0.7)
            IDLE_SOUND_PLAYED = True
            LAST_IDLE_SOUND = idle_sound_path
            try:
                import time as idle_time
                LAST_IDLE_SOUND_TIME = idle_time.time()  # Record when the idle sound was played
            except Exception as e:
                print(f"Error updating idle sound time: {e}")
                LAST_IDLE_SOUND_TIME = LAST_ACTIVITY_TIME  # Use activity time as fallback
            print(f"Idle sound played: {selected_file} at 70% volume")

# Function to check for inactivity
def check_inactivity():
    """Check if system has been inactive for the standby timeout period"""
    global LAST_ACTIVITY_TIME, IDLE_SOUND_PLAYED, LAST_IDLE_SOUND_TIME
    
    try:
        import time as check_time
        current_time = check_time.time()
        inactive_time = current_time - LAST_ACTIVITY_TIME
    except Exception as e:
        print(f"Error checking inactivity time: {e}")
        # Use a fallback approach that will trigger idle sounds occasionally
        import random
        current_time = LAST_ACTIVITY_TIME + random.randint(STANDBY_TIMEOUT - 10, STANDBY_TIMEOUT + 10)
        inactive_time = current_time - LAST_ACTIVITY_TIME
    
    # Check if it's time to reset the idle sound flag
    if IDLE_SOUND_PLAYED and (current_time - LAST_IDLE_SOUND_TIME) >= IDLE_REPEAT_INTERVAL:
        print(f"It's been {int(current_time - LAST_IDLE_SOUND_TIME)} seconds since the last idle sound. Ready to play another.")
        IDLE_SOUND_PLAYED = False
    
    # If we've been inactive for the timeout period and not in a scare
    if inactive_time >= STANDBY_TIMEOUT and not SCARE_IN_PROGRESS and not IDLE_SOUND_PLAYED:
        play_idle_sound()

# Main loop
print("\nHalloween scare system ready!")
print(f"Press the button or the '{KEYBOARD_KEY}' key to trigger...")
print("The system will respond to:")
print("1. Physical button press on GPIO pin")
print("2. Pico Pi programmed as a keyboard")
print("3. Physical keyboard 'w' key press")
print("4. SSH terminal keyboard input")
print("5. GUI button click (if GUI is enabled)")
print(f"6. Random idle sounds will play after {STANDBY_TIMEOUT} seconds of inactivity and repeat every {IDLE_REPEAT_INTERVAL} seconds")
try:
    # Blink LED to indicate system is ready
    output.blink(3, 0.1, 0.1)
    
    print("Press Ctrl+C to exit")
    while True:
        # Check for inactivity
        check_inactivity()
        
        # Sleep for a short time to avoid high CPU usage
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
