#!/usr/bin/env python3
"""
GUI Interface for Halloween Scare System
Provides a touchscreen interface with a button that triggers the scare
"""
import os
import sys
import tkinter as tk
from tkinter import font as tkfont
import threading
import time

# Path to a callback file that will be imported by main.py
CALLBACK_PATH = None  # Will be set dynamically

class HalloweenScareGUI:
    def __init__(self, root, button_callback=None):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
            button_callback: Function to call when button is pressed
        """
        self.root = root
        self.button_callback = button_callback
        self.button_active = True  # To prevent multiple rapid presses
        self.cooldown_time = 3  # Seconds to wait before allowing another press
        
        # Configure the window
        self.root.title("Feed The Beast")
        self.root.attributes('-fullscreen', True)  # Fullscreen for TFT display
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set background color to dark
        self.root.configure(bg='black')
        
        # Create a frame to hold content
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add some padding at the top
        top_padding = tk.Frame(self.main_frame, height=50, bg='black')
        top_padding.pack(fill='x', pady=(30, 20))
        
        # Create a large button that fits the screen
        # Get screen width to calculate appropriate button size
        button_width = min(int(screen_width / 30), 15)  # Adjust width based on screen size
        
        # Adjust font size based on screen width
        font_size = min(int(screen_width / 25), 48)  # Cap at 48pt
        button_font = tkfont.Font(family="Arial", size=font_size, weight="bold")
        
        # Create button frame to center the button
        button_frame = tk.Frame(self.main_frame, bg='black')
        button_frame.pack(fill='x', pady=50)
        
        self.scare_button = tk.Button(
            button_frame,
            text="FEED BEAST",  # Shortened text to ensure it fits
            font=button_font,
            bg='darkred',
            fg='white',
            activebackground='red',
            activeforeground='white',
            height=3,
            width=button_width,
            relief=tk.RAISED,
            bd=8,
            command=self.on_button_press,
            wraplength=screen_width - 100  # Allow text to wrap if needed
        )
        self.scare_button.pack(expand=True, fill='both', padx=50)
        
        # Add a status label with size based on screen width
        status_font_size = min(int(screen_width / 40), 24)  # Cap at 24pt
        status_font = tkfont.Font(family="Arial", size=status_font_size)
        
        # Create a frame for the status label
        status_frame = tk.Frame(self.main_frame, bg='black')
        status_frame.pack(fill='x', pady=30)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to feed!",
            font=status_font,
            fg='green',
            bg='black',
            wraplength=screen_width - 100  # Allow text to wrap if needed
        )
        self.status_label.pack(expand=True)
        
        # No visible exit button - but add a hidden key sequence for developers
        # This requires pressing Ctrl+Alt+Q to exit (unlikely to be pressed accidentally)
        self.key_sequence = []
        self.root.bind('<KeyPress>', self._check_dev_exit_sequence)
        
    def on_button_press(self):
        """Handle button press event"""
        if not self.button_active:
            return
            
        # Update UI to show button was pressed
        self.button_active = False
        self.scare_button.config(bg='red', text="FEEDING...")
        self.status_label.config(text="Feeding in progress!", fg='red')
        
        # Call the callback function if provided
        if self.button_callback:
            # Run in a separate thread to keep UI responsive
            threading.Thread(target=self._trigger_callback).start()
        else:
            # If no callback, just simulate a button press
            print("GUI Button pressed! (No callback registered)")
            self._reset_button_after_delay()
    
    def _trigger_callback(self):
        """Trigger the callback and reset button after"""
        try:
            self.button_callback()
        except Exception as e:
            print(f"Error in button callback: {e}")
        finally:
            self._reset_button_after_delay()
    
    def _reset_button_after_delay(self):
        """Reset button after cooldown period"""
        time.sleep(self.cooldown_time)
        self.root.after(0, self._reset_button)
    
    def _reset_button(self):
        """Reset button to original state"""
        self.button_active = True
        self.scare_button.config(bg='darkred', text="FEED BEAST")
        self.status_label.config(text="Ready to feed!", fg='green')
    
    def _check_dev_exit_sequence(self, event):
        """Check for developer exit key sequence (Ctrl+Alt+Q)"""
        # Check if Ctrl and Alt are pressed
        ctrl = (event.state & 0x4) != 0  # Control key
        alt = (event.state & 0x8) != 0   # Alt key
        
        # If Ctrl+Alt+Q is pressed, exit the application
        if ctrl and alt and event.keysym == 'q':
            print("Developer exit sequence detected")
            self.exit_application()
    
    def exit_application(self):
        """Exit the application"""
        self.root.destroy()
        sys.exit(0)

def create_gui_callback_file(callback_file_path, button_callback_name):
    """
    Create a file that will be imported by main.py to get the GUI callback
    This allows the GUI to trigger the button_pressed function in main.py
    """
    with open(callback_file_path, 'w') as f:
        f.write(f"""# This file is auto-generated by gui_interface.py
# It provides a way for the GUI to call the button_pressed function in main.py

# The callback function will be set by main.py
{button_callback_name} = None

def register_callback(callback_function):
    \"\"\"Register the callback function from main.py\"\"\"
    global {button_callback_name}
    {button_callback_name} = callback_function
    print("GUI callback registered successfully")
""")

def is_display_available():
    """
    Check if a display server is available for GUI
    """
    import os
    
    # Check for DISPLAY environment variable
    if 'DISPLAY' not in os.environ:
        return False
    
    # Try to initialize Tk
    try:
        test_root = tk.Tk()
        test_root.destroy()
        return True
    except Exception:
        return False

def run_gui(button_callback=None):
    """
    Run the GUI application
    
    Args:
        button_callback: Function to call when button is pressed
        
    Returns:
        True if GUI was started successfully, False otherwise
    """
    # Check if display is available
    if not is_display_available():
        print("ERROR: No display available for GUI")
        print("To run the GUI, you need to:")
        print("  1. Run the program in a desktop environment, or")
        print("  2. Use SSH with X11 forwarding: ssh -X admin@yumpi")
        print("  3. Set DISPLAY environment variable: export DISPLAY=:0")
        print("Continuing without GUI...")
        return False
    
    try:
        root = tk.Tk()
        app = HalloweenScareGUI(root, button_callback)
        root.mainloop()
        return True
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Continuing without GUI...")
        return False

if __name__ == "__main__":
    # When run directly, create a test callback
    def test_callback():
        print("Button pressed! Feeding the beast...")
        time.sleep(2)
        print("Feeding complete!")
    
    # Run the GUI with the test callback
    run_gui(test_callback)
