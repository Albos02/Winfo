from customtkinter import *
from CTkTable import CTkTable
import tkintermapview
import requests, urllib.request, csv, json, webbrowser
import geocoder
from math import sqrt
from winfo_import import *

from windows_toasts import Toast, WindowsToaster, ToastDisplayImage
from PIL import Image
from PIL import ImageTk
from cosmo_parser import cosmo_parser

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def new_version_top_level():
    def top_level_focus():
            toplevel.focus_set()
            toplevel.after(5000, top_level_focus)
    global toplevel
    toplevel = CTkToplevel(window)
    toplevel.title('Nouvelle version de Winfo disponible !')
    toplevel.geometry('500x400+1900+300')
    toplevel.grid_columnconfigure(0, weight=1)
    toplevel.grid_rowconfigure(3, weight=1)

    CTkLabel(toplevel, text="Nouvelle version disponible !", font=h1_font).grid(row=0, column=0, padx=20, pady=(40,20), sticky="ew")
    CTkLabel(toplevel, text=f'La dernière version est {LATEST_VERSION}', font=h2_font).grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    if LATEST_VERSION_INFO != '':
        CTkLabel(toplevel, text="Améliorations :", font=h2_font).grid(row=2, column=0, padx=20, pady=(20,5), sticky="w")
        CTkLabel(toplevel, text=LATEST_VERSION_INFO, font=h2_font, justify="left", wraplength=460).grid(row=3, column=0, padx=20, pady=5, sticky="nw")

    button_frame = CTkFrame(toplevel, fg_color="transparent")
    button_frame.grid(row=4, column=0, pady=(20,20), sticky="ew")
    button_frame.grid_columnconfigure((0,1), weight=1)

    CTkButton(button_frame, text="Télécharger", command=open_new_version).grid(row=0, column=0, padx=10, sticky="e")
    CTkButton(button_frame, text='Ne plus afficher', command=ne_plus_afficher).grid(row=0, column=1, padx=10, sticky="w")

    toplevel.after(500, top_level_focus)

def open_new_version():
    webbrowser.open("https://louse-proud-raven.ngrok-free.app/versions/")
    toplevel.destroy()
def ne_plus_afficher():
    toplevel.destroy()
    reload_preferences()
    preferences['not_show_update'] = True
    dump_preferences()
def button1_pressed():
    map_frame.pack_forget()
    settings_scrollable_frame.pack_forget()
    button1.configure(fg_color=BUTTON_PRESSED_COLOR)
    button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    reload_preferences()
    if 'favorites' in preferences.keys():
        if len(preferences['favorites']) > 0:
            table_frame_setup(pack=True, fav_bool=True, wind_sorted=True)
        else: table_frame_setup(pack=True, fav_bool=False, wind_sorted=False)
    else: table_frame_setup(pack=True, fav_bool=False, wind_sorted=False)

