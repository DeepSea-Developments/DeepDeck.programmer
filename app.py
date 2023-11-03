import tkinter as tk
from tkinter import Menu, ttk, Canvas, messagebox, font, filedialog
from tkinter.messagebox import askyesno
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import esptool
import sys, os
import requests
import webbrowser
from datetime import datetime
import csv

# Titles generated with https://patorjk.com//software/taag/ with font ANSI regular

# ██    ██  █████  ██████  ██  █████  ██████  ██      ███████ ███████ 
# ██    ██ ██   ██ ██   ██ ██ ██   ██ ██   ██ ██      ██      ██      
# ██    ██ ███████ ██████  ██ ███████ ██████  ██      █████   ███████ 
#  ██  ██  ██   ██ ██   ██ ██ ██   ██ ██   ██ ██      ██           ██ 
#   ████   ██   ██ ██   ██ ██ ██   ██ ██████  ███████ ███████ ███████ 

deepdeck_release_info = {}

version = ""             # Variable to know the version downloaded and avoid redownloading the same version      
asset_list = {}         # List of assets used to flash esp32                                                                 

help_url = "https://deepdeck.co/en/QuickStartGuide/qsg-firmware-update/"
author_git_html = "https://deepdeck.co"                                                                

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

def esp_write_flash_advance(port,bin_dict):
    command = ['--baud', '460800', '--before', 'default_reset', '--after', 'hard_reset', 
               'write_flash', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect']
    # command = ['--baud', '460800', 'write_flash', '--flash_mode', 'dio', '--flash_size', 'detect']
    
    for bin in bin_dict:
        command.append(bin['memory'])
        command.append(resource_path(bin['file']))
    
    if port:
        port_command = ['-p',port]
        command = port_command + command
    
    print('Using command %s' % ' '.join(command))
    esptool.main(command)

def esp_read_all_flash(folder):
    file = folder + "/DeepDeck_download.bin"
    command = ['--baud', '460800', '--before', 'default_reset', '--after', 'hard_reset',
               'read_flash', '0x0', '0x400000', file]
    print('Using command %s' % ' '.join(command))
    esptool.main(command) 

        

def open_release_url():
    webbrowser.open(deepdeck_release_info[version_combobox.current()]['html_url'])

def open_help_url():
    webbrowser.open(help_url)
    
def open_author_url():
    webbrowser.open(author_git_html)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


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
    global deepdeck_release_info
    succesfull = get_deepdeck_release_info()
    curated_releases = []
    if succesfull:
        version_list = []
        for release in deepdeck_release_info:
            # Validate tag compatibility, and prerelease
            if release['prerelease'] == True:
                if prerelease.get():
                    version_list.append("BETA " + release['tag_name'])
                    curated_releases.append(release)
            else:
                version_list.append(release['tag_name'])
                curated_releases.append(release)
        
        deepdeck_release_info = curated_releases
            
                
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

def download_asset(download_url,asset_name):
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            # Save the asset to a file
            with open(resource_path(asset_name), 'wb') as file:
                file.write(response.content)
            print(f'{asset_name} downloaded successfully.')
        else:
            print(f'Error downloading asset: {response.status_code}')
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while download binary")
        messagebox.showerror("Binary download error", "Check your internet connection and try again") 
        return

# ████████ ██   ██ ██ ███    ██ ████████ ███████ ██████       █████  ██    ██ ██   ██ 
#    ██    ██  ██  ██ ████   ██    ██    ██      ██   ██     ██   ██ ██    ██  ██ ██  
#    ██    █████   ██ ██ ██  ██    ██    █████   ██████      ███████ ██    ██   ███   
#    ██    ██  ██  ██ ██  ██ ██    ██    ██      ██   ██     ██   ██ ██    ██  ██ ██  
#    ██    ██   ██ ██ ██   ████    ██    ███████ ██   ██     ██   ██  ██████  ██   ██ 



def on_download_firmware():
    folder = None
    folder = filedialog.askdirectory(initialdir = ".", title = "Select folder to store DeepDeck_download.bin")
    if len(folder) == 0:
        print("Canceled")
        return
    
    progress_label.config(text="Reading DeepDeck memory. This can take a while...")
    window.update_idletasks()  # Force an immediate update of the GUI
    
    try:
        esp_read_all_flash(folder)
        # Process completed successfully
        progress_label.config(text="Firmware stored")
        messagebox.showinfo("Firmware download successfully", "File stored in" + folder)

    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while reading occurred.")
        messagebox.showerror("Reading memory error", str(e))

def on_upload_firmware():
    file = filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("binary files","*.bin"),("all files","*.*")))
    
    if len(file) == 0:
        print("Canceled")
        return

    print (file)

    
    progress_label.config(text="Programming DeepDeck. This can take a while...")
    window.update_idletasks()  # Force an immediate update of the GUI
    
    try:
        esp_write_flash(file)
        # Process completed successfully
        progress_label.config(text="Firmware updated!")
        messagebox.showinfo("Firmware uploaded succesfull", "yey!, memory programmed succesfully")

    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while programming occurred.")
        messagebox.showerror("flashing memory error", str(e))

