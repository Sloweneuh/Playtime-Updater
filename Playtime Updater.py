import os
import winreg
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

# Read playtime value from registry
def read_playtime_from_registry(registry_path):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, "CollapseLauncher_Playtime")
        if isinstance(value, str):
            return int(value, 16)
        else:
            return int(value)
    except FileNotFoundError:
        print(f"Registry key or value not found: {registry_path}\\CollapseLauncher_Playtime")
    except Exception as e:
        print(f"Error reading registry: {e}")
    return 0

# Read playtime value from text file
def read_playtime_from_text_file(file_line, file_path):
    try:
        if not os.path.exists(file_path):
            open(file_path, "w").close()
                
        with open(file_path, "r") as f:
            lines = f.readlines()
            if len(lines) <= file_line:
                return 0
            else:
                return int(lines[file_line])
    except Exception as e:
        print(f"Error reading playtime.txt: {e}")

# Save playtime value to text file
def save_playtime_to_text_file(value, line, file_path):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            if len(lines) <= line:
                lines.extend(["0\n"] * (line - len(lines) + 1))
            lines[line] = str(value) + "\n"
        with open(file_path, "w") as f:
            f.writelines(lines)
        print("Successfully wrote to playtime.txt")
    except Exception as e:
        print(f"Error writing to playtime.txt: {e}")

# Save playtime value to registry
def save_playtime_to_registry(registry_path, value):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, "CollapseLauncher_Playtime", 0, winreg.REG_DWORD, value)
        print(f"Successfully saved playtime to registry: {value}")
    except Exception as e:
        print(f"Error saving playtime to registry: {e}")

# Convert playtime value to hours and minutes for display purposes
def convert_playtime(value):
    hours = value // 3600
    minutes = (value % 3600) // 60
    return f"{hours}h {minutes}m"

# Update playtime values based on selected source
def update_playtime():
    for game_name, registry_path, file_line in games:
        selected_var = selected_vars[game_name].get()
        
        if selected_var == 1:  # Registry selected
            playtime_value = read_playtime_from_registry(registry_path)
            save_playtime_to_text_file(playtime_value, file_line, file_path)
            print(f"Saved playtime value to text file for {game_name}.")
        elif selected_var == 2:  # Text File selected
            playtime_value = read_playtime_from_text_file(file_line, file_path)
            save_playtime_to_registry(registry_path, playtime_value)
            print(f"Saved playtime value to registry for {game_name}.")
        else: # No selection
            print(f"No option selected for {game_name}.")
            continue
    
    refresh_radiobuttons()
    messagebox.showinfo("Update Complete", "Playtime values have been updated.")

# Change the theme of the application
def change_theme():
    if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
        # Set light theme
        root.tk.call("set_theme", "light")
        theme_button.config(text="🌙")
    else:
        # Set dark theme
        root.tk.call("set_theme", "dark")
        theme_button.config(text="☀")

# Refresh radiobuttons with updated playtime values
def refresh_radiobuttons():
    for game_name, registry_path, file_line in games:
        playtime_value = read_playtime_from_registry(registry_path)
        text_playtime_value = read_playtime_from_text_file(file_line, file_path)

        # Update the text of the radiobuttons
        registry_radiobuttons[game_name].config(text=f"Playtime on registry : {convert_playtime(playtime_value)}")
        text_radiobuttons[game_name].config(text=f"Playtime on text file : {convert_playtime(text_playtime_value)}")

        # Set the color of the radiobuttons based on playtime values
        if playtime_value > text_playtime_value:
            registry_radiobuttons[game_name].config(style="Green.TRadiobutton")
            text_radiobuttons[game_name].config(style="")
        elif text_playtime_value > playtime_value:
            text_radiobuttons[game_name].config(style="Green.TRadiobutton")
            registry_radiobuttons[game_name].config(style="")
        else:
            registry_radiobuttons[game_name].config(style="")
            text_radiobuttons[game_name].config(style="")

# Get the file path from a text file
def get_file_path():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as f:
            if (file_path := f.readline()):
                return file_path
            return ""
    else:
        open("config.txt", "w").close()

# Save the file path to a text file
def save_file_path(file_path):
    with open("config.txt", "w") as f:
        f.write(file_path)

# Select a file path for playtime values
def select_file_path():
    global file_path
    path = filedialog.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__)), title="Select a file", filetypes=(("text files", "*.txt"), ("all files", "*.*")))
    if path:
        file_path_label.config(text=f"File path : {path}")
        save_file_path(path)
        file_path = path
        refresh_radiobuttons()

# Check if registry keys exist
def check_registry_keys(registry_path):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, "CollapseLauncher_Playtime")
    except FileNotFoundError:
        print(f"Registry key not found: {registry_path}")
        return False
    return True

