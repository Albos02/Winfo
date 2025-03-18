import os
import json
from customtkinter import CTk, CTkToplevel, CTkButton, CTkFrame, CTkLabel, CTkOptionMenu, CTkImage
from tkinter import filedialog
from PIL import Image
from winfo_constants import *
def dump_preferences():
    global preferences
    with open('preferences.json', 'w') as f:
        json.dump(preferences, f)
# from winfo_dump_preferences import dump_preferences

importable_directories = []
option_list = None
top_level = None

def start_importation_toplevel():
    def find_sibling_app_version():
        parent_dir = os.path.dirname(os.getcwd())
        for sibling in os.listdir(parent_dir):
            if sibling == os.path.basename(os.getcwd()) or 'Winfo' not in sibling:
                continue
                
            sibling_path = os.path.join(parent_dir, sibling)
            pref_path = os.path.join(sibling_path, 'preferences.json')
            if os.path.isdir(sibling_path) and os.path.exists(pref_path):
                importable_directories.append(f"{sibling} | {sibling_path}")

    def run_dialog():
        global importable_directories, option_list
        
        folder = filedialog.askdirectory(title="Select Folder to Search")
        if not folder:
            return
            
        if 'preferences.json' in os.listdir(folder):
            importable_directories.append(f"Selected Folder | {folder}")
            option_list.configure(values=importable_directories)
            option_list.set(f"Selected Folder | {folder}")
            return

    def import_preferences():
        global option_list, importation_bool
        
        choice = option_list.get()
        path = choice.split(" | ")[1]
        pref_path = os.path.join(path, 'preferences.json')
        
        try:
            with open(pref_path, 'r') as f:
                global preferences
                preferences = json.load(f)
                dump_preferences()
                # print(preferences)
                top_level.destroy()
                main_top_level.destroy()
                print('importation successful, toplevel destroyed')
                importation_bool = True
        except Exception as e:
            print(f"Error importing preferences: {e}")
    def cancel_importation():
        global importation_bool
        top_level.destroy()
        main_top_level.destroy()
        importation_bool = False
    def show_toplevel():
        global importable_directories, option_list, top_level
        
        if hasattr(main_top_level, 'toplevels') and any(toplevel.title() == "Import Preferences" for toplevel in main_top_level.toplevels):
            return

        importable_directories = []
        find_sibling_app_version()
        
        top_level = CTkToplevel(main_top_level)
        top_level.title("Import Preferences")
        top_level.grab_set()
        
        CTkLabel(top_level, text="Choose a Winfo app folder to import your preferences:", font=H3_FONT).pack(pady=10)

        select_frame = CTkFrame(top_level, fg_color='transparent')
        select_frame.pack(pady=10, padx=10)
        
        option_list = CTkOptionMenu(select_frame, values=importable_directories)
        if importable_directories:
            option_list.set(importable_directories[0])
        option_list.pack(padx=5, side='left')
        
        folder_img = Image.open('images/folder.png')
        folder_ctk_img = CTkImage(folder_img, size=(20, 20))
        CTkButton(select_frame, text="", width=10, command=run_dialog, image=folder_ctk_img).pack(padx=5, side='right')

        buttons_frame = CTkFrame(top_level, fg_color='transparent')
        buttons_frame.pack(pady=10)
        CTkButton(buttons_frame, text='Cancel', command=cancel_importation).pack(padx=10, side='left')
        CTkButton(buttons_frame, text='Import', command=import_preferences).pack(padx=10, side='right')

    global main_top_level
    main_top_level = CTkToplevel()
    main_top_level.title("Winfo Preferences")
    
    start_frame = CTkFrame(main_top_level, fg_color='transparent')
    start_frame.pack(pady=20)
    CTkButton(start_frame, text='Import Preferences', width=15, command=show_toplevel).pack(padx=10, side='left')
    CTkButton(start_frame, text='Start from new', width=15).pack(padx=10, side='right')
    
    # main_top_level.mainloop()
    main_top_level.wait_window()
    print('exiting importation_toplevel')
    return importation_bool, preferences