def button2_pressed():
    table_frame.pack_forget()
    settings_scrollable_frame.pack_forget()
    button2.configure(fg_color=BUTTON_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    map_frame_setup(pack=True, displaying_values=True)

def button3_pressed():
    table_frame.pack_forget()
    map_frame.pack_forget()
    button3.configure(fg_color=BUTTON_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    settings_frame_setup(pack=True)
def get_csv():
    global latest_date
    try:
        urllib.request.urlretrieve(URL_VQHA80, "VQHA80.csv")
        with open("VQHA80.csv", "r") as fichier_csv:
            reader = csv.DictReader(fichier_csv, delimiter=';')
            date = list(reader)[0]['Date']
            if date != latest_date:
                update_all_values()
                latest_date = date
    except Exception as error:
        create_errored_file(error)
    window.after(10000, get_csv)

def update_all_values():
    print('updating values... new ones are here !!!')
    if map_active:
        map_frame_setup(True, displaying_values=True)
        return
    elif fav_active:
        table_frame_setup(pack=True, fav_bool=True, wind_sorted=wind_sorted_btn_activated)
        return
    elif all_station_active:
        table_frame_setup(pack=True, fav_bool=False, wind_sorted=wind_sorted_btn_activated)
        return
    elif settings_active:
        print("updating values.. but in settings so idk what to do...")
        return
    elif station_frame_active:
        station_frame_setup(pack=True, station_id=station_id_active)
        return
    else:
        print('no page displayed yet')

def change_theme(theme):
    print('theme is ' + theme)
    global active_theme
    if theme == "Système":
        theme = "System"
    elif theme == "Sombre":
        theme = "Dark"
    elif theme == "Clair":
        theme = "Light"
    print(f'theme changed to {theme}')
    set_appearance_mode(theme)
    preferences['theme'] = theme
    dump_preferences()
    active_theme = theme

def display_loading(root):
    global loading_img_label
    loading_img_label = CTkLabel(root, text='Chargement...', font=('roboto mono', 30))
    loading_img_label.pack(expand=True, fill='both')

def change_default_tile_server(tile_server):
    reload_preferences()
    preferences['map_tile_server'] = tile_server
    dump_preferences()
def change_tile_server(tile_server):
    print('change_tile_server --> ', tile_server)
    if tile_server == 'Swisstopo':
        tile_server = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg'
    elif tile_server == 'Swisstopo Satellite':
        tile_server = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg'
    elif tile_server == 'Cadastre Maptiler':
        tile_server = 'https://api.maptiler.com/maps/cadastre/256/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' #cadastre maptile 256x256 
    elif tile_server == 'Streets Maptiler':
        tile_server = 'https://api.maptiler.com/maps/streets-v2/256/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' #maptileropenstreets-v2 256x256 
    elif tile_server == 'OpenStreetMap':
        tile_server = 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png' #openstreetmap #default
    elif tile_server == 'Google':
        tile_server = 'https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga' # google
    elif tile_server == 'Google Earth':
        tile_server = 'https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga'# google earth
    map_widget.set_tile_server(tile_server)
def find_station_data_in_data_geo_files(abr: str):
    try:
        urllib.request.urlretrieve(URL_WIND_SPEED, "ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv")
        urllib.request.urlretrieve(URL_WIND_GUST, "ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv")
    except:
        with open('ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv', 'w') as f:
            f.write('')
        with open('ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv', 'w') as f:
            f.write('')
    try:
        with open('ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv', 'r') as f:
            reader_moyenne = csv.DictReader(f, delimiter=';')
            content_moyenne = list(reader_moyenne)
    except:
        content_moyenne = []
    try:
        with open('ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv', 'r') as f:
            reader_rafale = csv.DictReader(f, delimiter=';')
            content_rafale = list(reader_rafale)
    except:
        content_rafale = []
    for i, line in enumerate(content_moyenne):
        if line['Abr.'] == abr:
            for j in content_moyenne[i].keys():
                if 'Direction du vent' in j:
                    try:
                        direction = int(360-float(content_moyenne[i][j]))
                        break
                    except:
                        direction = None
            try:
                moyenne = round(float(content_moyenne[i]['Vent km/h']) * wind_speed_coef, 1)
            except ValueError:
                moyenne = '-'
            try:
                rafale = round(float(content_rafale[i]['Rafale km/h']) * wind_speed_coef, 1)
            except ValueError:
                rafale = '-'
            if direction is None:
                try:
                    direction = int(360-float(content_rafale[i]['Direction du vent']))
                except KeyError:
                    direction = None
            break
    try:
        direction
    except:
        direction = None
    try:
        moyenne
        if moyenne == '-':
            moyenne = None
    except:
        moyenne = None
    try:
        rafale
        if rafale == '-':
            rafale = None
    except:
        rafale = None
    return direction, moyenne, rafale
def map_frame_setup(pack: bool, displaying_values : bool):
    global map_frame, map_widget, map_active, fav_active, all_station_active, settings_active, station_frame_active
    try:
        map_frame.pack_forget()
    except:
        pass
    try:
        station_frame.pack_forget()
    except: pass
    map_frame = CTkFrame(window)
    def display_values():
        map_frame_setup(pack=True, displaying_values=display_values_switch.get())

    if pack:
        map_frame.pack(fill='both', expand=True, padx=20, pady=10)
        map_options_frame = CTkFrame(map_frame, bg_color='transparent', fg_color='transparent')
        map_options_frame.pack(fill="x", expand=False, padx=10, pady=0)
        titre_carte = CTkLabel(map_options_frame, text="Carte des Stations", font=h1_font)
        titre_carte.pack(pady=20)
        display_loading(map_frame)
        map_widget = tkintermapview.TkinterMapView(map_frame, width=1000, height=700, corner_radius=20)
        display_values_switch = CTkSwitch(map_options_frame, text="Afficher les valeurs", command=display_values)
        if displaying_values:
            display_values_switch.select()
        else:
            display_values_switch.deselect()
        display_values_switch.pack(side=LEFT, padx=10, pady=10)
        try:
            CTkLabel(map_options_frame, text=f"Unité : {preferences['wind_speed_unit']}", bg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=100).pack(side=LEFT, padx=40, pady=10)
        except:
            CTkLabel(map_options_frame, text=f'Unité : km/h', bg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=100).pack(side=LEFT, padx=40, pady=10)

        tile_server_option_menu = CTkOptionMenu(map_options_frame, values=MAP_TILE_SERVER_LIST, command=change_tile_server)
        tile_server_option_menu.pack(side=RIGHT, padx=10, pady=10)
        try:
            reload_preferences()
            tile_server_option_menu.set(preferences['map_tile_server'])
            change_tile_server(preferences['map_tile_server'])
        except:
            tile_server_option_menu.set('OpenStreetMap')

        with open('coord_station_meteosuisse.json', 'r') as f:
            coord = json.load(f)
        with open("VQHA80.csv", "r") as f_csv:
            reader = csv.DictReader(f_csv, delimiter=';')
            VQHA80 = []

            count = 0
            for _ in coord:
                count += 1
            for ligne in reader:
                if ligne['Station/Location'] in abreviation_list:
                    VQHA80.append(ligne)
                else:
                    print(ligne)
            print('len(VQHA80) = ', count, 'len(coord) = ', len(coord))
        for ligne, coor in zip(VQHA80, coord):
            if ligne['Station/Location'] == 'MRP':
                continue
            if ligne['Station/Location'] == coor[0]:
                print(ligne['Station/Location'], coor[0], ligne['fu3010z0'])
            else:
                print(ligne['Station/Location'], coor[0], ligne['fu3010z0'], '----'*2)
            try:
                direction = int(-float(ligne['dkl010z0']))
            except:
                direction = None
            try:
                moyenne, rafale = round(float(ligne['fu3010z0']) * wind_speed_coef, 1), round(float(ligne['fu3010z1']) * wind_speed_coef, 1)
            except ValueError:
                moyenne, rafale = None, None
            if direction is None and moyenne is None and rafale is None:
                direction, moyenne, rafale = find_station_data_in_data_geo_files(abr=coor[0])
            if direction is None or moyenne is None or rafale is None:
                if direction is None:
                    direction = 0
                if rafale is None or moyenne is None:
                    moyenne = '-'
                    rafale = '-'

            vent = str(moyenne) + '/' + str(rafale)
            if moyenne == '-' and rafale == '-':
                new_image = Image.open('images/cross.png')
                icon = ImageTk.PhotoImage(new_image.resize((15, 15)))
            else:
                new_image = set_icon(moyenne, rafale)
                icon = ImageTk.PhotoImage(new_image.rotate(direction).resize((25, 25)))
            if not displaying_values:
                vent = ''
            def setting_the_marker(coor_, vent_, icon_):
                id = coor_[5]
                map_widget.set_marker(float(coor_[1]), float(coor_[2]), text=vent_, text_color="black", icon=icon_, command=lambda _:[station_frame_setup(pack=True, station_id=id)])
            setting_the_marker(coor, vent, icon)

        map_widget.set_position(float(LOCATION_COORDINATES[0]), float(LOCATION_COORDINATES[1]))
        map_widget.set_zoom(9)#7
        loading_img_label.pack_forget()
        map_widget.pack(fill="both", expand=True, padx=10)
        print('all packed up')
        map_active = True
        station_frame_active, fav_active, all_station_active, settings_active = False, False, False, False


def changed_wind_sorted():
    global wind_sorted_btn_activated
    if fav_active:
        fav_bool_ = True
    else: fav_bool_ = False
    if alphabetical_sort_box.get() == 0:
        table_frame_setup(pack=True, fav_bool=fav_bool_, wind_sorted=True)
        wind_sorted_btn_activated = True
    else:
        table_frame_setup(pack=True, fav_bool=fav_bool_, wind_sorted=False)
        wind_sorted_btn_activated = False

def calculate_distance(pos_lat, pos_lon, station_lat, station_lon):
    pos_lat, pos_lon, station_lat, station_lon = float(pos_lat), float(pos_lon), float(station_lat), float(station_lon)
    distance = sqrt(((pos_lat - station_lat) ** 2) + ((pos_lon - station_lon) ** 2))
    output = round(distance * 91.8855029586, 5)
    return output
def get_station_matrix(fav_bool: bool, wind_sorted: bool):
    already_direction = False
    with open("VQHA80.csv", "r") as f_csv:
        reader = csv.DictReader(f_csv, delimiter=';')
        values = []
        search_input = search_entry.get().lower()
        reload_preferences()
        with open("coord_station_meteosuisse.json", "r") as f_json:
            coord_reader = json.load(f_json)
            print(LOCATION_COORDINATES[0], '|', LOCATION_COORDINATES[1])
            for ligne, coord in zip(reader, coord_reader):
                if ligne['Station/Location'] == 'MRP':
                    continue
                distance = calculate_distance(LOCATION_COORDINATES[0], LOCATION_COORDINATES[1], coord[1], coord[2])
                try:
                    if distance > preferences['distance_slider'] and not preferences['distance_slider'] == 500:
                        continue
                except KeyError:
                    pass
                try:
                    if fav_bool and coord[5] in preferences['favorites']:
                        pass
                    elif fav_bool and not coord[5] in preferences['favorites']:
                        continue
                except KeyError:
                    continue
                if search_input == '' or search_input in coord[3].lower() or search_input in coord[0].lower():
                    pass
                else:
                    continue
                new_line = []
                new_line.append(coord[3])
                try:
                    vent, rafale = round(float(ligne['fu3010z0']) * wind_speed_coef, 1), round(float(ligne['fu3010z1']) * wind_speed_coef, 1)
                except ValueError:
                    direction, vent, rafale = find_station_data_in_data_geo_files(abr=coord[0])
                    print(direction, vent, rafale)
                    already_direction = True
                if vent is None or rafale is None:
                    vent, rafale = '-', '-'
                    new_line.append('')
                else:
                    if wind_speed_coef == 1:
                        new_line.append(f'{str(vent)} | {str(rafale)}  km/h')
                    else:
                        new_line.append(f'{str(vent)} | {str(rafale)}  noeuds')
                try:
                    if already_direction:
                        already_direction = False
                    else:
                        direction = int(float(ligne['dkl010z0']))
                    if direction <= 360-22.5 and direction >= 360/8*7-22.5: output = '⬊'
                    elif direction <= 360/8*7-22.5 and direction >= 360/8*6-22.5: output = '➞'
                    elif direction <= 360/8*6-22.5 and direction >= 360/8*5-22.5: output = '⬈'
                    elif direction <= 360/8*5-22.5 and direction >= 360/8*4-22.5: output = '⬆'
                    elif direction <= 360/8*4-22.5 and direction >= 360/8*3-22.5: output = '⬉'
                    elif direction <= 360/8*3-22.5 and direction >= 360/8*2-22.5: output = '⬅'
                    elif direction <= 360/8*2-22.5 and direction >= 360/8-22.5: output = '⬋'
                    elif (direction <= 360/8-22.5 or direction <= 360+360/8-22.5) and (direction >= 0-22.5 or direction >= 360-22.5): output = '⬇'
                    else: output = 'None'
                    new_line.append(f'{direction}°   {output}')
                except:
                    if 'error' in ligne['dkl010z0']:
                        new_line.append(ligne['dkl010z0'])
                    else:
                        new_line.append('')
                new_line.append(coord[4])
                if 'favorites' in preferences.keys():
                    if coord[5] in preferences['favorites']:
                        #new_line.append('v')
                        new_line.append('⬛')
                    else:
                        #new_line.append('x')
                        new_line.append('⬜')
                else:
                    #new_line.append('x')
                    new_line.append('⬜')
                values.append(new_line)
            if wind_sorted:
                values = sorted(values, key=lambda item_in_values: (-5 if item_in_values[1] == '' else float(item_in_values[1].split('|')[0])), reverse=True)
            values.insert(0, ['Station/Location', 'Vent / Rafale', 'Direction', 'Canton', 'Favoris'])
            return values

def set_segmented_btn(fav_bool: bool):
    global fav_or_all_btn
    fav_or_all_btn = CTkSegmentedButton(table_frame, values=['Favoris', 'Toutes les stations'], command=change_fav_or_all_from_segbtn)
    fav_or_all_btn.pack(pady=20)
    if fav_bool == True:
        fav_or_all_btn.set('Favoris')
    else:
        fav_or_all_btn.set('Toutes les stations')

def change_fav_or_all_from_segbtn(value):
    global search_input
    search_input = ''
    print(value)
    table_frame.pack_forget()
    if value == 'Favoris':
        table_frame_setup(pack=True, fav_bool=True, wind_sorted=wind_sorted_btn_activated)
        fav_or_all_btn.set('Favoris')
    if value == 'Toutes les stations':
        table_frame_setup(pack=True, fav_bool=False, wind_sorted=wind_sorted_btn_activated)

def search_in_table_T_T(e):
    global search_input
    search_input = search_entry.get()
    table_frame_setup(pack=True, fav_bool=True, wind_sorted=True)
def search_in_table_T_F(e):
    global search_input
    search_input = search_entry.get()
    table_frame_setup(pack=True, fav_bool=True, wind_sorted=False)
def search_in_table_F_T(e):
    global search_input
    search_input = search_entry.get()
    table_frame_setup(pack=True, fav_bool=False, wind_sorted=True)
def search_in_table_F_F(e):
    global search_input
    search_input = search_entry.get()
    table_frame_setup(pack=True, fav_bool=False, wind_sorted=False)
    
def empty_search(e): #called if backspace+ctrl is pressed and delete all the search
    global search_input
    text = search_entry.get()
    last_space = text.rstrip().rfind(' ')  # find the last space
    if last_space != -1:  # if there is a space
        search_entry.delete(last_space, END)
        search_input = search_entry.get()
    else:  # if there is only one word
        search_entry.delete(0, END)
        search_input = ''




def table_frame_setup(pack: bool, fav_bool: bool, wind_sorted: bool):
    global table_frame, table_frame_active, station_frame_active, map_active, settings_active, alphabetical_sort_box, table, fav_active, all_station_active, search_entry, entry_as_display
    try:
        table_frame.pack_forget()
    except:
        pass
    try:
        station_frame.pack_forget()
    except: pass
    table_frame = CTkFrame(window)
    if not pack:
        table_frame = CTkFrame(window)
        return
    else:
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
    if fav_bool:
        text = ['Favoris']
    else:
        text = ['Toutes les stations']
    CTkLabel(table_frame, text=text[0], font=h1_font).pack(pady=20)
    def setup_table_stations(e):
        global table
        try:
            table.destroy()
        except:
            pass
        table = CTkTable(scrollframe, values=get_station_matrix(fav_bool=fav_bool, wind_sorted=wind_sorted), header_color=BUTTON_NOT_PRESSED_COLOR, command=table_clicked)
        table.pack(expand=True, fill="both")
    def table_clicked(returns):
        row, column, value = returns['row'], returns['column'], returns['value']
        reload_preferences()
        if column == 0:
            station_name = table.get(row, 0)
            station_frame_setup(pack=True, station_id=station_dict[station_name])
        elif column == 4:
            if 'favorites' in preferences.keys():
                favoris = list(preferences['favorites'])
                if value == '⬜':
                    favoris.append(station_dict[table.get(row, 0)])
                    preferences['favorites'] = favoris
                    table.insert(row, column, '⬛')
                else:
                    favoris.remove(station_dict[table.get(row, 0)])
                    preferences['favorites'] = favoris
                    table.insert(row, column, '⬜')
                print(f'favoris = {favoris}')
            else:
                favoris = [station_dict[table.get(row, 0)]]
                preferences['favorites'] = favoris
                table.insert(row, column, '⬛')
            with open('preferences.json', 'w') as f:
                json.dump(preferences, f)

    def select_entry(event):
        entry_as_display.delete(0, 'end')
    def entry_as_display_changed(e):
        try:
            value = float(entry_as_display.get())
        except ValueError: # if a character is not a number, it takes all the numbers before the character
            count = 0
            for character in entry_as_display.get():
                try:
                    int(character)
                    if character == 'e':
                        break
                    count += 1
                except ValueError:
                    break
            value = float(entry_as_display.get()[:count])
        if value == int(value):
            value = int(value)
        entry_as_display.delete(0, 'end')
        if value == 500:
            entry_as_display.configure(placeholder_text=f'N/A KM')
        else:
            entry_as_display.configure(placeholder_text=f'{value} KM')
        distance_slider.set(value)
        distance_slider_and_search_frame.focus()
        preferences['distance_slider'] = value
        dump_preferences()
        setup_table_stations(None)
    def distance_slider_changed(value):
        value = int(round(value, -1))
        entry_as_display.delete(0, 'end')
        if value == 500:
            entry_as_display.configure(placeholder_text=f'N/A KM')
        else:
            entry_as_display.configure(placeholder_text=f'{value} KM')
        preferences['distance_slider'] = value
        dump_preferences()

    set_segmented_btn(fav_bool=fav_bool)
    alphabetical_sort_box = CTkCheckBox(table_frame, text="Ordre alphabétique", command=changed_wind_sorted)
    if not wind_sorted: alphabetical_sort_box.select()
    alphabetical_sort_box.pack()
    display_loading(table_frame)
    scrollframe = CTkScrollableFrame(table_frame)
    scrollframe.pack(expand=True, fill="both", padx=20, pady=20)
    distance_slider_and_search_frame = CTkFrame(scrollframe, fg_color='transparent')
    distance_slider_and_search_frame.pack(pady=10)
    if len(LOCATION) < 25:
        location_begining = LOCATION.upper()
    else:
        location_begining = LOCATION[0:23].upper() + '..'
    CTkLabel(distance_slider_and_search_frame, text=f"Rayon d'affichage autour de : {location_begining}", width=100).pack(side=LEFT, padx=10)
    entry_as_display = CTkEntry(distance_slider_and_search_frame, placeholder_text="", width=70)
    entry_as_display.bind('<Return>', entry_as_display_changed)
    entry_as_display.bind('<Button-1>', select_entry)
    reload_preferences()
    try:
        value = round(float(preferences['distance_slider']), 1)
    except KeyError:
        value = 500
    if value == int(value):
        value = int(value)
    if value == 500:
        entry_as_display.configure(placeholder_text=f'N/A KM')
    else:
        entry_as_display.configure(placeholder_text=f'{value} KM')
    entry_as_display.pack(padx=10, side=LEFT)
    distance_slider = CTkSlider(distance_slider_and_search_frame, from_=10, to=500, command=distance_slider_changed)
    distance_slider.set(value)
    distance_slider.bind("<ButtonRelease-1>", setup_table_stations)
    distance_slider.pack(padx=0, side=LEFT)
    CTkLabel(distance_slider_and_search_frame, text="", width=10).pack(side=LEFT, padx=20)
    search_entry = CTkEntry(distance_slider_and_search_frame, placeholder_text="Rechercher une station", width=200)
    search_entry.bind('<Control-BackSpace>', empty_search)
    if fav_bool:
        if wind_sorted:
            search_entry.bind("<Return>", search_in_table_T_T)
        else:
            search_entry.bind("<Return>", search_in_table_T_F)
    else:
        if wind_sorted:
            search_entry.bind("<Return>", search_in_table_F_T)
        else:
            search_entry.bind("<Return>", search_in_table_F_F)
    try:
        search_entry.insert(0, search_input)
        search_entry.focus()
    except NameError:
        pass
    search_entry.pack(padx=20, pady=20, side=RIGHT)
    setup_table_stations(None)
    loading_img_label.pack_forget()
    table_frame_active = True
    fav_active, all_station_active = False, False
    if fav_bool:
        fav_active = True
    else:
        all_station_active = True
    station_frame_active, map_active, settings_active = False, False, False
def get_active_wind(station_id: int):
    abr = coord_station_meteosuisse[station_id-1][0]
    with open('VQHA80.csv', 'r') as fichier_csv:
        reader = csv.DictReader(fichier_csv, delimiter=';')
        for row in reader:
            if row['Station/Location'] == abr:
                try:
                    moyenne = float(row['fu3010z0'])
                    rafale = float(row['fu3010z1'])
                except:
                    moyenne = 'N/A'
                    rafale = 'N/A'
                try:
                    direction = int(float(row['dkl010z0']))
                except:
                    direction = 'N/A'
                if moyenne == 'N/A' or rafale == 'N/A' or direction == 'N/A':
                    pass
                else:
                    info = [moyenne, rafale, direction]
                    return info
    direction, moyenne, rafale = find_station_data_in_data_geo_files(abr=abr)
    if direction is None: direction = 'N/A'
    if moyenne is None: moyenne = 'N/A'
    if rafale is None: rafale = 'N/A'
    return [moyenne, rafale, direction]
def get_history_matrix(station_id: int, raw: bool):
    if wind_speed_coef == 1:
        unit = ' km/h'
    else:
        unit = ' noeuds'
    abr = coord_station_meteosuisse[station_id-1][0]
    matrix = []
    urllib.request.urlretrieve(URL_HISTORY_MESUREMENT, 'mesurement_history.csv')
    with open('mesurement_history.csv', 'r') as fichier_csv:
        reader = csv.DictReader(fichier_csv, delimiter=',')
        for row in reader:
            # print(row)
            print(row['Date'], row[f'{abr}_moyenne'], row[f'{abr}_rafale'], row[f'{abr}_direction'], row[f'{abr}_temp'], row[f'{abr}_pluie'], row[f'{abr}_humidite'], row[f'{abr}_QFE'], row[f'{abr}_QFF'], row[f'{abr}_QNH'])
            hour, minute, date = strafe_date_from_csv(local_time=row['Date'])
            direction = row[f'{abr}_direction']
            try:
                arrow = get_text_icon_arrow(float(direction))
            except:
                arrow = ''


            try:
                wind = round(float(row[f'{abr}_moyenne'])*wind_speed_coef, 1)
            except:
                wind = row[f'{abr}_moyenne']
            try:
                wind_gusts = round(float(row[f'{abr}_rafale'])*wind_speed_coef, 1)
            except:
                wind_gusts = row[f'{abr}_rafale']
            try:
                direction = int(float(direction))
            except:
                pass
            if not raw:
                matrix.append([f'{date} {hour}h{minute}', f"{wind} | {wind_gusts} {unit}", f"{direction}° {arrow}"])
            else:
                matrix.append([f'{date[:-5]} {hour}h{minute}', wind, wind_gusts, direction])
    if not raw:
        matrix.append(['Date', 'Vent | Rafale', 'Direction'])
        matrix.reverse()
    return matrix
def get_prevision_matrix(station_id: int, raw: bool):
    abr = coord_station_meteosuisse[station_id][0]
    matrix = cosmo_parser(abr, wind_speed_coef=wind_speed_coef, raw=raw)
    return matrix



def chart_setup(frame, station_id, history_bool, unit: str):
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(left=0.06, right=0.94, bottom=0.2, top=0.97)
    
    ax2 = ax.twinx()
    
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel(f'Vitesse du vent ({unit})', fontsize=10)
    ax2.set_ylabel('Direction (°)', fontsize=10)
    ax2.grid(False)
    
    data = get_history_matrix(station_id, raw=True) if history_bool else get_prevision_matrix(station_id, raw=True)
    
    x_values = []
    y_values = [[], [], []]
    
    for row in data:
        x_values.append(row[0])
        for i in range(3):
            try:
                y_values[i].append(float(row[i + 1]))
            except ValueError:
                y_values[i].append(row[i + 1])
    
    x_numeric = list(range(len(x_values)))
    
    lines = []
    labels = []
    
    moyenne_line = ax.plot(x_numeric, y_values[0], label='Moyenne', linewidth=2.0)[0]
    lines.append(moyenne_line)
    labels.append('Moyenne')
    
    if history_bool:
        rafale_line = ax.plot(x_numeric, y_values[1], label='Rafale', linewidth=1.0)[0]
        lines.append(rafale_line)
        labels.append('Rafale')
        
        direction_line = ax2.plot(x_numeric, y_values[2], label='Direction', linewidth=0.5, color='red', linestyle='--')[0]
        lines.append(direction_line)
        labels.append('Direction')
        
        ax2.set_ylim(0, 360)
        ax2.set_yticks([0, 90, 180, 270, 360])
        ax2.tick_params(axis='y', which='both', length=0)
    else:
        fill_between = ax.fill_between(x_numeric, y_values[1], y_values[2], alpha=0.5, label='Min / Max')
        lines.append(fill_between)
        labels.append('Min / Max')

        ax2.set_ylabel('')
        ax2.set_visible(False)
    
    ax.legend(lines, labels, loc='best')
    
    if history_bool:
        tick_positions = list(range(len(x_values)-1, 1, -6))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([x_values[i] for i in tick_positions][::1], rotation=45, ha='right')
    else:
        ax.set_xticks(range(len(x_values)-1, -1, -1))
        ax.set_xticklabels(x_values[::-1], rotation=45, ha='right')
    
    if len(x_numeric) > 1:
        x_padding = (x_numeric[-1] - x_numeric[0]) * 0.01  # 5% padding on the x-ax
        ax.set_xlim(x_numeric[0] - x_padding, x_numeric[-1] + x_padding)

    # Create hover line
    hover_line = ax.axvline(x=0, color='gray', alpha=0.8, visible=False)
    hover_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                         bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'),
                         verticalalignment='top')
    
    def motion_notify_event(event):
        if event.inaxes in (ax, ax2) and event.xdata is not None and event.ydata is not None:
            idx = min(range(len(x_numeric)), key=lambda i: abs(x_numeric[i] - event.xdata))
            if history_bool:
                text = (f"Date: {x_values[idx]}\n"
                        f"Moyenne: {y_values[0][idx]:.1f}\n"
                        f"Rafale: {y_values[1][idx]:.1f}\n"
                        f"Direction: {y_values[2][idx]:.0f}°")
                main_ydata = ax.transData.inverted().transform((event.x, event.y))[1]
                if 3 > abs(main_ydata - y_values[0][idx]):
                    moyenne_line.set_linewidth(4.0)
                    rafale_line.set_linewidth(2.0)
                    direction_line.set_linewidth(0.5)
                elif 3 > abs(main_ydata - y_values[1][idx]):
                    rafale_line.set_linewidth(4.0)
                    moyenne_line.set_linewidth(2.0)
                    direction_line.set_linewidth(0.5)
                elif 20 > abs(event.ydata - y_values[2][idx]):
                    direction_line.set_linewidth(2.0)
                    moyenne_line.set_linewidth(2.0)
                    rafale_line.set_linewidth(2.0)
                else:
                    moyenne_line.set_linewidth(2.0)
                    rafale_line.set_linewidth(2.0)
                    direction_line.set_linewidth(0.5)
            else:
                text = (f"Date: {x_values[idx]}\n"
                        f"Moyenne: {y_values[0][idx]:.1f}\n"
                        f"Min: {y_values[1][idx]:.1f}\n"
                        f"Max: {y_values[2][idx]:.1f}")
                if 3 > abs(event.ydata - y_values[0][idx]):
                    moyenne_line.set_linewidth(4.0)
                else:
                    moyenne_line.set_linewidth(2.0)
            
            hover_line.set_xdata([x_numeric[idx]])
            hover_line.set_visible(True)
            hover_text.set_text(text)
            hover_text.set_visible(True)
        else:
            hover_line.set_visible(False)
            hover_text.set_visible(False)
            moyenne_line.set_linewidth(2.0)
            if history_bool:
                rafale_line.set_linewidth(2.0)
                direction_line.set_linewidth(0.5)
        
        fig.canvas.draw_idle()
    
    def handle_figure_leave(event):
        hover_line.set_visible(False)
        hover_text.set_visible(False)
        moyenne_line.set_linewidth(2.0)
        if history_bool:
            rafale_line.set_linewidth(2.0)        
            direction_line.set_linewidth(0.5)
        fig.canvas.draw_idle()
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(padx=20, pady=20, fill=BOTH, expand=True)
    
    canvas.mpl_connect('motion_notify_event', motion_notify_event)
    canvas.mpl_connect('figure_leave_event', handle_figure_leave)
    
    canvas_widget.figure = fig
    canvas_widget.canvas = canvas
    
    return canvas_widget
def station_frame_setup(pack: bool, station_id: int):
    global wind_speed_coef, station_id_active, station_frame, station_frame_active, table_frame, table_frame_active, map_active, settings_active, alphabetical_sort_box, table, fav_active, all_station_active, search_entry, entry_as_display
    station_id_active = station_id
    try:
        station_frame.pack_forget()
    except:
        pass
    try:
        table_frame.pack_forget()
    except: pass
    try:
        map_frame.pack_forget()
    except: pass
    try:
        settings_scrollable_frame.pack_forget()
    except: pass
    if not pack:
        station_frame = CTkScrollableFrame(window)

    else:
        station_frame = CTkScrollableFrame(window)
        station_frame.pack(fill='both', expand=True, padx=20, pady=20)
        station_name = reversed_station_dict[station_id]
        CTkLabel(station_frame, text=station_name, font=h1_font).pack(pady=20)
        display_loading(station_frame)

        button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)

        reload_preferences()
        if preferences['wind_speed_unit'] == 'km/h':
            wind_speed_coef = 1
            unit = 'km/h'
        else:
            wind_speed_coef = 1/1.852
            unit = 'noeuds'

        def show_history_table():
            nonlocal history_table_showed
            if not history_table_showed:
                table_history.pack(expand=True, fill="both", padx=20, pady=20)
                history_btn.configure(text='Toutes les données  ∧')
                history_table_showed = True
            else:
                table_history.pack_forget()
                history_btn.configure(text='Toutes les données  ∨')
                history_table_showed = False

        def show_prevision_table():
            nonlocal prevision_table_showed
            if not prevision_table_showed:
                table_prevision.pack(expand=True, fill="both", padx=20, pady=20)
                prevision_btn.configure(text='Toutes les données  ∧')
                prevision_table_showed = True
            else:
                table_prevision.pack_forget()
                prevision_btn.configure(text='Toutes les données  ∨')
                prevision_table_showed = False

        quick_info_frame = CTkFrame(station_frame, fg_color='transparent')
        quick_info_frame.pack(expand=True, fill="x", padx=20, pady=20)
        info = get_active_wind(station_id)
        print('Vent actuel : ', info)
        try:
            moyenne = round(info[0]*wind_speed_coef, 1)
            rafale = round(info[1]*wind_speed_coef, 1)
        except:
            moyenne, rafale = info[0], info[1]
        wind_label = CTkLabel(quick_info_frame, text=f"{moyenne} | {rafale} {unit}", font=h2_font)
        wind_label.pack(padx=10, side=LEFT)
        if info[2] != 'N/A':
            direction_content = f"{info[2]}°"# + get_text_icon_arrow(info[2])
            arrow_img = set_icon(info[0], info[1])
            try:
                arrow_img = arrow_img.rotate(-int(info[2]))
            except:
                pass


        else:
            direction_content = info[2]
            arrow_img = Image.open('images/cross.png')
        direction_label = CTkLabel(quick_info_frame, text=direction_content, font=h2_font)
        direction_label.pack(padx=10, side=LEFT)


        arrow_img = CTkImage(arrow_img, size=(80, 80))
        image_label = CTkLabel(quick_info_frame, text='', image=arrow_img)
        image_label.pack(padx=30, side=RIGHT)

        history_frame = CTkFrame(station_frame, fg_color='transparent')
        history_frame.pack(expand=True, fill="both", padx=20, pady=20)#, side=LEFT)
        prevision_frame = CTkFrame(station_frame, fg_color='transparent')
        prevision_frame.pack(expand=True, fill="both", padx=20, pady=20)#, side=RIGHT)

        CTkLabel(history_frame, text="Historique", font=h2_font).pack(pady=20)
        CTkLabel(prevision_frame, text="Previsions", font=h2_font).pack(pady=20)

        print('\nHistorique :')
        chart_setup(history_frame, station_id, True, unit=unit)
        history_table_showed = False
        table_history = CTkTable(history_frame, values=get_history_matrix(station_id, raw=False), header_color=BUTTON_NOT_PRESSED_COLOR)
        history_btn = CTkButton(history_frame, text='Toutes les données  ∨', command=show_history_table)
        history_btn.pack(pady=10)


        print('\nPrévisions :')
        chart_setup(prevision_frame, station_id, False, unit=unit)
        prevision_table_showed = False
        table_prevision = CTkTable(prevision_frame, values=get_prevision_matrix(station_id, raw=False), header_color=BUTTON_NOT_PRESSED_COLOR)
        prevision_btn = CTkButton(prevision_frame, text='Toutes les données  ∨', command=show_prevision_table)
        prevision_btn.pack(pady=10)

        loading_img_label.pack_forget()
        station_frame_active = True

        fav_active, all_station_active, table_frame_active, map_active, settings_active = False, False, False, False, False

