# USB Relay Connection Diagram

## Overview

The USB relay provides an alternative to GPIO-controlled relays. It connects directly to a USB port on the Raspberry Pi and is controlled via serial commands.

## Connection Diagram

```
┌─────────────────┐                  ┌─────────────────┐
│                 │                  │                 │
│   Raspberry Pi  │      USB         │   USB Relay     │
│                 ├──────────────────┤                 │
│                 │                  │                 │
└─────────────────┘                  └───────┬─────────┘
                                             │
                                             │
                                     ┌───────┴─────────┐
                                     │                 │
                                     │  External       │
                                     │  Device         │
                                     │  (Prop, Light,  │
                                     │   Fog Machine)  │
                                     │                 │
                                     └─────────────────┘
```

## Hardware Requirements

1. Raspberry Pi with USB port
2. USB relay module with CH340 chip
3. USB cable (Type-A to appropriate connector for your relay)
4. External device to control (with appropriate power supply)

## Connection Steps

1. Connect the USB relay to any available USB port on the Raspberry Pi
2. Connect your external device to the relay terminals:
   - COM (Common) - Connect to your device's power supply
   - NO (Normally Open) - Connect to your device
   - NC (Normally Closed) - Leave disconnected unless you need reverse logic

## Software Configuration

The system will automatically detect the USB relay when connected. No additional configuration is required.

If you want to manually specify the USB port, you can edit `main.py`:

```python
# Find your USB port
python3 -c "import serial.tools.list_ports; print([port.device for port in serial.tools.list_ports.comports()])"

# Then use that port in main.py
output = CombinedOutputControl(output_type="usb_relay", usb_port="/dev/ttyUSB0")  # Replace with your port
```

## Testing

To test if your USB relay is working properly:

```bash
# Simple test
sudo python3 code/usb_relay_control.py

# Advanced test with options
sudo python3 code/test_output.py --usb
```

You should hear the relay click and see the LED on the relay module change state when the relay is activated.
