"""
Audio Output Module for Raspberry Pi 5
This module handles audio output using the built-in audio capabilities
of the Raspberry Pi 5 for both simple tones and audio file playback.
"""
import os
import time
import subprocess
import threading
import numpy as np
import pygame
from pygame import mixer

# Initialize pygame mixer
try:
    # Try to initialize with specific device settings for headphone output
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    PYGAME_AVAILABLE = True
except Exception as e:
    PYGAME_AVAILABLE = False
    print(f"Error initializing pygame mixer: {e}")
    print("Install pygame for audio playback: pip install pygame")

# Configure system audio to use headphone jack
def configure_audio_output():
    """Configure system audio to use headphone jack"""
    try:
        # Set the audio output to analog (headphone jack)
        import subprocess
        print("Configuring audio output to use headphone jack...")
        
        # Based on the audio test results, we know the headphone jack is card 1
        # Method 1: Using amixer to set the default audio device
        try:
            # Set the default audio device to card 1 (Headphones)
            subprocess.run(["amixer", "cset", "numid=3", "1"], check=False)
            print("Set default audio device to headphone jack")
        except Exception as e:
            print(f"Method 1 failed: {e}")
            
        # Method 2: Set volume to maximum
        try:
            subprocess.run(["amixer", "set", "Master", "100%"], check=False)
            print("Set volume to maximum")
        except Exception as e:
            print(f"Could not set volume: {e}")
        
        # Method 3: Using specific ALSA configuration
        try:
            # Create an .asoundrc file to set the default device
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
            
        print("Audio output configuration complete")
    except Exception as e:
        print(f"Warning: Could not configure audio output: {e}")
        print("You may need to manually configure audio output to use the headphone jack")

# Run audio configuration
configure_audio_output()