def settings_frame_setup(pack:bool):
    global settings_scrollable_frame, alert_frame_dict, last_alert_frame, plus_button, station_frame_active, map_active, fav_active, all_station_active, settings_active, alert_horiz_scrollframe, alert_nonscroll_frame, frame_len, frame_id_list, station_to_add
    reload_preferences()
    try:
        settings_scrollable_frame.pack_forget()
    except:
        pass
    try:
        station_frame.pack_forget()
    except: pass
    settings_scrollable_frame = CTkScrollableFrame(window)
    if pack:
        alert_frame_dict = {}
        settings_scrollable_frame.pack(fill='both', expand=True, padx=20, pady=20)
        settings_title = CTkLabel(settings_scrollable_frame, text="Paramètres", font=h1_font)
        settings_title.pack(padx=20, pady=30)

        empty = True
        stations_to_add = []
        for i in range(1, 20):
            returns = get_station_which_frame_order_is_frame_id(i)
            if returns is not None:
                empty = False
                stations_to_add.append(returns)
        frame_id_list = []
        frame_len = 0

        last_alert_frame = 0
        right_plus_frame = CTkFrame(settings_scrollable_frame)
        right_plus_frame.pack(fill='x', expand=False)
        empty_img = CTkImage(light_image=Image.new('RGBA', (30, 30), (0, 0, 0, 0)), dark_image=Image.new('RGBA', (30, 30), (0, 0, 0, 0)), size=(30, 30))
        left_empty_frame = CTkButton(right_plus_frame, text='', image=empty_img, fg_color='transparent', hover=False)
        left_empty_frame.pack(side=LEFT)

        CTkLabel(right_plus_frame, text="Notifications", font=h2_font).pack(side=LEFT, expand=True, fill='x', padx=20)

        plus_image = CTkImage(light_image=Image.open('images/plus.png'), dark_image=Image.open('images/plus.png'), size=(30, 30))
        right_plus_icon_btn = CTkButton(right_plus_frame, text='', image=plus_image, fg_color='transparent', hover=False, command=add_alert_frame)
        right_plus_icon_btn.pack(side=RIGHT)
        frame_for_scroll_or_not_frame = CTkFrame(settings_scrollable_frame)
        frame_for_scroll_or_not_frame.pack(expand=True, fill='both')
        alert_horiz_scrollframe = CTkScrollableFrame(frame_for_scroll_or_not_frame, fg_color=(LIGHT_2, DARK_2), corner_radius=20, height=500, orientation='horizontal')#, border_color='red', border_width=1)#, ) #add transform to CTkScrollableFrame()   #fg_color=('#C0C0C0', '#333333')
        if empty:
            alert_nonscroll_frame = CTkFrame(frame_for_scroll_or_not_frame, fg_color=(LIGHT_2, DARK_2), corner_radius=20, height=500)
            alert_nonscroll_frame.pack(expand=True, fill='x', padx=20, pady=20)
            big_plus_image = CTkImage(light_image=Image.open('images/plus.png'), dark_image=Image.open('images/plus.png'), size=(200, 200))
            plus_button = CTkButton(alert_nonscroll_frame, text='', image=big_plus_image, fg_color='transparent', hover=False, command=add_alert_frame)
            plus_button.pack(anchor='center', pady=100)
        else:
            alert_horiz_scrollframe.pack(expand=True, fill='x', padx=20, pady=20)
            print('stations to add', stations_to_add)
            for station in stations_to_add:
                print(f'adding station Num{station}')
                add_alert_frame(station)
        def change_wind_speed_unit(e):
            global wind_speed_coef
            preferences['wind_speed_unit'] = e
            dump_preferences()
            if e == 'km/h':
                wind_speed_coef = 1
            elif e == 'noeuds':
                wind_speed_coef = 1/1.852
            print(wind_speed_coef)
            button3_pressed()

        def update_location(event):
            global LOCATION, LOCATION_COORDINATES
            search_term = location_entry.get()
            headers = {'User-Agent': f'Winfo/{CURRENT_VERSION} (winfo.projet@gmail.com)'}
            url_nominatim_OSM = f'https://nominatim.openstreetmap.org/search.php?q={search_term}&format=jsonv2'
            print(f'url {url_nominatim_OSM}')
            r = requests.get(url_nominatim_OSM, headers=headers)
            data = json.loads(r.text)

            print('---------------------')
            best_importance = 0
            for response in data:
                place_importance = response['importance']
                if place_importance > best_importance:
                    best_importance = place_importance
                print('----')

            print(f'best importance: {best_importance}')

            print(best_importance)
            if best_importance != 0:
                for response in data:
                    print(response['importance'], best_importance)
                    if response['importance'] == best_importance:
                        LOCATION = response['display_name']
                        print('to add', LOCATION)
                        LOCATION_COORDINATES = (response['lat'], response['lon'])
                        preferences['location'][0] = LOCATION
                        preferences['location'][1], preferences['location'][2] = LOCATION_COORDINATES
                        preferences['location'][3] = 'created_by_user'
                        dump_preferences()
                        location_entry.delete(0, END)
                        location_entry.insert(0, LOCATION)
                        break

            preferences['location'][0] = LOCATION
            preferences['location'][1], preferences['location'][2] = LOCATION_COORDINATES
            preferences['location'][3] = 'created_by_user'
            dump_preferences()

        def empty_location_entry(*e):
            location_entry.delete(0, END)
            '''
            text = location_entry.get()
            last_space = text.rstrip().rfind(' ')  # find the last space
            if last_space != -1:  # if there is a space
                location_entry.delete(last_space, END)
            else:  # if there is only one word
                location_entry.delete(0, END)
                '''
        wind_speed_unit_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        wind_speed_unit_frame.pack(pady=20)
        CTkLabel(wind_speed_unit_frame, text='Unité de mesure').pack(padx=10, side=LEFT)
        wind_speed_unit = CTkOptionMenu(wind_speed_unit_frame, values=['km/h', 'noeuds'], command=change_wind_speed_unit)
        try:
            global wind_speed_coef
            if preferences['wind_speed_unit'] == 'km/h':
                wind_speed_coef = 1
                wind_speed_unit.set('km/h')
            else:
                wind_speed_coef = 1/1.852
                wind_speed_unit.set('noeuds')
        except:
            pass
        wind_speed_unit.pack(padx=10, side=RIGHT)
        location_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        location_frame.pack(pady=20)
        CTkLabel(location_frame, text='Entrez votre localisation pour plus de précision').pack(padx=0, side=LEFT)
        CTkLabel(location_frame, text='', width=10).pack(padx=10, side=RIGHT)
        location_entry = CTkEntry(location_frame, placeholder_text='Lieu', width=250)
        location_entry.bind('<Return>', update_location)
        location_entry.bind('<Control-BackSpace>', empty_location_entry)
        location_entry.pack(padx=20, side=LEFT)
        bin_img = CTkImage(light_image=Image.open('images/bin.png'), dark_image=Image.open('images/bin.png'), size=(20, 20))
        CTkButton(location_frame, text='', image=bin_img, width=10, command=empty_location_entry).pack(side=RIGHT, padx=0)

        default_tile_server_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        default_tile_server_frame.pack(pady=20)
        CTkLabel(default_tile_server_frame, text='Tile server par defaut').pack(padx=10, side=LEFT)
        default_map_tile_server = CTkOptionMenu(default_tile_server_frame, values=MAP_TILE_SERVER_LIST, command=change_default_tile_server)
        default_map_tile_server.pack(padx=10, side=RIGHT)
        try:
            default_map_tile_server.set(preferences['map_tile_server'])
        except:
            pass
        theme_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        theme_frame.pack(pady=20)
        CTkLabel(theme_frame, text="Theme de l'application").pack(padx=10, side=LEFT)
        theme_color_option_menu = CTkOptionMenu(theme_frame, values=["Système", "Clair", "Sombre"], command=change_theme)
        try:
            if preferences['theme'] == 'System':
                theme_color_option_menu.set('Système')
            elif preferences['theme'] == 'Dark':
                theme_color_option_menu.set('Sombre')
            elif preferences['theme'] == 'Light':
                theme_color_option_menu.set('Clair')
        except:
            theme_color_option_menu.set('Système')
        theme_color_option_menu.pack(padx=10)
        CTkButton(settings_scrollable_frame, text='Accédez au site web', command=open_website).pack(padx=20, pady=20)
        CTkLabel(settings_scrollable_frame, text='Toutes les données affichées sont mises à disposition par MétéoSuisse').pack(pady=20)
        CTkLabel(settings_scrollable_frame, text=f"Version de l'application : {CURRENT_VERSION}").pack(pady=20)

        station_frame_active = False
        map_active = False
        fav_active = False
        all_station_active = False
        settings_active = True


