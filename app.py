import tkinter as tk
from tkinter import ttk, Canvas
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import esptool
import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def on_version_selected(event):
    selected_version = version_combobox.get()
    print(f"Selected version: {selected_version}")

def on_program_button_click():
    firmware_path = "assets/DeepDeck_single.bin"  # Replace with the path to your firmware binary file
    command = ['--baud', '460800', 'write_flash', '0x0', resource_path(firmware_path)]
    print('Using command %s' % ' '.join(command))
    esptool.main(command)

def on_erase_button_click():
    serial_port = serial_entry.get()
    print(f"Serial port: {serial_port}")
    command = ['--baud', '460800', 'erase_flash']
    print('Using command %s' % ' '.join(command))
    esptool.main(command)

    
# Create the main window
# window = tk.Tk()
window = ThemedTk(theme="breeze")
window.title("ESP Firmware Updater")

# image_path = os.path.join(bundle_dir, "background.png")
image = Image.open(resource_path("assets/background.png"))
background_image = ImageTk.PhotoImage(image)

# Create a canvas widget and display the background image
canvas = Canvas(window, width=image.width, height=image.height)
canvas.pack()
canvas.create_image(0, 0, image=background_image, anchor="nw")

# Add a label for the version selection
version_label = ttk.Label(window, text="Select Version:")
version_label.pack()

# Create a dropdown list for version selection
version_combobox = ttk.Combobox(window, values=["Version 1.0", "Version 1.1", "Version 1.2"])
version_combobox.bind("<<ComboboxSelected>>", on_version_selected)
version_combobox.pack()

# Add a label for the serial port entry
serial_label = ttk.Label(window, text="Serial Port:")
serial_label.pack()

# Create an entry field for the serial port
serial_entry = ttk.Entry(window)
serial_entry.pack()

# Add a button to initiate programming
program_button = ttk.Button(window, text="Program", command=on_program_button_click)
program_button.pack()

# Add a button to initiate programming
program_button = ttk.Button(window, text="Erase", command=on_erase_button_click)
program_button.pack()

# Start the main event loop
window.mainloop()
