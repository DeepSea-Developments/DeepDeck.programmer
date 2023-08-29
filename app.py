import tkinter as tk
from tkinter import ttk, Canvas, messagebox, font
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import esptool
import sys, os
import requests
import webbrowser
from datetime import datetime


# ███████ ███████ ██████  ████████  ██████   ██████  ██      
# ██      ██      ██   ██    ██    ██    ██ ██    ██ ██      
# █████   ███████ ██████     ██    ██    ██ ██    ██ ██      
# ██           ██ ██         ██    ██    ██ ██    ██ ██      
# ███████ ███████ ██         ██     ██████   ██████  ███████ 
                                                           
def esp_erase_flash():
    command = ['--baud', '460800', 'erase_flash']
    print('Using command %s' % ' '.join(command))
    esptool.main(command)

def esp_write_flash(firmware_path):
    command = ['--baud', '460800', 'write_flash', '0x0', resource_path(firmware_path)]
    print('Using command %s' % ' '.join(command))
    esptool.main(command)                                                           

def open_release_url():
    webbrowser.open(deepdeck_release_info[version_combobox.current()]['html_url'])

def open_help_url():
    webbrowser.open("https://deepdeck.co/installer/")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

deepdeck_release_info = {}

def get_deepdeck_release_info():
    global deepdeck_release_info
    # Define the repository information
    owner = 'DeepSea-Developments'
    repo = 'DeepDeck.Ahuyama.fw'
    url = f'https://api.github.com/repos/{owner}/{repo}/releases'

    # Send the API request
    try:
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the response as JSON
            releases = response.json()
            deepdeck_release_info = releases
            return True
            
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while looking for updates")
        messagebox.showerror("Error accesing server", "Check internet connection or try again") 
    
    return False

def get_release_list():
    succesfull = get_deepdeck_release_info()
    if succesfull:
        version_list = []
        for release in deepdeck_release_info:
            version_list.append(release['tag_name'])
            # print(release['tag_name'])
        return version_list
    else:
        return []

#  █████  ██    ██ ██   ██ 
# ██   ██ ██    ██  ██ ██  
# ███████ ██    ██   ███   
# ██   ██ ██    ██  ██ ██  
# ██   ██  ██████  ██   ██ 
                         

# Load the emoji images
emoji_images = {
    "+1": Image.open(resource_path("assets/thumbs_up.png")),      
    "laugh": Image.open(resource_path("assets/smile.png")),    
    "hooray": Image.open(resource_path("assets/hooray.png")), 
    "heart": Image.open(resource_path("assets/heart.png")),        
    "rocket": Image.open(resource_path("assets/rocket.png")),      
    "eyes": Image.open(resource_path("assets/eyes.png"))           
}

# ████████ ██   ██ ██ ███    ██ ████████ ███████ ██████       █████  ██    ██ ██   ██ 
#    ██    ██  ██  ██ ████   ██    ██    ██      ██   ██     ██   ██ ██    ██  ██ ██  
#    ██    █████   ██ ██ ██  ██    ██    █████   ██████      ███████ ██    ██   ███   
#    ██    ██  ██  ██ ██  ██ ██    ██    ██      ██   ██     ██   ██ ██    ██  ██ ██  
#    ██    ██   ██ ██ ██   ████    ██    ███████ ██   ██     ██   ██  ██████  ██   ██ 


def on_version_selected(event):
    # print("-----------------------------------------------")
    # print(deepdeck_release_info[version_combobox.current()]['body'])
    # print(deepdeck_release_info[version_combobox.current()]['reactions']['total_count'])
    # print(deepdeck_release_info[version_combobox.current()]['name'])
    # print(deepdeck_release_info[version_combobox.current()]['html_url'])
    # print(release['assets'])


    release = deepdeck_release_info[version_combobox.current()]
    binary_json = {}
    for asset in deepdeck_release_info[version_combobox.current()]['assets']:
        if asset["name"].endswith(".bin"):
            binary_json = asset
            break
    
    # Convert string to datetime object
    datetime_obj = datetime.strptime(release["published_at"], "%Y-%m-%dT%H:%M:%SZ")
    # Format the datetime object as "May 11, 2023"
    formatted_date = datetime_obj.strftime("%B %d, %Y")

    # Format size to mega bytes"
    formatted_megabytes = "{:.2f} Mb".format(binary_json["size"] / 1048576)

    if 'reactions' in release:
        num_thumbs_up.set(str(release['reactions'].get("+1", 0)))
        num_smile.set(str(release['reactions'].get("laugh", 0)))
        num_hooray.set(str(release['reactions'].get("hooray", 0)))
        num_heart.set(str(release['reactions'].get("heart", 0)))
        num_rocket.set(str(release['reactions'].get("rocket", 0)))
        num_eyes.set(str(release['reactions'].get("eyes", 0)))
    else:
        num_thumbs_up.set("0")
        num_smile.set("0")
        num_hooray.set("0")
        num_heart.set("0")
        num_rocket.set("0")
        num_eyes.set("0")

    name_text.set(binary_json["name"])
    date_text.set(formatted_date)
    size_text.set(formatted_megabytes)
    down_num_text.set(binary_json["download_count"])


