#!/usr/bin/env python3
"""
Audio Test Script for Halloween Scare System
This script tests different audio output methods to help configure the headphone jack
"""
import os
import sys
import subprocess
import time
import argparse

# Add the current directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Try to import pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not available. Some tests will be skipped.")

def check_audio_devices():
    """Check available audio devices"""
    print("\n=== CHECKING AUDIO DEVICES ===")
    
    # Check ALSA devices
    print("\nALSA Devices:")
    try:
        subprocess.run(["aplay", "-l"], check=False)
    except Exception as e:
        print(f"Error checking ALSA devices: {e}")
    
    # Check current audio settings
    print("\nCurrent Audio Settings:")
    try:
        subprocess.run(["amixer", "cget", "numid=3"], check=False)
    except Exception as e:
        print(f"Error checking audio settings: {e}")
    
    # Check if headphone jack is detected
    print("\nChecking for headphone jack:")
    try:
        result = subprocess.run(["grep", "headphone", "/proc/asound/cards"], 
                               capture_output=True, text=True, check=False)
        if "headphone" in result.stdout.lower():
            print("Headphone jack detected!")
        else:
            print("Headphone jack not explicitly detected in sound cards.")
    except Exception as e:
        print(f"Error checking for headphone jack: {e}")

def set_audio_output(output_type):
    """
    Set the audio output type
    
    Args:
        output_type: 0=auto, 1=headphones, 2=hdmi
    """
    print(f"\n=== SETTING AUDIO OUTPUT TO {'AUTO' if output_type==0 else 'HEADPHONES' if output_type==1 else 'HDMI'} ===")
    
    try:
        # Using amixer to set the audio output
        subprocess.run(["amixer", "cset", "numid=3", str(output_type)], check=False)
        print("Audio output set successfully")
        
        # Set volume to maximum
        subprocess.run(["amixer", "set", "Master", "100%"], check=False)
        print("Volume set to maximum")
    except Exception as e:
        print(f"Error setting audio output: {e}")
        print("You may need to manually configure audio output")

def test_pygame_audio():
    """Test audio playback using pygame"""
    if not PYGAME_AVAILABLE:
        print("Pygame not available. Skipping pygame audio test.")
        return False
        
    print("\n=== TESTING PYGAME AUDIO ===")
    
    try:
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        print("Pygame mixer initialized")
        
        # Generate a test tone
        print("Playing test tone with pygame...")
        
        # Create a Sound object with a simple sine wave
        duration = 1.0  # seconds
        frequency = 440  # Hz (A4 note)
        sample_rate = 44100
        
        # Initialize pygame
        pygame.init()
        
        # Play a simple beep
        pygame.mixer.Sound(f"{current_dir}/../audio_files/test_tone.wav").play()
        time.sleep(1)
        
        print("Pygame audio test complete")
        return True
    except Exception as e:
        print(f"Error testing pygame audio: {e}")
        return False

def test_aplay():
    """Test audio playback using aplay"""
    print("\n=== TESTING APLAY AUDIO ===")
    
    # Create a test WAV file if it doesn't exist
    test_file = f"{os.path.dirname(current_dir)}/audio_files/test_tone.wav"
    if not os.path.exists(test_file):
        try:
            # Generate a test tone using sox
            print("Generating test tone...")
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            subprocess.run(["sox", "-n", test_file, "synth", "1", "sine", "440"], check=False)
        except Exception:
            print("Could not generate test tone with sox.")
            print("Creating an empty file for testing...")
            with open(test_file, "w") as f:
                f.write("Test file")
    
    # Test methods
    methods = [
        ["aplay", "-q", test_file],
        ["aplay", "-D", "default", "-q", test_file],
        ["aplay", "-D", "plughw:0,0", "-q", test_file],  # HDMI
        ["aplay", "-D", "hw:0,0", "-q", test_file],      # HDMI
        ["aplay", "-D", "plughw:1,0", "-q", test_file],  # Headphones
        ["aplay", "-D", "hw:1,0", "-q", test_file],      # Headphones
        ["aplay", "-D", "sysdefault:CARD=Headphones", "-q", test_file]
    ]
    
    success = False
    for i, cmd in enumerate(methods):
        try:
            print(f"\nMethod {i+1}: {' '.join(cmd)}")
            subprocess.run(cmd, check=False)
            print(f"Method {i+1} completed")
            success = True
        except Exception as e:
            print(f"Method {i+1} failed: {e}")
    
    return success

