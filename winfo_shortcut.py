import keyboard, time
from winfo_import import reload_preferences, conversion_key_tkinter_keyboard, send_alert
from windows_toasts import *

def create_dict_shortcuts():
    shortcuts = {}
    try:
        preferences['notification']
        for station in list(preferences['notification']):
            if 'shortcut' in preferences['notification'][station]:
                shortcuts[station] = preferences['notification'][station]['shortcut']
    except:
        shortcuts = {}
    return shortcuts
def check_last_time_send_alert(station):
    current_time = time.time()
    try:
        last_time = last_time_station_sent[station]
    except:
        last_time = 0
    if current_time - last_time >= 2:
        last_time_station_sent[station] = current_time
        send_alert(station)
def add_new_hotkey(shortcut, station):
    new_shortcut = []
    if 'Control_L' in shortcut and 'Alt_R' in shortcut:
        new_shortcut.append('alt gr')
        shortcut.remove('Control_L').remove('Alt_R')
    for key in shortcut:
        if key != 'alt gr':
            key = conversion_key_tkinter_keyboard[key]
        new_shortcut.append(key)
    if new_shortcut != []:
        keyboard.add_hotkey('+'.join(new_shortcut), check_last_time_send_alert, args=[int(station)])

last_time_station_sent = {}
preferences = reload_preferences()
create_dict_shortcuts()
shortcuts = create_dict_shortcuts()
for station in shortcuts.keys():
    add_new_hotkey(shortcuts[station], station)

while True:
    preferences = reload_preferences()
    new_shortcuts = create_dict_shortcuts()
    if new_shortcuts != shortcuts:
        for station in new_shortcuts.keys():
            if station not in shortcuts.keys():
                add_new_hotkey(new_shortcuts[station], station)
                print('shortcut added', '+'.join(new_shortcuts[station]))
        shortcuts = new_shortcuts
    time.sleep(5)