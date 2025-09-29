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
- One of the following output options:
  - GPIO-controlled relay module or LED (with 220-330 ohm resistor)
  - USB relay module (CH340 chip-based, controlled via serial commands)
- 10K ohm resistor for button (optional if using internal pull-up)
- USB, Bluetooth, or 3.5mm jack compatible speaker or amplifier
- Breadboard and jumper wires
- Micro SD card with Raspberry Pi OS installed
- Appropriate power supply for Raspberry Pi 5 (USB-C, 5V/5A recommended)
- TFT touchscreen display (optional, for GUI interface)

## Circuit Diagram

See the [circuit diagram](docs/circuit_diagram.md) for detailed connection instructions.

## Output Options

### GPIO Relay/LED
The traditional setup uses a GPIO pin to control an LED or relay module. This requires wiring the relay to the appropriate GPIO pin on the Raspberry Pi.

### USB Relay
Alternatively, you can use a USB relay module that connects via USB and is controlled through serial commands. This is easier to set up as it doesn't require any GPIO wiring - just plug it into a USB port.

#### USB Relay Requirements:
- CH340 USB-to-serial chip based relay module
- Uses the following serial commands:
  - Turn ON: `A0 01 01 A2` (hex)
  - Turn OFF: `A0 01 00 A1` (hex)
- Baud rate: 9600

The system will automatically detect which output method to use. If a USB relay is connected, it will use that; otherwise, it will fall back to the GPIO relay/LED.

## Software Setup

### 1. Set up Raspberry Pi OS

