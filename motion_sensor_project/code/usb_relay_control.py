#!/usr/bin/env python3
"""
USB Relay Control Module
Controls USB relay modules that use serial commands (CH340 chip)
"""
import time
import serial
import serial.tools.list_ports
import logging

# Set up custom logging with newlines
class NewlineFormatter(logging.Formatter):
    """Custom formatter that adds a newline before each message"""
    def format(self, record):
        record.msg = "\n" + str(record.msg)
        return super().format(record)

# Configure logger with custom formatter
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = NewlineFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # Remove the root logger handler to avoid duplicate messages
    logger.propagate = False

class USBRelay:
    """
    Controls a USB relay module using serial commands.
    Compatible with CH340 USB-to-serial chip based relays.
    
    Commands:
    - Turn ON: A0 01 01 A2 (hex)
    - Turn OFF: A0 01 00 A1 (hex)
    """
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """
        Initialize the USB relay controller.
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' or 'COM3'). 
                  If None, will attempt to auto-detect.
            baudrate: Baud rate for serial communication (default: 9600)
            timeout: Serial timeout in seconds (default: 1)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.is_on = False
        
        # Command bytes (hex)
        self.ON_COMMAND = bytes.fromhex('A0 01 01 A2')
        self.OFF_COMMAND = bytes.fromhex('A0 01 00 A1')
        
        # Try to connect to the relay
        self._connect()
    
    def _connect(self):
        """Connect to the USB relay device"""
        try:
            # If no port specified, try to find a CH340 device
            if self.port is None:
                self.port = self._find_ch340_port()
                if self.port is None:
                    logger.warning("No CH340 USB device found. USB relay will not be available.")
                    return False
            
            # Connect to the serial port
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            logger.info(f"Connected to USB relay on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to USB relay: {e}")
            self.serial = None
            return False
    
    def _find_ch340_port(self):
        """
        Attempt to find a CH340 USB-to-serial device
        Returns the port name if found, None otherwise
        """
        try:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                # Look for CH340 in the description
                if "CH340" in port.description or "ch340" in port.description.lower():
                    logger.info(f"Found CH340 device on port {port.device}")
                    return port.device
                
                # Some CH340 devices might be identified differently
                if "USB Serial" in port.description and "1a86:" in port.hwid.lower():
                    logger.info(f"Found possible CH340 device on port {port.device}")
                    return port.device
            
            # If no specific CH340 found, return the first USB serial device if available
            for port in ports:
                if "USB" in port.description and "Serial" in port.description:
                    logger.info(f"Found USB Serial device on port {port.device}")
                    return port.device
            
            return None
        except Exception as e:
            logger.error(f"Error finding CH340 device: {e}")
            return None
    
    def is_connected(self):
        """Check if connected to the USB relay"""
        return self.serial is not None and self.serial.is_open
    
    def turn_on(self):
        """Turn on the USB relay"""
        if not self.is_connected():
            if not self._connect():
                logger.error("Cannot turn on relay: Not connected")
                return False
        
        try:
            self.serial.write(self.ON_COMMAND)
            self.is_on = True
            logger.info("USB relay turned ON")
            return True
        except Exception as e:
            logger.error(f"Failed to turn on USB relay: {e}")
            return False
    
    def turn_off(self):
        """Turn off the USB relay"""
        if not self.is_connected():
            if not self._connect():
                logger.error("Cannot turn off relay: Not connected")
                return False
        
        try:
            self.serial.write(self.OFF_COMMAND)
            self.is_on = False
            logger.info("USB relay turned OFF")
            return True
        except Exception as e:
            logger.error(f"Failed to turn off USB relay: {e}")
            return False
    
    def pulse(self, duration=1.0):
        """
        Turn on the relay for a specified duration, then turn it off.
        
        Args:
            duration: Time in seconds to keep the relay on
        """
        if self.turn_on():
            time.sleep(duration)
            self.turn_off()
            return True
        return False
    
    def blink(self, count=3, on_time=0.5, off_time=0.5):
        """
        Blink the relay a specified number of times.
        
        Args:
            count: Number of blinks
            on_time: Time in seconds to keep the relay on during each blink
            off_time: Time in seconds to keep the relay off between blinks
        """
        for _ in range(count):
            self.turn_on()
            time.sleep(on_time)
            self.turn_off()
            if _ < count - 1:  # Don't wait after the last blink
                time.sleep(off_time)
        return True
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_connected():
            try:
                # Make sure relay is off before closing
                if self.is_on:
                    self.turn_off()
                
                self.serial.close()
                logger.info("USB relay connection closed")
            except Exception as e:
                logger.error(f"Error during USB relay cleanup: {e}")


# Test function
def test_usb_relay():
    """Test the USB relay functionality"""
    relay = USBRelay()
    
    if relay.is_connected():
        print("USB relay connected successfully")
        print("Testing relay...")
        
        print("Turning ON")
        relay.turn_on()
        time.sleep(2)
        
        print("Turning OFF")
        relay.turn_off()
        time.sleep(1)
        
        print("Pulsing")
        relay.pulse(1.0)
        time.sleep(1)
        
        print("Blinking")
        relay.blink(3, 0.3, 0.3)
        
        print("Test complete")
        relay.cleanup()
    else:
        print("Failed to connect to USB relay")

if __name__ == "__main__":
    test_usb_relay()