def on_version_selected(event):

    global author_image
    global author_photo
    global author_git_html
    global asset_list
    
    global emoji_label
    global num_reaction_label
    
    programmer_found = False # This flag show if programmer.csv was found or not. It is vital for the usage of this verision of the software
    
    asset_list = []
    
    release = deepdeck_release_info[version_combobox.current()]
    
    partition_table = {}
    for asset in deepdeck_release_info[version_combobox.current()]['assets']:
        if asset["name"].endswith(".bin"):
            asset_list.append(asset)
            print(asset["name"])
            
        elif asset["name"] == "programmer.csv":
            print("Found partition table") 
            asset_list.append(asset)
            partition_table = asset
            programmer_found = True
    
    if programmer_found == False:
        program_button.config(state="disable") 
        program_erase_button.config(state="disable")
        # Display a message to indicate the process has started
        progress_label.config(text="Version not compatible")
        window.update_idletasks()  # Force an immediate update of the GUI
    else:
        program_button.config(state="normal") 
        program_erase_button.config(state="normal")
        progress_label.config(text="")
        window.update_idletasks()  # Force an immediate update of the GUI

    
    author_git_html = release["author"]["html_url"]
    
    # Convert string to datetime object
    datetime_obj = datetime.strptime(release["published_at"], "%Y-%m-%dT%H:%M:%SZ")
    # Format the datetime object as "May 11, 2023"
    formatted_date = datetime_obj.strftime("%B %d, %Y")

    # global emoji_label
    # global num_reaction_label

    if 'reactions' in release:
        reactions_frame.grid()
        # Thubms Up
        if release['reactions'].get("+1", 0) > 0:
            num_thumbs_up.set(str(release['reactions'].get("+1", 0)))
            emoji_label[0].grid()
            num_reaction_label[0].grid()
        else:
            emoji_label[0].grid_remove()
            num_reaction_label[0].grid_remove()
        
        # Laugh
        if release['reactions'].get("laugh", 0) > 0:
            num_smile.set(str(release['reactions'].get("laugh", 0)))
            emoji_label[1].grid()
            num_reaction_label[1].grid()
        else:
            emoji_label[1].grid_remove()
            num_reaction_label[1].grid_remove()
            
        # Hooray
        if release['reactions'].get("hooray", 0) > 0:
            num_hooray.set(str(release['reactions'].get("hooray", 0)))
            emoji_label[2].grid()
            num_reaction_label[2].grid()
        else:
            emoji_label[2].grid_remove()
            num_reaction_label[2].grid_remove()
            
        # <3
        if release['reactions'].get("heart", 0) > 0:
            num_heart.set(str(release['reactions'].get("heart", 0)))
            emoji_label[3].grid()
            num_reaction_label[3].grid()
        else:
            emoji_label[3].grid_remove()
            num_reaction_label[3].grid_remove()
        
        # Rocket
        if release['reactions'].get("rocket", 0) > 0:
            num_rocket.set(str(release['reactions'].get("rocket", 0)))
            emoji_label[4].grid()
            num_reaction_label[4].grid()
        else:
            emoji_label[4].grid_remove()
            num_reaction_label[4].grid_remove()
        
        # Eyes
        if release['reactions'].get("eyes", 0) > 0:
            num_eyes.set(str(release['reactions'].get("eyes", 0)))
            emoji_label[5].grid()
            num_reaction_label[5].grid()
        else:
            emoji_label[5].grid_remove()
            num_reaction_label[5].grid_remove()
            
        
    else:
        reactions_frame.grid_remove()
        # num_thumbs_up.set("0")
        # num_smile.set("0")
        # num_hooray.set("0")
        # num_heart.set("0")
        # num_rocket.set("0")
        # num_eyes.set("0")

    author_name_text.set(release["author"]["login"])
    date_text.set(formatted_date)
    down_num_text.set(asset_list[0]["download_count"])
    
    # Show author image
    try:
        response = requests.get(release["author"]["avatar_url"])
        if response.status_code == 200:
            # Save the asset to a file
            with open(resource_path('author_avatar.jpg'), 'wb') as file:
                file.write(response.content)
            # print('Author Image downloaded successfully.')
        else:
            print(f'Error downloading image: {response.status_code}')
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while download binary")
        messagebox.showerror("Binary download error", "Check your internet connection and try again") 
        return
    # print(resource_path("author.jpeg"))
    
    author_image = Image.open(resource_path("author_avatar.jpg")).resize((100, 100)) # resize image 
    author_photo = ImageTk.PhotoImage(author_image)
    author_label.config(image=author_photo, state="normal")