class AudioOutput:
    def __init__(self, audio_dir="/home/pi/audio_files"):
        """
        Initialize the audio output.
        
        Args:
            audio_dir: Directory where audio files are stored
        """
        self.audio_dir = audio_dir
        self.current_process = None
        
        # Create audio directory if it doesn't exist
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                print("Pygame mixer initialized for audio playback")
            except Exception as e:
                print(f"Error reinitializing pygame mixer: {e}")
        else:
            print("Pygame mixer not available. Using system commands for audio playback.")
            
        # Check audio system
        self.check_audio_system()
    
    def play_tone(self, frequency, duration=0.5, volume=50):
        """
        Play a tone of specified frequency.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            volume: Volume level (0-100)
        """
        if frequency <= 0:
            return
        
        if PYGAME_AVAILABLE:
            # Generate a sine wave
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(frequency * 2 * np.pi * t) * (volume / 100)
            
            # Convert to 16-bit signed integers
            audio_data = (tone * 32767).astype(np.int16)
            
            # Create a pygame Sound object
            sound = pygame.mixer.Sound(audio_data.tobytes())
            
            # Play the sound
            sound.play()
            
            # Wait for the sound to finish
            time.sleep(duration)
        else:
            # Fallback to using system command (aplay)
            cmd = f"play -n synth {duration} sine {frequency} vol {volume/100}"
            try:
                subprocess.run(cmd, shell=True, check=False)
            except Exception as e:
                print(f"Error playing tone: {e}")
    
    def play_alarm(self, duration=3):
        """
        Play an alarm sound.
        
        Args:
            duration: Total duration in seconds
        """
        # Check if we have a pre-recorded alarm sound
        alarm_file = os.path.join(self.audio_dir, "alarm.wav")
        if os.path.exists(alarm_file):
            self.play_audio_file(alarm_file)
            return
            
        # Otherwise generate an alarm tone
        start_time = time.time()
        while time.time() - start_time < duration:
            # Alternate between two frequencies for alarm effect
            self.play_tone(800, 0.1, 70)
            self.play_tone(600, 0.1, 70)
    
    def play_melody(self, notes, durations):
        """
        Play a melody defined by a sequence of notes and durations.
        
        Args:
            notes: List of frequencies in Hz
            durations: List of durations in seconds for each note
        """
        if len(notes) != len(durations):
            print("Error: notes and durations must have the same length")
            return
            
        for i in range(len(notes)):
            self.play_tone(notes[i], durations[i])
            time.sleep(0.05)  # Small pause between notes
    
    def list_audio_files(self, directory=None):
        """
        List available audio files in the specified directory.
        
        Args:
            directory: Directory to list files from (defaults to self.audio_dir)
        """
        if directory is None:
            directory = self.audio_dir
            
        try:
            # Make sure the directory exists
            if not os.path.exists(directory):
                print(f"Creating audio directory: {directory}")
                os.makedirs(directory, exist_ok=True)
                return []
                
            # List all files
            files = os.listdir(directory)
            
            # Filter for audio files
            audio_files = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
            
            if audio_files:
                print(f"Found {len(audio_files)} audio file(s) in {directory}")
            else:
                print(f"No audio files found in {directory}")
                
            return audio_files
        except Exception as e:
            print(f"Error listing audio files: {e}")
            return []
    
    def play_audio_file(self, filename, volume=1.0):
        """
        Play an audio file.
        
        Args:
            filename: Path to the audio file
            volume: Volume level from 0.0 to 1.0 (default: 1.0 = maximum)
        """
        if not os.path.exists(filename):
            print(f"Audio file not found: {filename}")
            return False
            
        print(f"Playing audio file: {filename}")
        
        # Make sure any previous playback is stopped
        self.stop_audio()
        
        # Ensure audio is routed to headphone jack
        self._ensure_headphone_output()
        
        # For WAV files, use a simpler approach to avoid memory issues
        if filename.lower().endswith('.wav'):
            try:
                # Try multiple methods to play WAV files
                print("Playing WAV file through headphone jack...")
                
                # Method 1: aplay with headphone device specification (card 1)
                try:
                    # Use card 1 (Headphones) based on audio test results
                    subprocess.run(["aplay", "-D", "plughw:1,0", "-q", filename], check=False)
                    print("WAV playback complete using plughw:1,0 (headphone jack)")
                    return True
                except Exception as e:
                    print(f"Method 1 failed: {e}, trying next method...")
                
                # Method 2: standard aplay
                try:
                    subprocess.run(["aplay", "-q", filename], check=False)
                    print("WAV playback complete using standard aplay")
                    return True
                except Exception as e:
                    print(f"Method 2 failed: {e}, trying next method...")
                    
                # Method 3: Try pygame
                if PYGAME_AVAILABLE:
                    try:
                        # Set volume
                        pygame.mixer.music.set_volume(volume)
                        
                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()
                        # Wait for playback to complete
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        print("WAV playback complete using pygame")
                        return True
                    except Exception as e:
                        print(f"Method 3 failed: {e}")
                        
                print("All WAV playback methods failed")
                return False
            except Exception as e:
                print(f"Error playing WAV file: {e}")
                return False
        
        # For MP3 files
        elif filename.lower().endswith('.mp3'):
            # Try multiple methods for MP3
            
            # Method 1: Try pygame first
            if PYGAME_AVAILABLE:
                try:
                    # Set volume according to parameter
                    pygame.mixer.music.set_volume(volume)
                    
                    # Load and play the file
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()
                    
                    # Give a moment for playback to start
                    time.sleep(0.1)
                    
                    if pygame.mixer.music.get_busy():
                        print("MP3 playback started with pygame")
                        return True
                except Exception as e:
                    print(f"Pygame MP3 playback failed: {e}, trying next method...")
            
            # Method 2: Try mpg123 with specific output device (headphone jack)
            try:
                # Try to use the headphone jack directly (card 1)
                # Convert volume (0.0-1.0) to mpg123 scale (0-100)
                vol_percent = int(volume * 100)
                cmd = ["mpg123", "-a", "hw:1,0", "-q", "--scale", str(vol_percent), filename]
                print(f"Playing with command: {' '.join(cmd)}")
                process = subprocess.Popen(cmd)
                
                # Store the process only if it started successfully
                if process.poll() is None:
                    self.current_process = process
                    print("MP3 playback started with mpg123 using hw:1,0 (headphone jack)")
                    return True
            except Exception as e:
                print(f"mpg123 with device specification failed: {e}, trying next method...")
            
            # Method 3: Standard mpg123
            try:
                # Convert volume (0.0-1.0) to mpg123 scale (0-100)
                vol_percent = int(volume * 100)
                cmd = ["mpg123", "-q", "--scale", str(vol_percent), filename]
                print(f"Playing with command: {' '.join(cmd)}")
                process = subprocess.Popen(cmd)
                
                if process.poll() is None:
                    self.current_process = process
                    print("MP3 playback started with standard mpg123")
                    return True
            except Exception as e:
                print(f"Standard mpg123 failed: {e}")
                
            print("All MP3 playback methods failed")
            return False
        
        # For other formats
        else:
            # Try pygame first
            if PYGAME_AVAILABLE:
                try:
                    # Set volume
                    pygame.mixer.music.set_volume(volume)
                    
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()
                    time.sleep(0.1)
                    if pygame.mixer.music.get_busy():
                        print("Audio playback started with pygame")
                        return True
                except Exception as e:
                    print(f"Pygame playback failed: {e}, trying system commands...")
            
            # Use system command as fallback
            try:
                # Choose the appropriate command based on file type
                if filename.lower().endswith('.ogg'):
                    # Convert volume (0.0-1.0) to ogg123 scale (0.0-1.0)
                    cmd = ["ogg123", "-d", "alsa", "-q", "--volume", str(volume), filename]  # Specify ALSA output
                else:
                    # aplay doesn't have direct volume control, we'll use softvol plugin if needed
                    vol_percent = int(volume * 100)
                    if volume < 1.0:
                        cmd = ["aplay", "-D", f"softvol:softvol=volume={vol_percent}", "-q", filename]
                    else:
                        cmd = ["aplay", "-D", "plughw:0,0", "-q", filename]  # Try with device specification
                    
                print(f"Playing with command: {' '.join(cmd)}")
                process = subprocess.Popen(cmd)
                
                if process.poll() is None:
                    self.current_process = process
                    print("Audio playback started with system command")
                    return True
                else:
                    print("Failed to start audio playback process")
                    return False
                    
            except Exception as e:
                print(f"Error playing audio file with system command: {e}")
                return False
                
    def _ensure_headphone_output(self):
        """Ensure audio is routed to the headphone jack"""
        try:
            # Try to force audio to the headphone jack (card 1)
            subprocess.run(["amixer", "cset", "numid=3", "1"], check=False)
            
            # Set volume to maximum
            subprocess.run(["amixer", "set", "Master", "100%"], check=False)
            
            # Create a temporary ALSA config for this process if needed
            # This ensures we're using the headphone jack (card 1)
            os.environ['ALSA_CARD'] = '1'
        except Exception as e:
            print(f"Warning: Could not ensure headphone output: {e}")
            # Continue anyway, as we have multiple fallback methods
    
    def stop_audio(self):
        """
        Stop any currently playing audio.
        """
        # Stop pygame audio if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()  # Stop all sound channels
            except Exception as e:
                print(f"Error stopping pygame audio: {e}")
            
        # Stop any system processes - more carefully
        if self.current_process and self.current_process.poll() is None:
            try:
                # Send SIGTERM
                self.current_process.terminate()
                # Give it a moment to terminate
                time.sleep(0.1)
                # Check if it's still running
                if self.current_process and self.current_process.poll() is None:
                    # Only send SIGKILL if still running
                    self.current_process.kill()
                    time.sleep(0.1)  # Give it time to clean up
            except Exception as e:
                print(f"Error stopping audio process: {e}")
            finally:
                # Clear the reference to avoid double free
                self.current_process = None
        
        # We'll avoid the aggressive pkill approach as it might be causing the double free
        # Instead, we'll just make sure our own process is properly terminated
    
    def play_audio_async(self, filename, volume=1.0):
        """
        Play audio file asynchronously (in a separate thread).
        
        Args:
            filename: Path to the audio file
            volume: Volume level from 0.0 to 1.0 (default: 1.0 = maximum)
        """
        thread = threading.Thread(target=self.play_audio_file, args=(filename, volume))
        thread.daemon = True  # Thread will exit when main program exits
        thread.start()
        return thread
        
    def check_audio_system(self):
        """
        Check if the audio system is working properly and print diagnostic information.
        """
        print("\nChecking audio system...")
        
        # Check pygame status
        if PYGAME_AVAILABLE:
            print("✓ Pygame is available for audio playback")
        else:
            print("✗ Pygame is not available, will use system commands")
        
        # Check for audio files
        audio_files = self.list_audio_files()
        if audio_files:
            print(f"✓ Found {len(audio_files)} audio file(s) in {self.audio_dir}")
            for i, file in enumerate(audio_files[:5]):
                print(f"  {i+1}. {file}")
            if len(audio_files) > 5:
                print(f"  ... and {len(audio_files) - 5} more")
        else:
            print(f"✗ No audio files found in {self.audio_dir}")
            print(f"  You can add .wav, .mp3, or .ogg files to this directory")
        
        # Check for system audio players
        audio_players = []
        try:
            # Check for aplay (for WAV files)
            result = subprocess.run(["which", "aplay"], capture_output=True, text=True)
            if result.returncode == 0:
                audio_players.append("aplay (WAV)")
                
            # Check for mpg123 (for MP3 files)
            result = subprocess.run(["which", "mpg123"], capture_output=True, text=True)
            if result.returncode == 0:
                audio_players.append("mpg123 (MP3)")
                
            # Check for ogg123 (for OGG files)
            result = subprocess.run(["which", "ogg123"], capture_output=True, text=True)
            if result.returncode == 0:
                audio_players.append("ogg123 (OGG)")
                
            if audio_players:
                print(f"✓ Found audio players: {', '.join(audio_players)}")
            else:
                print("✗ No system audio players found")
                print("  Consider installing: sudo apt install alsa-utils mpg123 vorbis-tools")
        except Exception as e:
            print(f"Error checking audio players: {e}")
            
        # Try to get audio devices
        try:
            result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
            if "no soundcards found" in result.stdout.lower() or "no soundcards found" in result.stderr.lower():
                print("✗ No sound cards detected by ALSA")
            else:
                print("✓ Sound card(s) detected by ALSA")
        except Exception as e:
            print(f"Error checking sound cards: {e}")
            
        print("Audio system check complete\n")


# Example usage
if __name__ == "__main__":
    try:
        audio = AudioOutput()
        
        # Play a simple tone
        print("Playing a tone...")
        audio.play_tone(440, 1)  # A4 note for 1 second
        
        # Play an alarm
        print("Playing an alarm...")
        audio.play_alarm(2)
        
        # Play a simple melody (first few notes of "Twinkle Twinkle Little Star")
        notes = [262, 262, 392, 392, 440, 440, 392]  # C4, C4, G4, G4, A4, A4, G4
        durations = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
        print("Playing a melody...")
        audio.play_melody(notes, durations)
        
        # List audio files
        print("\nListing audio files:")
        files = audio.list_audio_files()
        if files:
            print("Audio files found:")
            for file in files:
                print(f"- {file}")
                
            # Play first audio file (if any)
            audio_path = os.path.join(audio.audio_dir, files[0])
            print(f"\nPlaying audio file: {audio_path}")
            audio.play_audio_file(audio_path)
            time.sleep(5)  # Let the audio play for a bit
        else:
            print("No audio files found in the audio directory")
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        
    finally:
        # Clean up
        if 'audio' in locals():
            audio.stop_audio()
        print("Audio resources cleaned up")