def on_program_button_click():
    program_and_erase(erase=False)

def on_program_erase_button_click():
    program_and_erase(erase=True)


def program_and_erase(erase=False):

    if erase:
        # Display a message to indicate the process has started
        progress_label.config(text="Erasing DeepDeck..")
        window.update_idletasks()  # Force an immediate update of the GUI
        try:
            esp_erase_flash()

            # Process completed successfully
            progress_label.config(text="DeepDeck memory erased.")
        except Exception as e:
            # An error occurred, display error message
            progress_label.config(text="Error while erasing occurred.")
            messagebox.showerror("Erasing Error", str(e))
            return
    
    # Display a message to indicate the process has started
    progress_label.config(text="Looking for binary...")
    window.update_idletasks()  # Force an immediate update of the GUI

    download_url = ""
    # print(deepdeck_release_info[version_combobox.current()]['assets'])
    for asset in deepdeck_release_info[version_combobox.current()]['assets']:
        if asset["name"].endswith(".bin"):
            download_url = asset["browser_download_url"]
            print(f"Valid binary found: {asset['name']}")
            break

    if download_url == "":
        # Display a message to indicate the process has started
        progress_label.config(text="Error while looking for binary.")
        messagebox.showerror("Binary not found", str(e))
        return

    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            # Save the asset to a file
            with open(resource_path('DeepDeck.bin'), 'wb') as file:
                file.write(response.content)
            print('Asset downloaded successfully.')
        else:
            print(f'Error downloading asset: {response.status_code}')
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while download binary")
        messagebox.showerror("Binary download error", "Check your internet connection and try again") 
        return

    # Display a message to indicate the process has started
    progress_label.config(text="Programming DeepDeck..")
    window.update_idletasks()  # Force an immediate update of the GUI 

    try:
        esp_write_flash(resource_path("DeepDeck.bin"))
        progress_label.config(text="DeepDeck Ready!")
        messagebox.showinfo("Program succesfull", "You can now close this program and start enjoying DeepDeck")
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while flashing occurred.")
        messagebox.showerror("Erasing Error", str(e))
        return

def on_erase_button_click():
    # Display a message to indicate the process has started
    progress_label.config(text="Erasing DeepDeck..")
    window.update_idletasks()  # Force an immediate update of the GUI
    
    try:
        esp_erase_flash()

        # Process completed successfully
        progress_label.config(text="DeepDeck memory erased.")
        messagebox.showinfo("Erase succesfull", "Memory erased succesfully")

    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while erasing occurred.")
        messagebox.showerror("Erasing Error", str(e))


def look_for_updates():
    progress_label.config(text="Looking for releases...")
    window.update_idletasks()  # Force an immediate update of the GUI

    new_values = get_release_list()
    if len(new_values) > 0:
        version_combobox['values'] = new_values
        version_combobox.current(0)

        # Enable button and combobox
        program_button.config(state="normal")
        program_erase_button.config(state="normal")
        version_combobox.config(state="readonly")
        name_label.config(state="normal")
        date_label.config(state="normal")
        size_label.config(state="normal")
        down_num_label.config(state="normal")
        name_entry.config(state="readonly")
        date_entry.config(state="readonly")
        size_entry.config(state="readonly")
        down_num_entry.config(state="readonly")

        url_button.config(state="normal")
        # body_button.config(state="normal")
        # Show reation emojis
        reactions_frame.grid(row=2, column=0,columnspan=4)
        progress_label.config(text="")

        on_version_selected("")    



# ████████ ██   ██ ██ ███    ██ ████████ ███████ ██████      ██    ██ ██ 
#    ██    ██  ██  ██ ████   ██    ██    ██      ██   ██     ██    ██ ██ 
#    ██    █████   ██ ██ ██  ██    ██    █████   ██████      ██    ██ ██ 
#    ██    ██  ██  ██ ██  ██ ██    ██    ██      ██   ██     ██    ██ ██ 
#    ██    ██   ██ ██ ██   ████    ██    ███████ ██   ██      ██████  ██ 
                                                                                                                   
                                                       
    
# Create the main window
window = ThemedTk(theme="breeze")
window.title("DeepDeck Programmer v0.51")

# Load the image
image = Image.open(resource_path("assets/background_3.png"))
new_width = 414
new_height = 262
image = image.resize((new_width, new_height), Image.LANCZOS)
background_image = ImageTk.PhotoImage(image)

# Create a canvas widget and display the background image
canvas = Canvas(window, width=new_width, height=new_height)
canvas.create_image(new_width // 2, 0, anchor='n', image=background_image)
canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)



# Add a label for the version selection
version_label = ttk.Label(window, text="DeepDeck firmware version:")
version_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)  # Use grid layout

