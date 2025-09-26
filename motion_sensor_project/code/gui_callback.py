# This file is used to communicate between the GUI and the main program
# It provides a way for the GUI to call the button_pressed function in main.py

# The callback function will be set by main.py
button_callback = None

def register_callback(callback_function):
    """Register the callback function from main.py"""
    global button_callback
    button_callback = callback_function
    print("GUI callback registered successfully")