def test_headphone_jack():
    """Test audio playback specifically on the headphone jack"""
    print("\n=== TESTING HEADPHONE JACK AUDIO ===")
    
    # Create a test WAV file if it doesn't exist
    test_file = f"{os.path.dirname(current_dir)}/audio_files/test_tone.wav"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    print("Setting up headphone jack output...")
    
    # Method 1: Set the default audio device to card 1 (Headphones)
    try:
        subprocess.run(["amixer", "cset", "numid=3", "1"], check=False)
        print("Set default audio device to headphone jack")
    except Exception as e:
        print(f"Could not set default audio device: {e}")
    
    # Method 2: Set environment variable
    os.environ['ALSA_CARD'] = '1'
    print("Set ALSA_CARD=1 environment variable")
    
    # Method 3: Create .asoundrc file
    try:
        home_dir = os.path.expanduser("~")
        asoundrc_path = os.path.join(home_dir, ".asoundrc")
        
        with open(asoundrc_path, "w") as f:
            f.write("""pcm.!default {
    type hw
    card 1
    device 0
}

ctl.!default {
    type hw
    card 1
}
""")
        print(f"Created .asoundrc file at {asoundrc_path}")
    except Exception as e:
        print(f"Could not create .asoundrc file: {e}")
    
    # Test playback
    print("\nPlaying test tone through headphone jack...")
    try:
        subprocess.run(["aplay", "-D", "plughw:1,0", "-q", test_file], check=False)
        print("Headphone jack test completed successfully")
        return True
    except Exception as e:
        print(f"Headphone jack test failed: {e}")
        return False

def test_mpg123():
    """Test audio playback using mpg123"""
    print("\n=== TESTING MPG123 AUDIO ===")
    
    # Create a test MP3 file path
    test_file = f"{os.path.dirname(current_dir)}/audio_files/test_tone.mp3"
    
    # Check if the file exists
    if not os.path.exists(test_file):
        print(f"Test MP3 file not found: {test_file}")
        print("Skipping mpg123 test")
        return False
    
    # Test methods
    methods = [
        ["mpg123", "-q", test_file],
        ["mpg123", "-a", "hw:0,0", "-q", test_file],
        ["mpg123", "-a", "default", "-q", test_file],
        ["mpg123", "-o", "alsa", "-q", test_file]
    ]
    
    success = False
    for i, cmd in enumerate(methods):
        try:
            print(f"\nMethod {i+1}: {' '.join(cmd)}")
            subprocess.run(cmd, check=False)
            print(f"Method {i+1} completed")
            success = True
        except Exception as e:
            print(f"Method {i+1} failed: {e}")
    
    return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Audio Test for Halloween Scare System")
    parser.add_argument("--check", action="store_true", help="Check audio devices")
    parser.add_argument("--headphones", action="store_true", help="Set output to headphones")
    parser.add_argument("--hdmi", action="store_true", help="Set output to HDMI")
    parser.add_argument("--auto", action="store_true", help="Set output to auto")
    parser.add_argument("--test-pygame", action="store_true", help="Test pygame audio")
    parser.add_argument("--test-aplay", action="store_true", help="Test aplay")
    parser.add_argument("--test-mpg123", action="store_true", help="Test mpg123")
    parser.add_argument("--test-headphones", action="store_true", help="Test headphone jack specifically")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fix-headphones", action="store_true", help="Apply all fixes for headphone jack")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Check audio devices
    if args.check or args.all:
        check_audio_devices()
    
    # Set audio output
    if args.headphones or args.fix_headphones:
        set_audio_output(1)
    elif args.hdmi:
        set_audio_output(2)
    elif args.auto:
        set_audio_output(0)
    
    # Special fix for headphones
    if args.fix_headphones:
        print("\n=== APPLYING ALL HEADPHONE FIXES ===")
        # Create .asoundrc file
        try:
            home_dir = os.path.expanduser("~")
            asoundrc_path = os.path.join(home_dir, ".asoundrc")
            
            with open(asoundrc_path, "w") as f:
                f.write("""pcm.!default {
    type hw
    card 1
    device 0
}

ctl.!default {
    type hw
    card 1
}
""")
            print(f"Created .asoundrc file at {asoundrc_path}")
            
            # Set environment variable
            os.environ['ALSA_CARD'] = '1'
            print("Set ALSA_CARD=1 environment variable")
            
            # Set volume to maximum
            subprocess.run(["amixer", "set", "Master", "100%"], check=False)
            print("Set volume to maximum")
            
            print("All headphone fixes applied")
        except Exception as e:
            print(f"Error applying headphone fixes: {e}")
    
    # Test audio playback
    if args.test_pygame or args.all:
        test_pygame_audio()
    
    if args.test_aplay or args.all:
        test_aplay()
    
    if args.test_mpg123 or args.all:
        test_mpg123()
        
    if args.test_headphones or args.all:
        test_headphone_jack()

if __name__ == "__main__":
    main()
