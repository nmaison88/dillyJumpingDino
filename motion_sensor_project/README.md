# Button-Activated Halloween Scare with Raspberry Pi 5

A Raspberry Pi 5 project that uses a button to trigger both an output device (LED/relay) and spooky audio output for Halloween scares.

## Features

- Button-activated trigger for Halloween scares
- Visual output via LED (can be replaced with a relay for controlling other devices like fog machines or animatronics)
- Audio output with multiple options:
  - Spooky sound effects and screams using audio files
  - Simple tones and melodies using pygame and numpy
  - Audio file playback (.wav, .mp3, .ogg) using Raspberry Pi's built-in audio
  - Support for USB, Bluetooth, HDMI, or 3.5mm jack audio output
- Modular design for easy customization
- Interrupt-based button detection with debounce for reliability
- Random audio file playback when button is pressed

## Hardware Requirements

- Raspberry Pi 5
- Momentary push button (normally open)
- LED or relay module (for controlling lights, fog machines, or other props)
- 220-330 ohm resistor for LED
- 10K ohm resistor for button (optional if using internal pull-up)
- USB, Bluetooth, or 3.5mm jack compatible speaker or amplifier
- Breadboard and jumper wires
- Micro SD card with Raspberry Pi OS installed
- Appropriate power supply for Raspberry Pi 5 (USB-C, 5V/5A recommended)

## Circuit Diagram

See the [circuit diagram](docs/circuit_diagram.md) for detailed connection instructions.

## Software Setup

### 1. Set up Raspberry Pi OS