def add_alert_frame(*args):
    global last_alert_frame, frame_len, frame_id_list
    alert_visible = None
    shortcut_visible = None
    try:
        plus_button.pack_forget()
    except:
        pass
    try:
        alert_nonscroll_frame.pack_forget()
    except:
        pass
    frame_len += 1
    frame_id_list.append(frame_len)
    frame_id = frame_len
    shortcut=[]

    def select_station_event(event):
        last_station = get_station_which_frame_order_is_frame_id(frame_id=frame_id)
        if last_station is not None:
            update_alert_preferences(last_station, 'all', 'remove')
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'frame_order', int(frame_id))
            try:
                if alert_visible:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(slider.get()/wind_speed_coef))
            except:
                pass
            try:
                if shortcut_visible:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'shortcut', shortcut)
            except:
                pass
        else:
            print('No station selected -> cannot save frame_order')
    def enable_alert(*initializing_bool):
        nonlocal alert_visible
        if alert_visible == None:
            alert_visible = False
        if alert_visible:
            alert_frame_1.pack_forget()
            alert_frame.configure(height=50)
            alert_visible = False
            if str(combobox.get()) in station_dict.keys():
                update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', 'remove')
            else:
                print('No station selected -> cannot remove wind limit')
            slider.set(25)
            value_entry.delete(0, 'end')
            if unit == 'km/h':
                value_entry.insert(0, '25  km/h')
            else:
                value_entry.insert(0, f'{int(25/1.852)}  noeuds')
        else:
            alert_frame_1.pack(expand=True, fill='both')
            alert_visible = True
            try:
                slider.set(round(preferences['notification'][str(station_dict[combobox.get()])]['wind_limit']*wind_speed_coef, 1))
                value_entry.delete(0, 'end')
                value_entry.insert(0, str(round(float(slider.get()), 1))+'  '+unit)
            except:
                pass
            if str(combobox.get()) in station_dict.keys():
                if not initializing_bool:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(slider.get()))
            else:
                print('No station selected -> cannot save wind limit')
    def enable_shortcut(*initializing_bool):
        nonlocal shortcut_visible
        if shortcut_visible == None:
            shortcut_visible = False
        if shortcut_visible:
            shortcut_frame_1.pack_forget()
            shortcut_frame.configure(height=50)
            if str(combobox.get()) in station_dict.keys():
                if not initializing_bool:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'shortcut', 'remove')
            else:
                print('No station selected -> cannot remove shortcut')
            entry.delete(0, 'end')
            shortcut_visible = False
        else:
            shortcut_frame_1.pack(expand=True, fill='both')
            shortcut_visible = True
    def select_entry(e):
        value_entry.delete(0, 'end')
    def entry_changed(e):
        try:
            value = float(value_entry.get())
        except ValueError: # if comma instead of dot
            try:
                value = int(value_entry.get().split(',')[0]) + float(value_entry.get().split(',')[1])/(10**len(value_entry.get().split(',')[1]))
            except:
                value = float('')
        value_entry.delete(0, 'end')
        if value == int(value):
            value_entry.insert(0, str(int(value))+'  '+unit)
        else:
            value_entry.insert(0, str(value)+'  '+unit)
        slider.set(int(value))
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', value/wind_speed_coef)
        else:
            print('No station selected -> cannot save wind limit')
        frame.focus()
    def slider_changed(event):
        print(int(event))
        value_entry.delete(0, 'end')
        value_entry.insert(0, str(int(slider.get()))+'  '+unit)
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(event/wind_speed_coef))
        else:
            print('No station selected -> cannot save wind limit')
    def shortcut_entry_entered(event):
        if event.keysym != 'Escape':
            if event.keysym not in shortcut:
                shortcut.append(event.keysym)
        else:
            for i in range(len(shortcut)):
                shortcut.pop(0)
        entry.delete(0, 'end')
        entry.insert(0, ' + '.join(shortcut))
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'shortcut', shortcut)
        else:
            print('No station selected -> cannot save shortcut')
    def send_alert():
        content, local_time = alert_content()

        hour, minute, date = strafe_date_from_csv(local_time=local_time)
        date = f"{hour}h{minute}  {date}"

        if wind_speed_coef == 1:
            unit = 'km/h'
        else:
            unit = 'noeuds'
        
        img = set_icon(float(content[station_dict[combobox.get()]][0].split('|')[0]), float(content[station_dict[combobox.get()]][0].split('|')[1]))
        img = img.resize((350, 350), Image.Resampling.HAMMING)
        img = img.rotate(-int(content[station_dict[combobox.get()]][1].split('°')[0]))

        background = Image.new('RGBA', (400, 400), (0, 0, 0, 0))  # larger transparent background
        position = ((background.width - img.width) // 2,
                (background.height - img.height) // 2)
        background.paste(img, position, img)
        background.save('wind_arrow_alert.png', 'PNG')

        newToast = Toast()
        newToast.AddImage(ToastDisplayImage.fromPath('wind_arrow_alert.png'))

        checkmark_img = CTkImage(light_image=Image.open('images/checkmark.png'), dark_image=Image.open('images/checkmark.png'), size=(20, 20))
        checkmark_img_label = CTkLabel(test_btn_frame, image=checkmark_img, text='')
        try:
            newToast.text_fields = [combobox.get(), content[station_dict[combobox.get()]][0] + unit + '     ' + date, content[station_dict[combobox.get()]][1]]
        except KeyError:
            newToast.text_fields = ['Veuillez selectionner une station', 'pour obtenir les données']
        newToast.on_activated = lambda _: checkmark_img_label.pack(side=LEFT, padx=10, pady=10)

        WindowsToaster('Winfo').show_toast(newToast)
        print('notification sent to ', station)
    def remove_alert_frame():
        global frame_len
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'all', 'remove')
        frame.pack_forget()
        frame_len -= 1
        frame_id_list.remove(int(frame_id))
    frame = CTkFrame(alert_horiz_scrollframe, fg_color=(LIGHT_3, DARK_3), corner_radius=20)
    CTkFrame(frame, height=1, width=325).pack() #empty frame for width of "frame"
    alert_horiz_scrollframe.pack(expand=True, fill='x', padx=20, pady=20)
    frame.pack(side=LEFT, expand=True, fill='y', padx=20, pady=20)
    CTkLabel(frame, text='', height=3).pack()
    cross_frame = CTkFrame(frame, fg_color='transparent')
    cross_frame.pack(fill='x', pady=5)
    cross_image = CTkImage(light_image=Image.open('images/cross.png'), dark_image=Image.open('images/cross.png'), size=(30, 30))
    cross_button = CTkButton(cross_frame, text='', width=30, image=cross_image, fg_color='transparent', hover=False, command=remove_alert_frame)
    cross_button.pack(side=RIGHT, fill='y', padx=20)
    title_lab = CTkLabel(cross_frame, text='Notification ' + str(frame_id))
    title_lab.pack(side=LEFT, expand=True, padx=10)
    values = station_list[:]
    values.insert(0, 'Sélectionnez une station')

    combobox = CTkOptionMenu(frame, values=values, width=200, command=select_station_event)
    combobox.pack(padx=10, pady=10)

    CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text='Créer une alerte : ', width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover_color=LIGHT_3, hover=False, command=enable_alert).pack()
    alert_frame = CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=50)
    alert_frame.pack()
    alert_frame_1 = CTkFrame(alert_frame, fg_color=(LIGHT_3, DARK_3))
    if preferences['wind_speed_unit'] == 'km/h':
        unit = 'km/h'
        wind_speed_coef = 1
    else:
        unit = 'noeuds'
        wind_speed_coef = 1/1.852
    CTkLabel(alert_frame_1, text='Déterminez un vent moyen minimum :').pack()
    value_and_slider_frame = CTkFrame(alert_frame_1, corner_radius=50)
    value_and_slider_frame.pack(padx=10, pady=5)
    slider = CTkSlider(value_and_slider_frame, from_=0, to=50, number_of_steps=30, command=slider_changed)
    slider.pack(padx=5, pady=5, side=RIGHT)
    value_entry = CTkEntry(value_and_slider_frame, width=100, justify=CENTER, fg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=50)
    value_entry.insert(0, str(int(slider.get()))+'  '+unit)
    value_entry.bind('<Button-1>', select_entry)
    value_entry.bind("<Return>", entry_changed)
    value_entry.pack(padx=5, pady=5, side=LEFT)

    CTkFrame(frame, fg_color=(DARK_1, LIGHT_1), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text='Ajouter un raccourci clavier', width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover=False, corner_radius=10, command=enable_shortcut).pack()
    CTkButton(frame, text='pour envoyer une alerte :', width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover=False, command=enable_shortcut).pack()
    shortcut_frame = CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=50)
    shortcut_frame.pack()
    shortcut_frame_1 = CTkFrame(shortcut_frame, fg_color=(LIGHT_3, DARK_3))
    CTkLabel(shortcut_frame_1, text='', height=15).pack()
    entry = CTkEntry(shortcut_frame_1, width=250, placeholder_text="Entrez un raccourci")
    entry.bind("<KeyPress>", shortcut_entry_entered)
    entry.pack(padx=10, pady=10)

    test_btn_frame = CTkFrame(frame)
    test_btn_frame.place(rely=0.92, relx=0.5, anchor=CENTER)
    CTkButton(test_btn_frame, text="Testez la notification", width=60, command=send_alert).pack(side=RIGHT, padx=10, pady=10)

    skip = False
    if args == ():
        skip = True
    if not skip:
        reload_preferences()
        station_to_add = args[0]
        title_lab['text'] = 'Alerte '+str(preferences['notification'][station_to_add]['frame_order'])
        print(station_to_add, values[int(station_to_add)], f'\n -> {coord_station_meteosuisse[int(station_to_add)-1] = } ')
        combobox.set(values[int(station_to_add)+1])
        entry.delete(0, 'end')
        try:
            try:
                wind = round(float(preferences['notification'][station_to_add]['wind_limit'])*wind_speed_coef, 1)
                if wind == int(wind):
                    wind = int(wind)
                value_entry.delete(0, 'end')
                value_entry.insert(0, str(wind)+'  '+unit)
            except KeyError:
                pass
            slider.set(round(float(preferences['notification'][station_to_add]['wind_limit'])*wind_speed_coef, 1))
            enable_alert(True)
        except KeyError:
            pass
        try:
            entry.insert(0, ' + '.join(preferences['notification'][station_to_add]['shortcut']))
            enable_shortcut()
        except KeyError:
            pass
        del station_to_add