def on_program_button_click():
    program_and_erase(erase=False)

def on_program_erase_button_click():
    
    answer = askyesno(title= 'Do you want to erase and program?',
                    message= "This action will erase the whole DeepDeck memory including any setting or layer modified \n\n Do you want to proceed?")
    
    if not(answer):
        return
    
    program_and_erase(erase=True)


def program_and_erase(erase=False):
    
    global asset_list
    global version
    
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

    # Verify if asset was already downloaded for this version
    if version == version_combobox.current():
        print("Assets already downloaded. Skip step")
    else:
        print("Downloading assets")
        for asset in asset_list:
            download_asset(asset["browser_download_url"],asset['name'])
        version = version_combobox.current()

    binary_dict_list = []
    with open(resource_path('programmer.csv'), newline='') as csvfile:
        binary_dict = csv.DictReader(csvfile)
        for row in binary_dict:
            binary_dict_list.append(row)
            print(row)
    
    # Display a message to indicate the process has started
    progress_label.config(text="Programming DeepDeck..")
    window.update_idletasks()  # Force an immediate update of the GUI 
    
    port = None
    if advance_mode.get():
        port = port_text.get()
        print(port)
    try:
        esp_write_flash_advance(port,binary_dict_list)
        # esp_write_flash(resource_path("DeepDeck.bin"))
        progress_label.config(text="DeepDeck Ready!")
        messagebox.showinfo("Program succesfull", "You can now close this program and start enjoying DeepDeck")
    except Exception as e:
        # An error occurred, display error message
        progress_label.config(text="Error while flashing occurred.")
        messagebox.showerror("Erasing Error", str(e))
        return

def on_erase_button_click():
    
    answer = askyesno(title= 'Do you want to erase the whole memory?',
                    message= "This action will erase the whole DeepDeck memory including any setting or layer modified \n\n Do you want to proceed?")
    
    if not(answer):
        return
    
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
        date_label.config(state="normal")
        down_num_label.config(state="normal")
        author_name_label.config(state="normal")
        date_entry.config(state="readonly")
        down_num_entry.config(state="readonly")
        author_name_entry.config(state="readonly")

        url_button.config(state="normal")
        # body_button.config(state="normal")
        
        # Show reation emojis
        # reactions_frame.grid(row=3, column=0,columnspan=4)
        progress_label.config(text="")

        on_version_selected("")    

def toggle_advance_mode():
    if advance_mode.get():
        inside_advanced_frame.grid()
    else:
        inside_advanced_frame.grid_remove()


# ████████ ██   ██ ██ ███    ██ ████████ ███████ ██████      ██    ██ ██ 
#    ██    ██  ██  ██ ████   ██    ██    ██      ██   ██     ██    ██ ██ 
#    ██    █████   ██ ██ ██  ██    ██    █████   ██████      ██    ██ ██ 
#    ██    ██  ██  ██ ██  ██ ██    ██    ██      ██   ██     ██    ██ ██ 
#    ██    ██   ██ ██ ██   ████    ██    ███████ ██   ██      ██████  ██ 
                                                                                                                   
                                                       
    
# Create the main window
window = ThemedTk(theme="breeze")
window.title("DeepDeck Programmer v0.6.0")

# Load the image
image = Image.open(resource_path("assets/background_3.png"))
new_width = 414
new_height = 242
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

# Add a Checkbox to allow beta releases
prerelease =  tk.IntVar()    
beta_checkbox = ttk.Checkbutton(window, text="Include Prereleases", variable = prerelease)
beta_checkbox.grid(row=2, column=2, padx=10, pady=10)  # Use grid layout

# # Add a button to get help
# upload_button = ttk.Button(window, text="Help", command=open_help_url)
# upload_button.grid(row=2, column=2, padx=20, pady=10)  # Use grid layout


# Create a frame for the release information section
release_frame = ttk.Frame(window, relief="groove", borderwidth=2)
release_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Add labels for the release information

date_label = ttk.Label(release_frame, text="Release date:", state="disable")
date_label.grid(row=0, column=1, sticky="w",padx=(20,0))


down_num_label = ttk.Label(release_frame, text="Times downloaded:", state="disable")
down_num_label.grid(row=1, column=1, sticky="w",padx=(20,0))

author_name_label = ttk.Label(release_frame, text="Author:", state="disable")
author_name_label.grid(row=2, column=1, sticky="w",padx=(20,0))