1. Download and install the Raspberry Pi Imager from the [official website](https://www.raspberrypi.com/software/).
2. Use the imager to install Raspberry Pi OS (64-bit) on your microSD card.
3. Insert the microSD card into your Raspberry Pi 5 and boot it up.
4. Complete the initial setup process for Raspberry Pi OS.


Open a terminal on your Raspberry Pi and run the following commands to install the required libraries:

```bash
sudo apt update
sudo apt install -y python3-pip python3-numpy python3-pygame mpg123 vorbis-tools alsa-utils python3-tk RPi.GPIO

# Install pyserial for USB relay support
pip3 install pyserial
```

### 3. Download Project Files

Clone the project repository or copy the following files to your Raspberry Pi:

- `motion_sensor.py` - Button trigger functionality
- `output_control.py` - GPIO-based output control
- `usb_relay_control.py` - USB relay control
- `combined_output_control.py` - Unified interface for both output types
- `audio_output.py` - Audio playback functionality
- `gui_interface.py` - Touchscreen GUI interface
- `main.py` - Main program

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

## GUI Interface

The project includes a touchscreen GUI interface that provides an on-screen button labeled "FEED THE BEAST" which triggers the same scare effect as the physical button. This allows you to control the Halloween scare system directly from the TFT screen.

### GUI Features:

- Fullscreen interface optimized for touchscreens
- Large, easy-to-press button labeled "FEED THE BEAST"
- Visual feedback when the scare is triggered
- Status indicator showing when the system is ready
- Exit button in the top-right corner

### Requirements for GUI:

- TFT touchscreen display connected to the Raspberry Pi
- Python Tkinter library (`python3-tk` package)
- X Window System running (desktop environment)

The GUI runs in a separate thread alongside the physical button detection, so you can trigger the scare using either method. To disable the GUI interface, set `USE_GUI = False` in the main.py file.

### Running the GUI

There are several ways to run the GUI interface:

#### 1. Normal Mode

The GUI will start automatically when you run the main program if a display is available:

```bash
sudo python3 code/main.py
```

#### 2. Test Mode

To test just the GUI without activating any hardware:

python3 code/run_gui.py
#### 3. Kiosk Mode

To set up the system to run in kiosk mode (fullscreen GUI that starts automatically on boot):

```bash
sudo python3 code/kiosk_mode.py --setup
sudo reboot
```

This will:
1. Install necessary packages
2. Disable screen blanking
3. Create an autostart entry
4. Configure the system to start the GUI on boot
5. Create a systemd service for more reliable startup

#### Kiosk Mode Commands

```bash
# Set up kiosk mode (full setup)
sudo python3 code/kiosk_mode.py --setup

# Enable just the autostart file
python3 code/kiosk_mode.py --enable

# Disable kiosk mode completely
sudo python3 code/kiosk_mode.py --disable

# Check kiosk mode status
python3 code/kiosk_mode.py --status
```

#### Troubleshooting Kiosk Mode

If kiosk mode is not working after setup, use the fix script:

```bash
sudo bash code/fix_kiosk.sh
sudo reboot
```

This script will:
1. Check and install required packages
2. Fix file permissions
3. Create a systemd service
4. Configure screen blanking prevention
5. Set up the display environment
6. Configure audio output

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

## Testing the USB Relay

If you're using a USB relay, you can test it separately before running the main program:

```bash
# Navigate to your project directory
cd ~/motion_sensor_project

# Run the USB relay test script
python3 code/usb_relay_control.py
```

This will attempt to detect your USB relay, turn it on and off, and perform a blink test. If successful, you should hear the relay click and see the LED on the relay module change state.

### Manual USB Relay Configuration

If the automatic detection doesn't work, you can manually specify the USB port in `main.py`:

```python
# Find your USB port first
python3 -c "import serial.tools.list_ports; print([port.device for port in serial.tools.list_ports.comports()])"

# Then edit main.py to use that specific port
output = CombinedOutputControl(output_type="usb_relay", usb_port="/dev/ttyUSB0")  # Replace with your port
```

## Troubleshooting

### Common Issues

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

- **USB Relay Not Working**
  - Make sure the USB relay is properly connected to a USB port
  - Check that the CH340 driver is installed (`lsusb` should show a device with ID 1a86:7523)
  - Try unplugging and reconnecting the USB relay
  - Run the test script to verify the relay works: `python3 code/usb_relay_control.py`
  - Try a different USB port
  - If using a USB hub, try connecting directly to the Raspberry Pi
  - Install the CH340 driver manually if needed:
    ```bash
    sudo apt update
    sudo apt install -y kmod
    sudo modprobe ch341
    sudo modprobe usbserial
    ```
    
- **Kiosk Mode Not Starting on Boot**
  - Run the fix script: `sudo bash code/fix_kiosk.sh`
  - Check the status: `python3 code/kiosk_mode.py --status`
  - Check systemd service logs: `sudo journalctl -u halloween-scare.service`
  - Verify the display environment: `echo $DISPLAY` (should be `:0`)
  - Check if the service is running: `sudo systemctl status halloween-scare.service`
  - Try manually starting the service: `sudo systemctl start halloween-scare.service`
  - Check for permission issues: `ls -la /home/pi/motion_sensor_project/code/`
  - Verify the GUI works manually: `DISPLAY=:0 python3 code/run_gui.py`

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
  - Use the included audio test script to diagnose and fix issues:
    ```bash
    # Check audio devices
    python3 code/audio_test.py --check
    
    # Force audio to headphone jack
    python3 code/audio_test.py --headphones
    
    # Apply all headphone jack fixes (recommended)
    python3 code/audio_test.py --fix-headphones
    
    # Test headphone jack specifically
    python3 code/audio_test.py --test-headphones
    
    # Test all audio methods
    python3 code/audio_test.py --all
    ```
  - Set the audio output manually:
    ```bash
    # Set output to headphone jack
    amixer cset numid=3 1
    
    # Set volume to maximum
    amixer set Master 100%
    ```

- **Permission Errors**
  - Make sure to run the program with `sudo` to access GPIO pins
  - Check file permissions for audio files

- **Program Crashes**
  - Check for error messages in the terminal
  - Verify that all required libraries are installed
  - Make sure GPIO pin numbers match your actual connections

- **GUI Not Appearing**
  - Make sure you're running in a desktop environment
  - Verify that python3-tk is installed: `sudo apt install python3-tk`
  - Check for "No display available" error messages
  - If using SSH, use X11 forwarding: `ssh -X admin@yumpi`
  - Try setting the DISPLAY variable: `export DISPLAY=:0`
  - Run just the GUI test script: `python3 code/run_gui.py`

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