def update_alert_preferences(station_id, type, value):
    reload_preferences()
    print(f'preferences["notification"][{station_id}] -> type: {type}, value: {value}')
    try:
        preferences['notification']
    except KeyError:
        preferences['notification'] = {}
    try:
        preferences['notification'][station_id]
    except KeyError:
        preferences['notification'][station_id] = {}
    if value == 'remove':
        if type == 'all':
            del preferences['notification'][station_id]
        elif type == 'shortcut':
            try:
                del preferences['notification'][station_id]['shortcut']
            except KeyError:
                pass
        elif type == 'wind_limit':
            try:
                del preferences['notification'][station_id]['wind_limit']
            except KeyError:
                pass
    else:
        preferences['notification'][station_id][type] = value
    dump_preferences()

def get_station_which_frame_order_is_frame_id(frame_id):
    reload_preferences()
    try:
        preferences['notification']
    except KeyError:
        return None
    for station_id in preferences['notification'].keys():
        if preferences['notification'][station_id]['frame_order'] == int(frame_id):
            return station_id

def open_website():
    webbrowser.open(SERVER_URL)

def dump_preferences():
    global preferences
    with open('preferences.json', 'w') as f:
        json.dump(preferences, f)

def launch_customtkinter(*args):
    global preferences, station_id_active, station_frame_active, map_active, fav_active, all_station_active, settings_active, wind_sorted_btn_activated, wind_speed_coef, LOCATION, LOCATION_COORDINATES, LATEST_VERSION, LATEST_VERSION_INFO, h1_font, h2_font, p_font, station_dict, abreviation_list, station_list, button1, button2, button3
    station_frame_active, map_active, fav_active, all_station_active, settings_active = False, False, False, False, False
    wind_sorted_btn_activated = False
    station_id_active = 1
    reload_preferences()
    dump_preferences()
    def set_location_by_ip():
        preferences['location'] = []
        preferences['location'].append(geocoder.ip('me').city) # index : 0
        preferences['location'].append(geocoder.ip('me').lat) # index : 1
        preferences['location'].append(geocoder.ip('me').lng) # index : 2
        preferences['location'].append('created_by_ip') # index : 3
        dump_preferences()
    try:
        preferences['location'][3]
        if preferences['location'][3] == 'created_by_ip':
            set_location_by_ip()
    except KeyError:
        set_location_by_ip()
    LOCATION = preferences['location'][0]
    LOCATION_COORDINATES = (preferences['location'][1], preferences['location'][2])


    h1_font = CTkFont('roboto mono', size=30)
    h2_font = CTkFont('roboto mono', size=24)
    h2_font = CTkFont('roboto mono', size=22)
    p_font =  CTkFont('roboto mono', size=12)

    left_column_frame = CTkFrame(window, width=150, height=window.winfo_screenheight())
    left_column_frame.pack(side="left", fill="y")

    button1 = CTkButton(left_column_frame, text="Stations", command=button1_pressed)
    button1.pack(padx=20, pady=10)

    button2 = CTkButton(left_column_frame, text="Carte", command=button2_pressed)
    button2.pack(padx=20, pady=10)

    button3 = CTkButton(left_column_frame, text="Paramètres", command=button3_pressed)
    button3.pack(padx=20, pady=10)

    if 'theme' in preferences.keys():
        set_appearance_mode(preferences['theme'])
        print(preferences['theme'])
        change_theme(preferences['theme'])

    map_frame_setup(pack=False, displaying_values=True)
    table_frame_setup(pack=False, fav_bool=False, wind_sorted=False)
    settings_frame_setup(pack=False)
    station_frame_setup(pack=False, station_id=1)
    try:
        r = requests.get('https://louse-proud-raven.ngrok-free.app/last_infos')
        r = json.loads(r.text)
        LATEST_VERSION = r['latest_version']
        LATEST_VERSION_INFO = r[str(LATEST_VERSION)]
    except Exception as error:
        print(error)
        LATEST_VERSION = 'error'
    print('\nVersion check :')
    if CURRENT_VERSION == LATEST_VERSION:
        print("you're on the latest version")
    elif LATEST_VERSION == 'error':
        print("you're on version " + str(CURRENT_VERSION) + ' but cannot check latest version')
    else:
        print('not the last version', 'you are on version ' + str(CURRENT_VERSION) + ' and the latest version is ' + str(LATEST_VERSION))
        if 'not_show_update' not in preferences.keys():
            new_version_top_level()

    get_csv()
    button1_pressed()
    window.mainloop()

window = CTk()
window.geometry("1200x800+200+50")
window.title(f'Winfo {CURRENT_VERSION}')

if __name__ == "__main__":
    launch_customtkinter()