1. Download and install the Raspberry Pi Imager from the [official website](https://www.raspberrypi.com/software/).
2. Use the imager to install Raspberry Pi OS (64-bit) on your microSD card.
3. Insert the microSD card into your Raspberry Pi 5 and boot it up.
4. Complete the initial setup process for Raspberry Pi OS.

### 2. Install Required Libraries

Open a terminal on your Raspberry Pi and run the following commands to install the required libraries:

```bash
sudo apt update
sudo apt install -y python3-pip python3-numpy python3-pygame mpg123
pip3 install RPi.GPIO
```

### 3. Download Project Files

Clone the project repository or copy the following files to your Raspberry Pi:

- `motion_sensor.py`
- `output_control.py`
- `audio_output.py`
- `main.py`

You can place them in a directory of your choice, for example:

```bash
mkdir -p ~/motion_sensor_project
cp /path/to/files/* ~/motion_sensor_project/
```

## Configuration

You can customize the project by modifying the parameters in `main.py`:

```python
# Configuration
BUTTON_PIN = 17      # Button pin (BCM numbering)
OUTPUT_PIN = 18      # LED/Relay pin (BCM numbering)

# Audio files are stored in the project directory
import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio_files")  # Audio files in project directory

USE_PULLUP = True    # Set to True if using internal pull-up resistor
```

You can add your own spooky audio files (.wav, .mp3, .ogg) to the project's `audio_files` directory, and they will be played randomly when the button is pressed. The system will automatically detect and use any audio files you add.

> **Note about audio files**: WAV files are handled differently than MP3/OGG files for better reliability. WAV playback uses a blocking approach that waits for the file to finish playing before continuing, while MP3/OGG files use a non-blocking approach with a duration estimate.

## Usage

1. Connect the hardware according to the circuit diagram.
2. Make sure all the required libraries are installed.
3. Add spooky audio files to the project's `audio_files` directory:
   ```bash
   # Copy audio files to the project directory
   cp /path/to/your/spooky_sounds/*.mp3 ~/motion_sensor_project/audio_files/
   ```
   
   You can find free Halloween sound effects on websites like:
   - [Freesound.org](https://freesound.org/search/?q=halloween)
   - [SoundBible](https://soundbible.com/tags-halloween.html)
   - [Orange Free Sounds](https://orangefreesounds.com/category/sound-effects/halloween-sound-effects/)
4. Run the main program:

```bash
sudo python3 main.py
```
5. The system will initialize and wait for button presses.
6. When the button is pressed:
   - The LED (or connected device/prop) will activate immediately
   - If audio files are available, a random one will be played
   - The output will remain on for the duration of the audio playback
   - If no audio files are available, an alarm sound followed by a melody will play
   - The output will automatically turn off when the audio finishes

7. Hide the button where you can easily access it, and the main unit (with speakers) where it will scare your visitors!

> Note: The program needs to be run with `sudo` to access the GPIO pins.

The program is designed to synchronize the output and audio behavior. When the button is pressed, the output will turn on immediately, and the audio will start playing. The output will remain on for the duration of the audio playback, and will automatically turn off when the audio finishes. This ensures that the output and audio are always in sync, creating a more immersive and frightening experience for your visitors.

## Halloween Customization Ideas

- Connect a relay to control a fog machine when the button is pressed
- Add multiple buttons for different scare effects or sounds
- Connect to animatronic props or pneumatic systems for physical scares
- Use a hidden pressure mat instead of a button for automatic triggering
- Add LED strip lights that flash with the audio
- Set up a hidden camera to record reactions to your scares
- Create a sequence of events (lights, sound, movement) for maximum scare effect
- Use a wireless remote button so you can trigger the scare from a distance
- Add a motion sensor as an alternative trigger method
- Connect multiple Raspberry Pis for a coordinated haunted house experience

## Troubleshooting

- **Button Not Triggering Scare**
  - Check button connections and wiring
  - Verify that you're using the correct GPIO pin number
  - If using pull-up configuration, ensure button connects to ground when pressed
  - If using pull-down configuration, ensure button connects to 3.3V when pressed
  - Try adjusting the debounce time if button presses are inconsistent

- **'Failed to add edge detection' Error**
  - This error can occur if there's a conflict with the GPIO pin
  - The program will automatically fall back to polling mode, which should still work
  - If you continue to have issues:
    - Try using a different GPIO pin for the button (update `BUTTON_PIN` in main.py)
    - Restart your Raspberry Pi to reset all GPIO states
    - Run `sudo gpio unexportall` before starting the program to reset GPIO

- **No Audio Output**
  - Check that your speakers are properly connected and powered on
  - Run `aplay -l` to verify that your audio device is recognized
  - Adjust the system volume using `alsamixer` or the desktop volume control
  - Make sure required audio libraries are installed:
    ```bash
    sudo apt update
    sudo apt install -y python3-pygame mpg123 vorbis-tools alsa-utils
    ```
  - Try a different audio output method (USB, Bluetooth, HDMI, or 3.5mm jack)
  - Test audio playback directly with system commands:
    ```bash
    # For MP3 files
    mpg123 /home/pi/audio_files/your_file.mp3
    
    # For WAV files
    aplay /home/pi/audio_files/your_file.wav
    
    # For OGG files
    ogg123 /home/pi/audio_files/your_file.ogg
    ```

- **Permission Errors**
  - Make sure to run the program with `sudo` to access GPIO pins
  - Check file permissions for audio files

- **Program Crashes**
  - Check for error messages in the terminal
  - Verify that all required libraries are installed
  - Make sure GPIO pin numbers match your actual connections

## License

This project is released under the MIT License. See the LICENSE file for details.

## Running at Startup

To make the program run automatically at startup:

1. Edit the systemd service file:

```bash
sudo nano /etc/systemd/system/motion-sensor.service
```

2. Add the following content:

```
[Unit]
Description=Motion Sensor Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/motion_sensor_project/main.py
WorkingDirectory=/home/pi/motion_sensor_project
User=root
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable motion-sensor.service
sudo systemctl start motion-sensor.service
```

4. Check the status:

```bash
sudo systemctl status motion-sensor.service
```

## Credits

Created by [Your Name]
