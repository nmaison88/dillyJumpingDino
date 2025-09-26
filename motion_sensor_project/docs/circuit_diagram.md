# Circuit Diagram for Button-Activated Halloween Scare with Raspberry Pi 5

## Components
- Raspberry Pi 5
- Momentary push button (normally open)
- LED (for visual output or indicator)
- 220-330 ohm resistor (for LED)
- 10K ohm resistor (optional if not using internal pull-up)
- Breadboard and jumper wires

## Optional Components
- USB or Bluetooth speaker (for spooky audio output)
- Relay module (to control fog machines, animatronics, or other props)
- Extension wires (to place button in a hidden location)

## Connections

### Button (with internal pull-up)
- One terminal → GPIO 17 (BCM numbering) on Raspberry Pi 5
- Other terminal → GND pin on Raspberry Pi 5

### Button (with external pull-down - alternative configuration)
- One terminal → GPIO 17 (BCM numbering) on Raspberry Pi 5
- Same terminal → GND via 10K ohm resistor (pull-down)
- Other terminal → 3.3V pin on Raspberry Pi 5

### LED Output
- Anode (+) → GPIO 18 (BCM numbering) on Raspberry Pi 5 through 220-330 ohm resistor
- Cathode (-) → GND on Raspberry Pi 5

### Audio Output
The Raspberry Pi 5 has built-in audio capabilities:

1. **USB Audio**: Connect any USB speaker to one of the USB ports
2. **Bluetooth Audio**: Pair a Bluetooth speaker using the Raspberry Pi's Bluetooth
3. **HDMI Audio**: Audio can be output through the HDMI port to a monitor or TV with speakers
4. **3.5mm Audio Jack**: Connect directly to powered speakers or an amplifier

### Optional: Relay Module (for controlling other devices)
- VCC → 5V pin on Raspberry Pi 5
- GND → GND pin on Raspberry Pi 5
- IN → GPIO 18 (BCM numbering) on Raspberry Pi 5 (same as LED, can be used alternatively)

## Notes
- The PIR sensor may need calibration. Adjust the sensitivity and delay potentiometers on the sensor.
- The Raspberry Pi 5 uses BCM pin numbering in our code, so make sure to connect to the correct GPIO pins.
- For audio output, the simplest approach is to use the built-in 3.5mm audio jack or USB audio.
- The LED can be replaced with a relay to control other devices like lights or alarms.
- The Raspberry Pi 5 requires a proper power supply (USB-C, 5V/5A recommended for full performance).
- Consider using a case with proper cooling as the Raspberry Pi 5 can generate heat during operation.

## GPIO Pin Reference

Here's a quick reference for the GPIO pins used in this project (BCM numbering):

- **GPIO 17**: Button input
- **GPIO 18**: LED/Relay output for Halloween props

You can use other GPIO pins by modifying the pin numbers in the code.

## Halloween Setup Tips

1. **Hide the Button**: Place the button in a location where you can easily press it when visitors approach, but where they can't see it.

2. **Conceal the Raspberry Pi**: Hide the Raspberry Pi and any wiring in a decorated box or behind props.

3. **Position Speakers Strategically**: Place speakers where they will have the maximum scare effect, possibly hidden but pointing toward visitors.

4. **Consider Using a Wireless Button**: For more flexibility, you can use a wireless remote button module instead of a wired button.

5. **Multiple Effects**: Consider connecting multiple outputs (lights, sounds, motors) for a coordinated scare effect when the button is pressed.