# Create a dropdown list for version selection
version_combobox = ttk.Combobox(window, values=["Look for updates"], state="disable")
version_combobox.bind("<<ComboboxSelected>>", on_version_selected)
version_combobox.current(0)
version_combobox.grid(row=2, column=0, padx=20, pady=10)  # Use grid layout

# Add a button to search for releases
update_button = ttk.Button(window, text="Look for updates", command=look_for_updates)
update_button.grid(row=2, column=1, padx=10, pady=10)  # Use grid layout

# Add a button to get help
upload_button = ttk.Button(window, text="Help", command=open_help_url)
upload_button.grid(row=2, column=2, padx=20, pady=10)  # Use grid layout


# Create a frame for the release information section
release_frame = ttk.Frame(window, relief="groove", borderwidth=2)
release_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Add labels for the release information
name_label = ttk.Label(release_frame, text="Name:", state="disable")
name_label.grid(row=0, column=0, sticky="w")

date_label = ttk.Label(release_frame, text="Release date:", state="disable")
date_label.grid(row=0, column=2, sticky="w",padx=(20,0))

size_label = ttk.Label(release_frame, text="Size:", state="disable")
size_label.grid(row=1, column=0, sticky="w")

down_num_label = ttk.Label(release_frame, text="Times downloaded:", state="disable")
down_num_label.grid(row=1, column=2, sticky="w",padx=(20,0))

# Create non-editable text boxes for the release information
name_text = tk.StringVar()
name_entry = ttk.Entry(release_frame, textvariable=name_text, state="disable")
name_entry.grid(row=0, column=1, sticky="w")

date_text = tk.StringVar()
date_entry = ttk.Entry(release_frame, textvariable=date_text, state="disable")
date_entry.grid(row=0, column=3, sticky="w")

size_text = tk.StringVar()
size_entry = ttk.Entry(release_frame, textvariable=size_text, state="disable")
size_entry.grid(row=1, column=1, sticky="w")

# Create a label with a linked text
down_num_text = tk.StringVar()
down_num_entry = ttk.Entry(release_frame, textvariable=down_num_text, state="disable")
down_num_entry.grid(row=1, column=3, sticky="w")

# Add a button go to release website
url_button = ttk.Button(release_frame, text="Release website", command=open_release_url, state="disable")
url_button.grid(row=3, column=0, columnspan=4, padx=20, pady=10)  # Use grid layout

# # Add a button to read release info
# body_button = ttk.Button(release_frame, text="Release info", command=open_release_url,state="disable")
# body_button.grid(row=3, column=2, columnspan=2, padx=20, pady=10)  # Use grid layout

num_thumbs_up = tk.StringVar()
num_smile = tk.StringVar()
num_hooray = tk.StringVar()
num_heart = tk.StringVar()
num_rocket = tk.StringVar()
num_eyes = tk.StringVar()

reaction_array = [  num_thumbs_up,
                    num_smile,
                    num_hooray,
                    num_heart,
                    num_rocket,
                    num_eyes]

num_thumbs_up.set("0")
num_smile.set("0")
num_hooray.set("0")
num_heart.set("0")
num_rocket.set("0")
num_eyes.set("0")

reactions_frame = tk.Frame(release_frame)

# Create labels with emoji images
for i, reaction in enumerate(emoji_images):
    emoji_image = emoji_images[reaction].resize((20, 20))  # Resize the image if needed
    emoji_photo = ImageTk.PhotoImage(emoji_image)

    emoji_label = tk.Label(reactions_frame, image=emoji_photo)
    emoji_label.image = emoji_photo
    emoji_label.grid(row=0, column=i*2)

    num_reaction_label = tk.Label(reactions_frame, textvariable=reaction_array[i])
    num_reaction_label.grid(row=0, column=i*2+1,padx=(0,35), pady=10)

# Create a frame for DeepDeck programming options
esp_frame = ttk.Frame(window)
esp_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

# Add a button to initiate programming
program_button = ttk.Button(esp_frame, text="Program", command=on_program_button_click,state="disabled")
program_button.grid(row=0, column=0, padx=10, pady=10)  # Use grid layout

# Add a button to initiate programming
program_erase_button = ttk.Button(esp_frame, text="Erase and Program", command=on_program_erase_button_click, state="disabled")
program_erase_button.grid(row=0, column=1, padx=10, pady=10)  # Use grid layout

# Add a button to initiate programming
erase_button = ttk.Button(esp_frame, text="Erase", command=on_erase_button_click)
erase_button.grid(row=0, column=2, padx=10, pady=10)  # Use grid layout

# Add a label to display the progress or status
progress_label = ttk.Label(window, text="")
progress_label.grid(row=5, column=0, columnspan=3, sticky="e", padx=10, pady=(0, 10))

# Configure the resizing behavior of the main window
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
 
# Start the main event loop
window.mainloop()
