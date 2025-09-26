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
        self.root.title("Halloween Scare Control")
        self.root.attributes('-fullscreen', True)  # Fullscreen for TFT display
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set background color to dark
        self.root.configure(bg='black')
        
        # Create a frame to hold content
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a title
        title_font = tkfont.Font(family="Arial", size=36, weight="bold")
        self.title_label = tk.Label(
            self.main_frame, 
            text="HALLOWEEN SCARE CONTROL", 
            font=title_font,
            fg='orange',
            bg='black'
        )
        self.title_label.pack(pady=(50, 30))
        
        # Create a large button
        button_font = tkfont.Font(family="Arial", size=48, weight="bold")
        self.scare_button = tk.Button(
            self.main_frame,
            text="FEED THE BEAST",
            font=button_font,
            bg='darkred',
            fg='white',
            activebackground='red',
            activeforeground='white',
            height=3,
            width=15,
            relief=tk.RAISED,
            bd=8,
            command=self.on_button_press
        )
        self.scare_button.pack(pady=50)
        
        # Add a status label
        status_font = tkfont.Font(family="Arial", size=24)
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready to scare!",
            font=status_font,
            fg='green',
            bg='black'
        )
        self.status_label.pack(pady=30)
        
        # Add an exit button (smaller, in the corner)
        exit_button = tk.Button(
            self.root,
            text="X",
            font=("Arial", 16),
            bg='darkred',
            fg='white',
            width=3,
            height=1,
            command=self.exit_application
        )
        exit_button.place(x=screen_width-60, y=10)
        
        # Add keyboard shortcut to exit (Escape key)
        self.root.bind('<Escape>', lambda e: self.exit_application())
        
    def on_button_press(self):
        """Handle button press event"""
        if not self.button_active:
            return
            
        # Update UI to show button was pressed
        self.button_active = False
        self.scare_button.config(bg='red', text="SCARING...")
        self.status_label.config(text="Scare in progress!", fg='red')
        
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
        self.scare_button.config(bg='darkred', text="FEED THE BEAST")
        self.status_label.config(text="Ready to scare!", fg='green')
    
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

def run_gui(button_callback=None):
    """
    Run the GUI application
    
    Args:
        button_callback: Function to call when button is pressed
    """
    root = tk.Tk()
    app = HalloweenScareGUI(root, button_callback)
    root.mainloop()

if __name__ == "__main__":
    # When run directly, create a test callback
    def test_callback():
        print("Button pressed! This would trigger the Halloween scare.")
        time.sleep(2)
        print("Scare complete!")
    
    # Run the GUI with the test callback
    run_gui(test_callback)
