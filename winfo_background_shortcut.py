import keyboard, json
from winfo import reload_preferences, create_file_to_send_alert
with open('conversion_key_tkinter_to_keyboard.json', 'r') as file:
    conversion_key_tkinter_keyboard = json.load(file)

'''
def send_alert_app_not_running(values):
    # print(coord_station_meteosuisse)
    print(values)
    #print(list(station_dict.values()).index(combobox.get()))

    newToast = Toast()
    print(coord_station_meteosuisse[values[0]-1])
    arrow = get_text_icon_arrow(float(values[4]))
    try:
        newToast.text_fields = [coord_station_meteosuisse[values[0]-1][3], f'{values[2]} / {values[3]}  {preferences["wind_speed_unit"]}', f'{values[4]}° {arrow}']
    except KeyError:
        newToast.text_fields = ['Veuillez selectionner une station', 'pour obtenir les données']
    newToast.on_activated = launch_customtkinter #lambda _:[launch_customtkinter(), print('Launching customtkinter')]
    WindowsToaster('Winfo').show_toast(newToast)
    #toast(' + '.join(shortcut), on_click=lambda e:[checkmark_img_label.pack()]) #des problèmes de crash ou il bloque sur la commande => windows-toasts
def waiting_for_key(key):
    keyboard.wait(key)
    waiting_for_key(key)
def send_alert_by_shortcut(station):
    print(station)
    with open('VQHA80.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        station_data_dict = dict(list(reader)[station-1])
        values = [station, station_data_dict['Station/Location'], round(float(station_data_dict['fu3010z0']), 1), round(float(station_data_dict['fu3010z1']), 1), int(float(station_data_dict['dkl010z0']))]
        send_alert_app_not_running(values)
        '''
preferences = reload_preferences()
shortcuts = {}
try:
    preferences['notification']
    for station in list(preferences['notification']):
        if 'shortcut' in preferences['notification'][station]:
            shortcuts[station] = preferences['notification'][station]['shortcut']
except:
    shortcuts = {}
for station in shortcuts.keys():
    shortcut = shortcuts[station]
    #if control left et alt droite = alt gr
    new_shortcut = []
    if 'Control_L' in shortcut and 'Alt_R' in shortcut:
        new_shortcut.append('alt gr')
        # shortcut = shortcut.replace('Control_L', 'alt gr')
        shortcut.remove('Control_L').remove('Alt_R')

    for key in shortcut:
        if key != 'alt gr':
            key = conversion_key_tkinter_keyboard[key]
        new_shortcut.append(key)
    print(new_shortcut)
    if new_shortcut != []:
        # # hotkey_pressed = True
        # # for key in new_shortcut:
        # #     if keyboard.is_pressed(key):
        # #         print('key pressed', key)
        # #     else:
        # #         hotkey_pressed = False
        # # if hotkey_pressed:
        # #     create_file_to_send_alert(station)
        # #     print('hotkey pressed', new_shortcut)
        keyboard.add_hotkey('+'.join(new_shortcut), create_file_to_send_alert, args=[int(station)])

        # waiting_for_key(shortcut)
while True:
    pass