# Create non-editable text boxes for the release information

date_text = tk.StringVar()
date_entry = ttk.Entry(release_frame, textvariable=date_text, state="disable")
date_entry.grid(row=0, column=3, sticky="w")

# Create a label with a linked text
down_num_text = tk.StringVar()
down_num_entry = ttk.Entry(release_frame, textvariable=down_num_text, state="disable")
down_num_entry.grid(row=1, column=3, sticky="w")

author_name_text = tk.StringVar()
author_name_entry = ttk.Entry(release_frame, textvariable=author_name_text, state="disable")
author_name_entry.grid(row=2, column=3, sticky="w")

# Add a button go to release website
url_button = ttk.Button(release_frame, text="See more info about this release", command=open_release_url, state="disable")
url_button.grid(row=3, column=0, columnspan=4, padx=20, pady=10)  # Use grid layout

# Author photo
author_label = tk.Button(release_frame, state="disabled", command=open_author_url)
author_label.grid(row=0, column=0, rowspan = 3, padx=20, pady=10)
author_image = Image.open(resource_path("assets/author.png")).resize((100, 100)) # resieze image if needed
author_photo = ImageTk.PhotoImage(author_image)
author_label.config(image=author_photo)

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
reactions_frame.grid(row=4, column=0,columnspan=4)
reactions_frame.grid_remove()

emoji_label = []
num_reaction_label = []

# Create labels with emoji images
for i, reaction in enumerate(emoji_images):
    emoji_image = emoji_images[reaction].resize((20, 20))  # Resize the image if needed
    emoji_photo = ImageTk.PhotoImage(emoji_image)

    emoji_label.append(tk.Label(reactions_frame, image=emoji_photo))
    emoji_label[i].image = emoji_photo
    emoji_label[i].grid(row=0, column=i*2)

    num_reaction_label.append(tk.Label(reactions_frame, textvariable=reaction_array[i]))
    num_reaction_label[i].grid(row=0, column=i*2+1,padx=(0,35), pady=10)

# Create a frame for advance options
advanced_frame = ttk.Frame(window)
advanced_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

advance_mode =  tk.IntVar()    
advanced_mode_checkbox = ttk.Checkbutton(advanced_frame, text="Advanced mode", variable = advance_mode, command=toggle_advance_mode)
advanced_mode_checkbox.grid(row=0, column=0, padx=10, pady=10)  # Use grid layout

# Create a frame for  inside advance options
inside_advanced_frame = ttk.Frame(advanced_frame)
inside_advanced_frame.grid(row=1, column=0, padx=10, pady=5)
inside_advanced_frame.grid_remove()

port_label = ttk.Label(inside_advanced_frame, text="Port:")
port_label.grid(row=0, column=0, sticky="w",padx=(20,0))

port_text = tk.StringVar()
port_entry = ttk.Entry(inside_advanced_frame, textvariable=port_text)
port_entry.grid(row=0, column=1, sticky="w")

# Add a button to initiate programming
download_button = ttk.Button(inside_advanced_frame, text="Dowload firmware form DeepDeck", command=on_download_firmware)
download_button.grid(row=1, column=0, columnspan=2,padx=10, pady=10)  # Use grid layout

# Add a button to initiate programming
upload_button = ttk.Button(inside_advanced_frame, text="Upload firmware to DeepDeck", command=on_upload_firmware)
upload_button.grid(row=1, column=2, columnspan=2, padx=10, pady=10)  # Use grid layout

# Add a button to initiate programming
erase_button = ttk.Button(inside_advanced_frame, text="Erase", command=on_erase_button_click)
erase_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Use grid layout


# Create a frame for DeepDeck programming options
esp_frame = ttk.Frame(window)
esp_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

# Add a button to initiate programming
program_button = ttk.Button(esp_frame, text="Program", command=on_program_button_click,state="disabled")
program_button.grid(row=0, column=0, padx=10, pady=10)  # Use grid layout

# Add a button to initiate programming
program_erase_button = ttk.Button(esp_frame, text="Erase and Program", command=on_program_erase_button_click, state="disabled")
program_erase_button.grid(row=0, column=1, padx=10, pady=10)  # Use grid layout

# Add a button to get help
help_button = ttk.Button(esp_frame, text="Help", command=open_help_url)
help_button.grid(row=0, column=3, padx=10, pady=10)  # Use grid layout

# Add a label to display the progress or status
progress_label = ttk.Label(window, text="")
progress_label.grid(row=6, column=0, columnspan=3, sticky="e", padx=10, pady=(0, 10))

# Configure the resizing behavior of the main window
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
 
# Start the main event loop
window.mainloop()