# Creater game list
def create_game_list():
    games = []

    if check_registry_keys(genshin_registry_path):
        games.append(("Genshin Impact", genshin_registry_path, 0))
    if check_registry_keys(starrail_registry_path):
        games.append(("Honkai Star Rail", starrail_registry_path, 1))
    if check_registry_keys(zzz_registry_path):
        games.append(("Zenless Zone Zero", zzz_registry_path, 2))
    if check_registry_keys(honkai_registry_path):
        games.append(("Honkai Impact 3rd", honkai_registry_path, 3))
    return games

# Registry paths
genshin_registry_path = r"Software\miHoYo\Genshin Impact"
starrail_registry_path = r"Software\Cognosphere\Star Rail"
zzz_registry_path = r"Software\miHoYo\ZenlessZoneZero"
honkai_registry_path = r"Software\miHoYo\Honkai Impact 3rd"

# Create a file path selection
file_path = get_file_path()
script_dir = os.path.dirname(os.path.abspath(__file__))
_file_path_ = os.path.join(script_dir, "playtime.txt")
if not file_path or not os.path.exists(file_path):
    file_path = _file_path_
    save_file_path(file_path)

# Create the main window
root = tk.Tk()
root.title("Collapse Launcher Playtime Updater")
root.resizable(False, False)
root.iconbitmap("icon.ico")

# Load the custom theme
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "dark")

# Create a frame to add padding
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.grid(row=0, column=0, sticky="nsew")

# Create custom styles
style = ttk.Style()
style.configure("Green.TRadiobutton", foreground="green")

# Initialize the list of games
games = create_game_list()

# Dictionary to store IntVars and Radiobuttons for each game
selected_vars = {}
registry_radiobuttons = {}
text_radiobuttons = {}

for i, (game_name, registry_path, file_line) in enumerate(games):
    playtime_value = read_playtime_from_registry(registry_path)
    text_playtime_value = read_playtime_from_text_file(file_line, file_path)

    # Create a label for the game
    game_label = ttk.Label(main_frame, text=f"{game_name} :", font=("", 12, "bold"))
    game_label.grid(row=i*3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    # Create an IntVar for the radiobuttons and store it in the dictionary
    selected_var = tk.IntVar(value=0)
    selected_vars[game_name] = selected_var

    # Create a radiobutton for the game's registry playtime
    registry_radiobutton = ttk.Radiobutton(main_frame, text=f"Playtime on registry : {convert_playtime(playtime_value)}", variable=selected_var, value=1)
    registry_radiobutton.grid(row=i*3+1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    registry_radiobuttons[game_name] = registry_radiobutton

    # Create a radiobutton for the game's text file playtime
    text_radiobutton = ttk.Radiobutton(main_frame, text=f"Playtime on text file : {convert_playtime(text_playtime_value)}", variable=selected_var, value=2)
    text_radiobutton.grid(row=i*3+2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    text_radiobuttons[game_name] = text_radiobutton

    # Set the initial color of the radiobuttons based on playtime values
    if playtime_value > text_playtime_value:
        registry_radiobutton.config(style="Green.TRadiobutton")
    elif text_playtime_value > playtime_value:
        text_radiobutton.config(style="Green.TRadiobutton")


# Create a label and button to select a file path
file_path_label = ttk.Label(main_frame, text=f"File path : {file_path}")
file_path_label.grid(row=len(games)*3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
file_path_button = ttk.Button(main_frame, text="...", width = 3, command=lambda: select_file_path())
file_path_button.grid(row=len(games)*3, column=2, sticky="w", padx=5, pady=5)

# Create a button to update playtime
update_button = ttk.Button(main_frame, text="Update Playtime", style="Accent.TButton", command=update_playtime)
update_button.grid(row=len(games)*3+1, column=0, columnspan=2, pady=20, padx=5)

# Create a button to display instructions
help_button = ttk.Button(main_frame, text="?", width=2, command=lambda: messagebox.showinfo("Instructions", "Only games that were launched at least once via Collapse Launcher will be displayed.\n\nYou can select where the file storing playtime will be located.\n\nSelect the source of playtime data for each game.\nThe higher value will be displayed in green.\n\nClick 'Update Playtime' to save the selected data source.\nNothing will be changed if no option is selected."))
help_button.grid(row=len(games)*3+1, column=2, pady=20, padx=5)

# Create a button to change the theme
theme_button = ttk.Button(main_frame, text="☀", width=3, command=change_theme)
theme_button.grid(row=len(games)*3+1, column=3, pady=20, padx=5)

# Run the application
root.mainloop()