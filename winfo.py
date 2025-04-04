from customtkinter import *
from CTkTable import CTkTable
import tkintermapview
import requests, urllib.request, csv, json, webbrowser
import geocoder
import geopy.distance
from math import log, sqrt
from datetime import timedelta
from winfo_import import *
from winfo_constants import *
import winfo_import_json_preferences
from winfo_classes import *

from PIL import Image
from PIL import ImageTk
from cosmo_parser import cosmo_parser

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import subprocess
import platform
import os

if platform.system().lower() == 'windows':
    OS = 'windows'
    from win32com.client import Dispatch
    from windows_toasts import Toast, InteractableWindowsToaster, WindowsToaster, ToastDisplayImage, ToastActivatedEventArgs, ToastImagePosition

    import pywinstyles # CTkwindow with style acrylic
elif platform.system().lower() == 'linux':
    OS = 'linux'
elif platform.system().lower() == 'darwin':
    OS = 'macos'
def new_version_top_level():
    logger.info('new_version_top_level() called')
    def top_level_focus():
        toplevel.focus_set()
        toplevel.after(10000, top_level_focus)
    global toplevel
    toplevel = CTkToplevel(window)
    toplevel.title(language_dict['New_Version_Available']['window_title'][lang_index])
    toplevel.geometry('500x400+1900+300')
    toplevel.grid_columnconfigure(0, weight=1)
    toplevel.grid_rowconfigure(3, weight=1)
    # if os == 'windows': # pywinstyles doesn't work well with toplevel
    #     pywinstyles.apply_style(toplevel, 'acrylic')
    #     pywinstyles.set_opacity(toplevel, 0.9)

    CTkLabel(toplevel, text=language_dict['New_Version_Available']['label_title'][lang_index], font=H1_FONT).grid(row=0, column=0, padx=20, pady=(40,20), sticky="ew")
    CTkLabel(toplevel, text=language_dict['New_Version_Available']['latest_is'][lang_index]+str(LATEST_VERSION), font=H2_FONT).grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    if LATEST_VERSION_INFO != '':
        CTkLabel(toplevel, text=language_dict['New_Version_Available']['updates'][lang_index], font=H2_FONT).grid(row=2, column=0, padx=20, pady=(20,5), sticky="w")
        CTkLabel(toplevel, text=LATEST_VERSION_INFO, font=H2_FONT, justify="left", wraplength=460).grid(row=3, column=0, padx=20, pady=5, sticky="nw")

    button_frame = CTkFrame(toplevel, fg_color="transparent")
    button_frame.grid(row=4, column=0, pady=(20,20), sticky="ew")
    button_frame.grid_columnconfigure((0,1), weight=1)

    CTkButton(button_frame, text=language_dict['New_Version_Available']['download_btn'][lang_index], command=open_new_version).grid(row=0, column=0, padx=10, sticky="e")
    CTkButton(button_frame, text=language_dict['New_Version_Available']['dont_show_again_btn'][lang_index], command=ne_plus_afficher).grid(row=0, column=1, padx=10, sticky="w")

    toplevel.after('idle', top_level_focus)

def open_new_version():
    logger.info('open_new_version() called')
    webbrowser.open("https://louse-proud-raven.ngrok-free.app/versions/")
    toplevel.destroy()
def ne_plus_afficher():
    logger.info('ne_plus_afficher() called')
    toplevel.destroy()
    reload_preferences()
    preferences['not_show_update'] = True
    dump_preferences()
def create_shortcut_top_level():
    logger.info('create_shortcut_top_level() called')
    def top_level_focus():
        toplevel.focus_set()
        toplevel.after(10000, top_level_focus)
    def create_shortcut_lnk():
        logger.info('create_shortcut_lnk() called')
        current_dir = os.getcwd()
        target_path = os.path.join(current_dir, 'winfo.py')

        shell = Dispatch('WScript.Shell')
        desktop = shell.SpecialFolders("Desktop")
        lnk_path = os.path.join(desktop, "Winfo.lnk")

        shortcut = shell.CreateShortCut(lnk_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = current_dir
        shortcut.save()
        toplevel.destroy()
        logger.info('create_shortcut_lnk() finished')

    toplevel = CTkToplevel(window)
    # if os == 'windows': # pywinstyles doesn't work well with toplevel
    #     pywinstyles.apply_style(toplevel, 'acrylic')
    #     pywinstyles.set_opacity(toplevel, 0.9)

    CTkLabel(toplevel, font=H1_FONT, text=language_dict['Infos']['add_desktop_shortcut'][lang_index]).pack(padx=20, pady=20)
    yes_no_frame = CTkFrame(toplevel, fg_color='transparent')
    yes_no_frame.pack(padx=20, pady=10)
    CTkButton(yes_no_frame, text=language_dict['Infos']['yes'][lang_index], command=create_shortcut_lnk).pack(padx=10, pady=10, side=LEFT)
    CTkButton(yes_no_frame, text=language_dict['Infos']['no'][lang_index], command=toplevel.destroy).pack(padx=10, pady=10, side=RIGHT)

    toplevel.after('idle', top_level_focus)
def button1_pressed():
    logger.info('button1_pressed() called')
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
    logger.info('button2_pressed() called')
    button2.configure(fg_color=BUTTON_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    map_frame_setup(pack=True, displaying_values=True)

def button3_pressed():
    logger.info('button3_pressed() called')
    button3.configure(fg_color=BUTTON_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    settings_frame_setup(pack=True)
def get_csv():
    logger.info('get_csv() called')
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
        logger.error(f'get_csv() failed: {error}')
        logger.info('creating errored file')
        create_errored_file(error)
    window.after(10000, get_csv)


def update_all_values():
    logger.info('updating values... new ones are here !!!')
    # if map_active:
    if active_frame_manager.active_frame_type == 'map':
        map_frame_setup(True, displaying_values=True)
        logger.info("updating values..  in map_frame")
        return
    # elif fav_active:
    elif active_frame_manager.active_frame_type == 'fav_station':

        table_frame_setup(pack=True, fav_bool=True, wind_sorted=wind_sorted_btn_activated)
        logger.info("updating values..  in favorites_frame")
        return
    # elif all_station_active:
    elif active_frame_manager.active_frame_type == 'all_station':
        table_frame_setup(pack=True, fav_bool=False, wind_sorted=wind_sorted_btn_activated)
        logger.info("updating values..  in all_station_frame")
        return
    # elif settings_active:
    elif active_frame_manager.active_frame_type == 'settings':
        logger.info("updating values..  in settings so idk what to do...")
        return
    # elif station_frame_active:
    elif active_frame_manager.active_frame_type == 'station_frame':
        logger.info("updating values..  in station_frame")
        station_frame_setup(pack=True, station_id=station_id_active)
        return
    else:
        logger.info('updating values.. no page displayed yet')

    frame_navigator.__init__() # reset everything so that it will update the values (not load back unupdated frames)








def change_theme(theme):
    logger.info(f'change_theme() called -> new theme : {theme}')
    global active_theme
    if theme == language_dict['Infos']['theme_system'][lang_index]:
        theme = "System"
    elif theme == language_dict['Infos']['theme_dark'][lang_index]:
        theme = "Dark"
    elif theme == language_dict['Infos']['theme_light'][lang_index]:
        theme = "Light"
    logger.info(f'theme changed to {theme}')
    set_appearance_mode(theme)
    preferences['theme'] = theme
    dump_preferences()
    active_theme = theme

def display_loading(root, *args):
    global loading_img
    loading_img = CTkLabel(root, text=language_dict['Infos']['text_loading'][lang_index], font=('roboto mono', 30))
    loading_img.pack(expand=True, fill='both')

def change_default_tile_server(tile_server):
    reload_preferences()
    preferences['map_tile_server'] = tile_server
    dump_preferences()
def change_tile_server(tile_server):
    logger.info(f'change_tile_server() called -> new tile server : {tile_server}')
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
    logger.info(f'find_station_data_in_data_geo_files() called -> station : {abr}')
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
    logger.info('map_frame_setup() called -> pack: {}, displaying_values: {}'.format(pack, displaying_values))
    global map_frame, map_widget, map_active, fav_active, all_station_active, settings_active, station_frame_active
    # try:
    #     map_frame.pack_forget()
    # except:
    #     pass
    # try:
    #     station_frame.pack_forget()
    # except: pass
    frame_navigator.forget_active_frame()
    map_frame = CTkFrame(window)
    def display_values():
        map_frame_setup(pack=True, displaying_values=display_values_switch.get())

    if pack:
        reload_preferences()
        map_frame.pack(fill='both', expand=True, padx=20, pady=10)
        if os == 'windows':
            pywinstyles.set_opacity(map_frame, 1)
        map_options_frame = CTkFrame(map_frame, bg_color='transparent', fg_color='transparent')
        map_options_frame.pack(fill="x", expand=False, padx=10, pady=0)
        titre_carte = CTkLabel(map_options_frame, text=language_dict['Map']['title'][lang_index], font=H1_FONT)
        titre_carte.pack(pady=20)
        display_loading(map_frame)
        map_widget = tkintermapview.TkinterMapView(map_frame, width=1000, height=700, corner_radius=20)
        display_values_switch = CTkSwitch(map_options_frame, text=language_dict['Map']['display_value_switch'][lang_index], command=display_values)
        if displaying_values:
            display_values_switch.select()
        else:
            display_values_switch.deselect()
        display_values_switch.pack(side=LEFT, padx=10, pady=10)
        if preferences['wind_speed_unit'] == 'kph':
            unit = language_dict['Infos']['kph'][lang_index]
        else:
            unit = language_dict['Infos']['knots'][lang_index]
        try:
            CTkLabel(map_options_frame, text=language_dict['Map']['unit_info_label'][lang_index]+unit, bg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=100).pack(side=LEFT, padx=40, pady=10)
        except:
            CTkLabel(map_options_frame, text=language_dict['Map']['unit_info_label'][lang_index]+unit, bg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=100).pack(side=LEFT, padx=40, pady=10)

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
        for ligne, coor in zip(VQHA80, coord):
            if ligne['Station/Location'] == 'MRP':
                continue
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
            map_widget.set_marker(float(coor[1]), float(coor[2]), text=vent, text_color="black", icon=icon, command=lambda marker, id=coor[5]:[station_frame_setup(pack=True, station_id=id)])

        map_widget.set_position(float(LOCATION_COORDINATES[0]), float(LOCATION_COORDINATES[1]))
        map_widget.set_zoom(9)#7
        loading_img.pack_forget()
        map_widget.pack(fill="both", expand=True, padx=10)
        active_frame_manager.set_active_frame(map_frame, 'map')
        # map_active = True
        # station_frame_active, fav_active, all_station_active, settings_active = False, False, False, False


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
    position = (pos_lat, pos_lon)
    station_pos = (station_lat, station_lon)
    distance = geopy.distance.distance(position, station_pos).km
    distance = round(distance, 5)
    return distance

def get_station_matrix(fav_bool: bool, wind_sorted: bool):
    already_direction = False
    with open("VQHA80.csv", "r") as f_csv:
        reader = csv.DictReader(f_csv, delimiter=';')
        values = []
        search_input = search_entry.get().lower()
        reload_preferences()
        with open("coord_station_meteosuisse.json", "r") as f_json:
            coord_reader = json.load(f_json)
            logger.info(f'LOCATION_COORDINATES: {LOCATION_COORDINATES[0]} | {LOCATION_COORDINATES[1]}')
            for ligne, coord in zip(reader, coord_reader):
                if ligne['Station/Location'] == 'MRP':  # exists in meteoswiss but always empty
                    continue
                if LOCATION_COORDINATES[0] is not None and LOCATION_COORDINATES[1] is not None: # if no LOCATION found don't check for distance and display all
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
                    if 'urlopen error' not in ligne['dkl010z0']:
                        direction, vent, rafale = find_station_data_in_data_geo_files(abr=coord[0])
                    else:
                        direction, vent, rafale = None, None, None
                    already_direction = True
                if vent is None or rafale is None:
                    vent, rafale = '-', '-'
                    new_line.append('')
                else:
                    if wind_speed_coef == 1:
                        new_line.append(f"{str(vent)} | {str(rafale)}  {language_dict['Infos']['kph'][lang_index]}")
                    else:
                        new_line.append(f"{str(vent)} | {str(rafale)}  {language_dict['Infos']['knots'][lang_index]}")
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
            values.insert(0, [language_dict['Stations']['table_title_station'][lang_index], language_dict['Stations']['table_title_wind-gust'][lang_index], language_dict['Stations']['table_title_direction'][lang_index], language_dict['Stations']['table_title_county'][lang_index], language_dict['Stations']['table_title_favorites'][lang_index]])
            return values

def set_segmented_btn(fav_bool: bool):
    global fav_or_all_btn
    fav_or_all_btn = CTkSegmentedButton(table_frame, values=[language_dict['Stations']['favorites_segmented_btn'][lang_index], language_dict['Stations']['all_stations_segmented_btn'][lang_index],], command=change_fav_or_all_from_segbtn)
    fav_or_all_btn.pack(pady=20)
    if fav_bool == True:
        fav_or_all_btn.set(language_dict['Stations']['favorites_segmented_btn'][lang_index])
    else:
        fav_or_all_btn.set(language_dict['Stations']['all_stations_segmented_btn'][lang_index])

def change_fav_or_all_from_segbtn(value):
    logger.info(f'change_fav_or_all_from_segbtn: {value}')
    global search_input
    search_input = ''
    frame_navigator.forget_active_frame()
    # table_frame.pack_forget()
    if value == language_dict['Stations']['favorites_segmented_btn'][lang_index]:
        table_frame_setup(pack=True, fav_bool=True, wind_sorted=wind_sorted_btn_activated)
        fav_or_all_btn.set(language_dict['Stations']['favorites_segmented_btn'][lang_index])
    if value == language_dict['Stations']['all_stations_segmented_btn'][lang_index]:
        table_frame_setup(pack=True, fav_bool=False, wind_sorted=wind_sorted_btn_activated)
        fav_or_all_btn.set(language_dict['Stations']['all_stations_segmented_btn'][lang_index])

def search_in_table(fav_bool: bool, wind_sorted: bool):
    global search_input
    search_input = search_entry.get()
    table_frame_setup(pack=True, fav_bool=fav_bool, wind_sorted=wind_sorted)

def remove_last_word_search_entry(e): #called if backspace+ctrl is pressed and delete all the search
    global search_input
    text = search_entry.get()
    last_space = text.rstrip().rfind(' ')  # find the last space
    if last_space != -1:  # if there is a space
        search_entry.delete(last_space+2, END)
        search_input = search_entry.get()
    else:  # if there is only one word
        search_entry.delete(0, END)
        search_input = ''




def table_frame_setup(pack: bool, fav_bool: bool, wind_sorted: bool):
    logger.info(f'table_frame_setup() called -> pack: {pack}, fav_bool: {fav_bool}, wind_sorted: {wind_sorted}')
    global table_frame, table_frame_active, station_frame_active, map_active, settings_active, alphabetical_sort_box, table, fav_active, all_station_active, search_entry, entry_as_display
    # try:
    #     table_frame.pack_forget()
    # except:
    #     pass
    # try:
    #     station_frame.pack_forget()
    # except: pass
    frame_navigator.forget_active_frame()
    table_frame = CTkFrame(window)
    if not pack:
        return
    else:
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        if os == 'windows':
            pywinstyles.set_opacity(table_frame, 1)
    info, date = get_active_wind(1)
    csv_date_frame = CTkFrame(table_frame, fg_color='transparent', height=1)
    csv_date_frame.pack(fill='x')
    CTkLabel(csv_date_frame, text=language_dict['Stations']['csv_date'][lang_index]+' : '+date[0]+'h'+date[1]).pack(side=RIGHT, padx=10)
    # table_frame_active = CTkLabel(table_frame, text=language_dict['Stations']['title'][lang_index], font=h1_font).pack(pady=20) #TODO
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
        if row == 0:
            return
        else:
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
                    logger.info(f'favoris = {favoris}')
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
    alphabetical_sort_box = CTkCheckBox(table_frame, text=language_dict['Stations']['sorted_box'][lang_index], command=changed_wind_sorted)
    if not wind_sorted: alphabetical_sort_box.select()
    alphabetical_sort_box.pack()
    display_loading(table_frame)
    distance_slider_and_search_frame = CTkFrame(table_frame, fg_color='transparent')
    distance_slider_and_search_frame.pack(pady=10)
    scrollframe = CTkScrollableFrame(table_frame, fg_color='transparent')
    scrollframe.pack(expand=True, fill="both", padx=10, pady=10)
    if LOCATION is None:
        location_begining = language_dict['Stations']['no_location_error'][lang_index].upper()
    elif len(LOCATION) < 25:
        location_begining = LOCATION.upper()
    else:
        location_begining = LOCATION[0:23].upper() + '..'
    CTkLabel(distance_slider_and_search_frame, text=language_dict['Stations']['displaying_radius'][lang_index]+location_begining, width=100).pack(side=LEFT, padx=10)
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
    search_entry = CTkEntry(distance_slider_and_search_frame, placeholder_text=language_dict['Stations']['search_placeholder'][lang_index], width=200)
    search_entry.bind('<Control-BackSpace>', remove_last_word_search_entry)
    search_entry.bind("<Return>", lambda _: search_in_table(fav_bool, wind_sorted))

    # if fav_bool:
    #     if wind_sorted:
    #         search_entry.bind("<Return>", search_in_table_T_T)
    #     else:
    #         search_entry.bind("<Return>", search_in_table_T_F)
    # else:
    #     if wind_sorted:
    #         search_entry.bind("<Return>", search_in_table_F_T)
    #     else:
    #         search_entry.bind("<Return>", search_in_table_F_F)
    try:
        search_entry.insert(0, search_input)
        search_entry.focus()
    except NameError:
        pass
    search_entry.pack(padx=20, pady=20, side=RIGHT)
    setup_table_stations(None)
    loading_img.pack_forget()
    table_frame_active = True
    # fav_active, all_station_active = False, False
    if fav_bool:
        # fav_active = True
        active_frame_manager.set_active_frame(table_frame, 'fav_station')
    else:
        # all_station_active = True
        active_frame_manager.set_active_frame(table_frame, 'all_station')
    # station_frame_active, map_active, settings_active = False, False, False
def get_active_wind(station_id: int):
    abr = coord_station_meteosuisse[station_id][0]
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
                date = row['Date']
                date = strafe_date_from_csv(date)
                if moyenne == 'N/A' or rafale == 'N/A' or direction == 'N/A':
                    pass
                else:
                    info = [moyenne, rafale, direction]
                    return info, date
    direction, moyenne, rafale = find_station_data_in_data_geo_files(abr=abr)
    if direction is None: direction = 'N/A'
    if moyenne is None: moyenne = 'N/A'
    if rafale is None: rafale = 'N/A'
    return [moyenne, rafale, direction]
def create_mesurement_errored_file():
    with open('mesurement_history.csv', 'w') as file:
        file.write('Date,TAE_moyenne,TAE_rafale,TAE_direction,TAE_temp,TAE_pluie,TAE_humidite,TAE_QFE,TAE_QFF,TAE_QNH,COM_moyenne,COM_rafale,COM_direction,COM_temp,COM_pluie,COM_humidite,COM_QFE,COM_QFF,COM_QNH,ABO_moyenne,ABO_rafale,ABO_direction,ABO_temp,ABO_pluie,ABO_humidite,ABO_QFE,ABO_QFF,ABO_QNH,AIG_moyenne,AIG_rafale,AIG_direction,AIG_temp,AIG_pluie,AIG_humidite,AIG_QFE,AIG_QFF,AIG_QNH,ALT_moyenne,ALT_rafale,ALT_direction,ALT_temp,ALT_pluie,ALT_humidite,ALT_QFE,ALT_QFF,ALT_QNH,ARH_moyenne,ARH_rafale,ARH_direction,ARH_temp,ARH_pluie,ARH_humidite,ARH_QFE,ARH_QFF,ARH_QNH,AND_moyenne,AND_rafale,AND_direction,AND_temp,AND_pluie,AND_humidite,AND_QFE,AND_QFF,AND_QNH,ANT_moyenne,ANT_rafale,ANT_direction,ANT_temp,ANT_pluie,ANT_humidite,ANT_QFE,ANT_QFF,ANT_QNH,ARO_moyenne,ARO_rafale,ARO_direction,ARO_temp,ARO_pluie,ARO_humidite,ARO_QFE,ARO_QFF,ARO_QNH,RAG_moyenne,RAG_rafale,RAG_direction,RAG_temp,RAG_pluie,RAG_humidite,RAG_QFE,RAG_QFF,RAG_QNH,BAN_moyenne,BAN_rafale,BAN_direction,BAN_temp,BAN_pluie,BAN_humidite,BAN_QFE,BAN_QFF,BAN_QNH,BAS_moyenne,BAS_rafale,BAS_direction,BAS_temp,BAS_pluie,BAS_humidite,BAS_QFE,BAS_QFF,BAS_QNH,LAT_moyenne,LAT_rafale,LAT_direction,LAT_temp,LAT_pluie,LAT_humidite,LAT_QFE,LAT_QFF,LAT_QNH,BER_moyenne,BER_rafale,BER_direction,BER_temp,BER_pluie,BER_humidite,BER_QFE,BER_QFF,BER_QNH,BEZ_moyenne,BEZ_rafale,BEZ_direction,BEZ_temp,BEZ_pluie,BEZ_humidite,BEZ_QFE,BEZ_QFF,BEZ_QNH,BIA_moyenne,BIA_rafale,BIA_direction,BIA_temp,BIA_pluie,BIA_humidite,BIA_QFE,BIA_QFF,BIA_QNH,BIN_moyenne,BIN_rafale,BIN_direction,BIN_temp,BIN_pluie,BIN_humidite,BIN_QFE,BIN_QFF,BIN_QNH,BIZ_moyenne,BIZ_rafale,BIZ_direction,BIZ_temp,BIZ_pluie,BIZ_humidite,BIZ_QFE,BIZ_QFF,BIZ_QNH,BIV_moyenne,BIV_rafale,BIV_direction,BIV_temp,BIV_pluie,BIV_humidite,BIV_QFE,BIV_QFF,BIV_QNH,BIE_moyenne,BIE_rafale,BIE_direction,BIE_temp,BIE_pluie,BIE_humidite,BIE_QFE,BIE_QFF,BIE_QNH,BLA_moyenne,BLA_rafale,BLA_direction,BLA_temp,BLA_pluie,BLA_humidite,BLA_QFE,BLA_QFF,BLA_QNH,BOL_moyenne,BOL_rafale,BOL_direction,BOL_temp,BOL_pluie,BOL_humidite,BOL_QFE,BOL_QFF,BOL_QNH,BOU_moyenne,BOU_rafale,BOU_direction,BOU_temp,BOU_pluie,BOU_humidite,BOU_QFE,BOU_QFF,BOU_QNH,BRZ_moyenne,BRZ_rafale,BRZ_direction,BRZ_temp,BRZ_pluie,BRZ_humidite,BRZ_QFE,BRZ_QFF,BRZ_QNH,BUS_moyenne,BUS_rafale,BUS_direction,BUS_temp,BUS_pluie,BUS_humidite,BUS_QFE,BUS_QFF,BUS_QNH,BUF_moyenne,BUF_rafale,BUF_direction,BUF_temp,BUF_pluie,BUF_humidite,BUF_QFE,BUF_QFF,BUF_QNH,FRE_moyenne,FRE_rafale,FRE_direction,FRE_temp,FRE_pluie,FRE_humidite,FRE_QFE,FRE_QFF,FRE_QNH,CEV_moyenne,CEV_rafale,CEV_direction,CEV_temp,CEV_pluie,CEV_humidite,CEV_QFE,CEV_QFF,CEV_QNH,CHZ_moyenne,CHZ_rafale,CHZ_direction,CHZ_temp,CHZ_pluie,CHZ_humidite,CHZ_QFE,CHZ_QFF,CHZ_QNH,CHA_moyenne,CHA_rafale,CHA_direction,CHA_temp,CHA_pluie,CHA_humidite,CHA_QFE,CHA_QFF,CHA_QNH,CHM_moyenne,CHM_rafale,CHM_direction,CHM_temp,CHM_pluie,CHM_humidite,CHM_QFE,CHM_QFF,CHM_QNH,CHU_moyenne,CHU_rafale,CHU_direction,CHU_temp,CHU_pluie,CHU_humidite,CHU_QFE,CHU_QFF,CHU_QNH,CHD_moyenne,CHD_rafale,CHD_direction,CHD_temp,CHD_pluie,CHD_humidite,CHD_QFE,CHD_QFF,CHD_QNH,CIM_moyenne,CIM_rafale,CIM_direction,CIM_temp,CIM_pluie,CIM_humidite,CIM_QFE,CIM_QFF,CIM_QNH,CDM_moyenne,CDM_rafale,CDM_direction,CDM_temp,CDM_pluie,CDM_humidite,CDM_QFE,CDM_QFF,CDM_QNH,GSB_moyenne,GSB_rafale,GSB_direction,GSB_temp,GSB_pluie,GSB_humidite,GSB_QFE,GSB_QFF,GSB_QNH,COY_moyenne,COY_rafale,COY_direction,COY_temp,COY_pluie,COY_humidite,COY_QFE,COY_QFF,COY_QNH,CMA_moyenne,CMA_rafale,CMA_direction,CMA_temp,CMA_pluie,CMA_humidite,CMA_QFE,CMA_QFF,CMA_QNH,CRM_moyenne,CRM_rafale,CRM_direction,CRM_temp,CRM_pluie,CRM_humidite,CRM_QFE,CRM_QFF,CRM_QNH,DAV_moyenne,DAV_rafale,DAV_direction,DAV_temp,DAV_pluie,DAV_humidite,DAV_QFE,DAV_QFF,DAV_QNH,DEM_moyenne,DEM_rafale,DEM_direction,DEM_temp,DEM_pluie,DEM_humidite,DEM_QFE,DEM_QFF,DEM_QNH,DIS_moyenne,DIS_rafale,DIS_direction,DIS_temp,DIS_pluie,DIS_humidite,DIS_QFE,DIS_QFF,DIS_QNH,EBK_moyenne,EBK_rafale,EBK_direction,EBK_temp,EBK_pluie,EBK_humidite,EBK_QFE,EBK_QFF,EBK_QNH,EGH_moyenne,EGH_rafale,EGH_direction,EGH_temp,EGH_pluie,EGH_humidite,EGH_QFE,EGH_QFF,EGH_QNH,EGO_moyenne,EGO_rafale,EGO_direction,EGO_temp,EGO_pluie,EGO_humidite,EGO_QFE,EGO_QFF,EGO_QNH,EIN_moyenne,EIN_rafale,EIN_direction,EIN_temp,EIN_pluie,EIN_humidite,EIN_QFE,EIN_QFF,EIN_QNH,ELM_moyenne,ELM_rafale,ELM_direction,ELM_temp,ELM_pluie,ELM_humidite,ELM_QFE,ELM_QFF,ELM_QNH,ENG_moyenne,ENG_rafale,ENG_direction,ENG_temp,ENG_pluie,ENG_humidite,ENG_QFE,ENG_QFF,ENG_QNH,EVI_moyenne,EVI_rafale,EVI_direction,EVI_temp,EVI_pluie,EVI_humidite,EVI_QFE,EVI_QFF,EVI_QNH,EVO_moyenne,EVO_rafale,EVO_direction,EVO_temp,EVO_pluie,EVO_humidite,EVO_QFE,EVO_QFF,EVO_QNH,FAH_moyenne,FAH_rafale,FAH_direction,FAH_temp,FAH_pluie,FAH_humidite,FAH_QFE,FAH_QFF,FAH_QNH,FLU_moyenne,FLU_rafale,FLU_direction,FLU_temp,FLU_pluie,FLU_humidite,FLU_QFE,FLU_QFF,FLU_QNH,GRA_moyenne,GRA_rafale,GRA_direction,GRA_temp,GRA_pluie,GRA_humidite,GRA_QFE,GRA_QFF,GRA_QNH,FRU_moyenne,FRU_rafale,FRU_direction,FRU_temp,FRU_pluie,FRU_humidite,FRU_QFE,FRU_QFF,FRU_QNH,GVE_moyenne,GVE_rafale,GVE_direction,GVE_temp,GVE_pluie,GVE_humidite,GVE_QFE,GVE_QFF,GVE_QNH,GES_moyenne,GES_rafale,GES_direction,GES_temp,GES_pluie,GES_humidite,GES_QFE,GES_QFF,GES_QNH,GIH_moyenne,GIH_rafale,GIH_direction,GIH_temp,GIH_pluie,GIH_humidite,GIH_QFE,GIH_QFF,GIH_QNH,GLA_moyenne,GLA_rafale,GLA_direction,GLA_temp,GLA_pluie,GLA_humidite,GLA_QFE,GLA_QFF,GLA_QNH,GOR_moyenne,GOR_rafale,GOR_direction,GOR_temp,GOR_pluie,GOR_humidite,GOR_QFE,GOR_QFF,GOR_QNH,GRE_moyenne,GRE_rafale,GRE_direction,GRE_temp,GRE_pluie,GRE_humidite,GRE_QFE,GRE_QFF,GRE_QNH,GRH_moyenne,GRH_rafale,GRH_direction,GRH_temp,GRH_pluie,GRH_humidite,GRH_QFE,GRH_QFF,GRH_QNH,GRO_moyenne,GRO_rafale,GRO_direction,GRO_temp,GRO_pluie,GRO_humidite,GRO_QFE,GRO_QFF,GRO_QNH,GRC_moyenne,GRC_rafale,GRC_direction,GRC_temp,GRC_pluie,GRC_humidite,GRC_QFE,GRC_QFF,GRC_QNH,GOS_moyenne,GOS_rafale,GOS_direction,GOS_temp,GOS_pluie,GOS_humidite,GOS_QFE,GOS_QFF,GOS_QNH,GOE_moyenne,GOE_rafale,GOE_direction,GOE_temp,GOE_pluie,GOE_humidite,GOE_QFE,GOE_QFF,GOE_QNH,GUE_moyenne,GUE_rafale,GUE_direction,GUE_temp,GUE_pluie,GUE_humidite,GUE_QFE,GUE_QFF,GUE_QNH,GUT_moyenne,GUT_rafale,GUT_direction,GUT_temp,GUT_pluie,GUT_humidite,GUT_QFE,GUT_QFF,GUT_QNH,HLL_moyenne,HLL_rafale,HLL_direction,HLL_temp,HLL_pluie,HLL_humidite,HLL_QFE,HLL_QFF,HLL_QNH,HOE_moyenne,HOE_rafale,HOE_direction,HOE_temp,HOE_pluie,HOE_humidite,HOE_QFE,HOE_QFF,HOE_QNH,ILZ_moyenne,ILZ_rafale,ILZ_direction,ILZ_temp,ILZ_pluie,ILZ_humidite,ILZ_QFE,ILZ_QFF,ILZ_QNH,INT_moyenne,INT_rafale,INT_direction,INT_temp,INT_pluie,INT_humidite,INT_QFE,INT_QFF,INT_QNH,JUN_moyenne,JUN_rafale,JUN_direction,JUN_temp,JUN_pluie,JUN_humidite,JUN_QFE,JUN_QFF,JUN_QNH,KOP_moyenne,KOP_rafale,KOP_direction,KOP_temp,KOP_pluie,KOP_humidite,KOP_QFE,KOP_QFF,KOP_QNH,BRL_moyenne,BRL_rafale,BRL_direction,BRL_temp,BRL_pluie,BRL_humidite,BRL_QFE,BRL_QFF,BRL_QNH,CDF_moyenne,CDF_rafale,CDF_direction,CDF_temp,CDF_pluie,CDF_humidite,CDF_QFE,CDF_QFF,CDF_QNH,DOL_moyenne,DOL_rafale,DOL_direction,DOL_temp,DOL_pluie,DOL_humidite,DOL_QFE,DOL_QFF,DOL_QNH,LAC_moyenne,LAC_rafale,LAC_direction,LAC_temp,LAC_pluie,LAC_humidite,LAC_QFE,LAC_QFF,LAC_QNH,LAG_moyenne,LAG_rafale,LAG_direction,LAG_temp,LAG_pluie,LAG_humidite,LAG_QFE,LAG_QFF,LAG_QNH,MLS_moyenne,MLS_rafale,MLS_direction,MLS_temp,MLS_pluie,MLS_humidite,MLS_QFE,MLS_QFF,MLS_QNH,LEI_moyenne,LEI_rafale,LEI_direction,LEI_temp,LEI_pluie,LEI_humidite,LEI_QFE,LEI_QFF,LEI_QNH,ATT_moyenne,ATT_rafale,ATT_direction,ATT_temp,ATT_pluie,ATT_humidite,ATT_QFE,ATT_QFF,ATT_QNH,CHB_moyenne,CHB_rafale,CHB_direction,CHB_temp,CHB_pluie,CHB_humidite,CHB_QFE,CHB_QFF,CHB_QNH,DIA_moyenne,DIA_rafale,DIA_direction,DIA_temp,DIA_pluie,DIA_humidite,DIA_QFE,DIA_QFF,DIA_QNH,MAR_moyenne,MAR_rafale,MAR_direction,MAR_temp,MAR_pluie,MAR_humidite,MAR_QFE,MAR_QFF,MAR_QNH,OTL_moyenne,OTL_rafale,OTL_direction,OTL_temp,OTL_pluie,OTL_humidite,OTL_QFE,OTL_QFF,OTL_QNH,LUG_moyenne,LUG_rafale,LUG_direction,LUG_temp,LUG_pluie,LUG_humidite,LUG_QFE,LUG_QFF,LUG_QNH,LUZ_moyenne,LUZ_rafale,LUZ_direction,LUZ_temp,LUZ_pluie,LUZ_humidite,LUZ_QFE,LUZ_QFF,LUZ_QNH,LAE_moyenne,LAE_rafale,LAE_direction,LAE_temp,LAE_pluie,LAE_humidite,LAE_QFE,LAE_QFF,LAE_QNH,MAG_moyenne,MAG_rafale,MAG_direction,MAG_temp,MAG_pluie,MAG_humidite,MAG_QFE,MAG_QFF,MAG_QNH,MAS_moyenne,MAS_rafale,MAS_direction,MAS_temp,MAS_pluie,MAS_humidite,MAS_QFE,MAS_QFF,MAS_QNH,MAH_moyenne,MAH_rafale,MAH_direction,MAH_temp,MAH_pluie,MAH_humidite,MAH_QFE,MAH_QFF,MAH_QNH,MTR_moyenne,MTR_rafale,MTR_direction,MTR_temp,MTR_pluie,MTR_humidite,MTR_QFE,MTR_QFF,MTR_QNH,MER_moyenne,MER_rafale,MER_direction,MER_temp,MER_pluie,MER_humidite,MER_QFE,MER_QFF,MER_QNH,MOB_moyenne,MOB_rafale,MOB_direction,MOB_temp,MOB_pluie,MOB_humidite,MOB_QFE,MOB_QFF,MOB_QNH,MVE_moyenne,MVE_rafale,MVE_direction,MVE_temp,MVE_pluie,MVE_humidite,MVE_QFE,MVE_QFF,MVE_QNH,GEN_moyenne,GEN_rafale,GEN_direction,GEN_temp,GEN_pluie,GEN_humidite,GEN_QFE,GEN_QFF,GEN_QNH,MRP_moyenne,MRP_rafale,MRP_direction,MRP_temp,MRP_pluie,MRP_humidite,MRP_QFE,MRP_QFF,MRP_QNH,MOA_moyenne,MOA_rafale,MOA_direction,MOA_temp,MOA_pluie,MOA_humidite,MOA_QFE,MOA_QFF,MOA_QNH,MTE_moyenne,MTE_rafale,MTE_direction,MTE_temp,MTE_pluie,MTE_humidite,MTE_QFE,MTE_QFF,MTE_QNH,MOE_moyenne,MOE_rafale,MOE_direction,MOE_temp,MOE_pluie,MOE_humidite,MOE_QFE,MOE_QFF,MOE_QNH,MUB_moyenne,MUB_rafale,MUB_direction,MUB_temp,MUB_pluie,MUB_humidite,MUB_QFE,MUB_QFF,MUB_QNH,NAS_moyenne,NAS_rafale,NAS_direction,NAS_temp,NAS_pluie,NAS_humidite,NAS_QFE,NAS_QFF,NAS_QNH,NAP_moyenne,NAP_rafale,NAP_direction,NAP_temp,NAP_pluie,NAP_humidite,NAP_QFE,NAP_QFF,NAP_QNH,NEU_moyenne,NEU_rafale,NEU_direction,NEU_temp,NEU_pluie,NEU_humidite,NEU_QFE,NEU_QFF,NEU_QNH,CGI_moyenne,CGI_rafale,CGI_direction,CGI_temp,CGI_pluie,CGI_humidite,CGI_QFE,CGI_QFF,CGI_QNH,OBR_moyenne,OBR_rafale,OBR_direction,OBR_temp,OBR_pluie,OBR_humidite,OBR_QFE,OBR_QFF,OBR_QNH,AEG_moyenne,AEG_rafale,AEG_direction,AEG_temp,AEG_pluie,AEG_humidite,AEG_QFE,AEG_QFF,AEG_QNH,ORO_moyenne,ORO_rafale,ORO_direction,ORO_temp,ORO_pluie,ORO_humidite,ORO_QFE,ORO_QFF,ORO_QNH,BEH_moyenne,BEH_rafale,BEH_direction,BEH_temp,BEH_pluie,BEH_humidite,BEH_QFE,BEH_QFF,BEH_QNH,PAY_moyenne,PAY_rafale,PAY_direction,PAY_temp,PAY_pluie,PAY_humidite,PAY_QFE,PAY_QFF,PAY_QNH,PIL_moyenne,PIL_rafale,PIL_direction,PIL_temp,PIL_pluie,PIL_humidite,PIL_QFE,PIL_QFF,PIL_QNH,PIO_moyenne,PIO_rafale,PIO_direction,PIO_temp,PIO_pluie,PIO_humidite,PIO_QFE,PIO_QFF,PIO_QNH,COV_moyenne,COV_rafale,COV_direction,COV_temp,COV_pluie,COV_humidite,COV_QFE,COV_QFF,COV_QNH,PMA_moyenne,PMA_rafale,PMA_direction,PMA_temp,PMA_pluie,PMA_humidite,PMA_QFE,PMA_QFF,PMA_QNH,PLF_moyenne,PLF_rafale,PLF_direction,PLF_temp,PLF_pluie,PLF_humidite,PLF_QFE,PLF_QFF,PLF_QNH,ROB_moyenne,ROB_rafale,ROB_direction,ROB_temp,ROB_pluie,ROB_humidite,ROB_QFE,ROB_QFF,ROB_QNH,PUY_moyenne,PUY_rafale,PUY_direction,PUY_temp,PUY_pluie,PUY_humidite,PUY_QFE,PUY_QFF,PUY_QNH,QUI_moyenne,QUI_rafale,QUI_direction,QUI_temp,QUI_pluie,QUI_humidite,QUI_QFE,QUI_QFF,QUI_QNH,ROE_moyenne,ROE_rafale,ROE_direction,ROE_temp,ROE_pluie,ROE_humidite,ROE_QFE,ROE_QFF,ROE_QNH,RUE_moyenne,RUE_rafale,RUE_direction,RUE_temp,RUE_pluie,RUE_humidite,RUE_QFE,RUE_QFF,RUE_QNH,SBE_moyenne,SBE_rafale,SBE_direction,SBE_temp,SBE_pluie,SBE_humidite,SBE_QFE,SBE_QFF,SBE_QNH,HAI_moyenne,HAI_rafale,HAI_direction,HAI_temp,HAI_pluie,HAI_humidite,HAI_QFE,HAI_QFF,HAI_QNH,SAM_moyenne,SAM_rafale,SAM_direction,SAM_temp,SAM_pluie,SAM_humidite,SAM_QFE,SAM_QFF,SAM_QNH,SAG_moyenne,SAG_rafale,SAG_direction,SAG_temp,SAG_pluie,SAG_humidite,SAG_QFE,SAG_QFF,SAG_QNH,SHA_moyenne,SHA_rafale,SHA_direction,SHA_temp,SHA_pluie,SHA_humidite,SHA_QFE,SHA_QFF,SHA_QNH,SRS_moyenne,SRS_rafale,SRS_direction,SRS_temp,SRS_pluie,SRS_humidite,SRS_QFE,SRS_QFF,SRS_QNH,SCM_moyenne,SCM_rafale,SCM_direction,SCM_temp,SCM_pluie,SCM_humidite,SCM_QFE,SCM_QFF,SCM_QNH,SPF_moyenne,SPF_rafale,SPF_direction,SPF_temp,SPF_pluie,SPF_humidite,SPF_QFE,SPF_QFF,SPF_QNH,SCU_moyenne,SCU_rafale,SCU_direction,SCU_temp,SCU_pluie,SCU_humidite,SCU_QFE,SCU_QFF,SCU_QNH,SIA_moyenne,SIA_rafale,SIA_direction,SIA_temp,SIA_pluie,SIA_humidite,SIA_QFE,SIA_QFF,SIA_QNH,SIM_moyenne,SIM_rafale,SIM_direction,SIM_temp,SIM_pluie,SIM_humidite,SIM_QFE,SIM_QFF,SIM_QNH,SIO_moyenne,SIO_rafale,SIO_direction,SIO_temp,SIO_pluie,SIO_humidite,SIO_QFE,SIO_QFF,SIO_QNH,PRE_moyenne,PRE_rafale,PRE_direction,PRE_temp,PRE_pluie,PRE_humidite,PRE_QFE,PRE_QFF,PRE_QNH,STC_moyenne,STC_rafale,STC_direction,STC_temp,STC_pluie,STC_humidite,STC_QFE,STC_QFF,STC_QNH,STG_moyenne,STG_rafale,STG_direction,STG_temp,STG_pluie,STG_humidite,STG_QFE,STG_QFF,STG_QNH,SMM_moyenne,SMM_rafale,SMM_direction,SMM_temp,SMM_pluie,SMM_humidite,SMM_QFE,SMM_QFF,SMM_QNH,SBO_moyenne,SBO_rafale,SBO_direction,SBO_temp,SBO_pluie,SBO_humidite,SBO_QFE,SBO_QFF,SBO_QNH,STK_moyenne,STK_rafale,STK_direction,STK_temp,STK_pluie,STK_humidite,STK_QFE,STK_QFF,STK_QNH,SAE_moyenne,SAE_rafale,SAE_direction,SAE_temp,SAE_pluie,SAE_humidite,SAE_QFE,SAE_QFF,SAE_QNH,THU_moyenne,THU_rafale,THU_direction,THU_temp,THU_pluie,THU_humidite,THU_QFE,THU_QFF,THU_QNH,TIT_moyenne,TIT_rafale,TIT_direction,TIT_temp,TIT_pluie,TIT_humidite,TIT_QFE,TIT_QFF,TIT_QNH,UEB_moyenne,UEB_rafale,UEB_direction,UEB_temp,UEB_pluie,UEB_humidite,UEB_QFE,UEB_QFF,UEB_QNH,ULR_moyenne,ULR_rafale,ULR_direction,ULR_temp,ULR_pluie,ULR_humidite,ULR_QFE,ULR_QFF,ULR_QNH,VAD_moyenne,VAD_rafale,VAD_direction,VAD_temp,VAD_pluie,VAD_humidite,VAD_QFE,VAD_QFF,VAD_QNH,VAB_moyenne,VAB_rafale,VAB_direction,VAB_temp,VAB_pluie,VAB_humidite,VAB_QFE,VAB_QFF,VAB_QNH,VLS_moyenne,VLS_rafale,VLS_direction,VLS_temp,VLS_pluie,VLS_humidite,VLS_QFE,VLS_QFF,VLS_QNH,VEV_moyenne,VEV_rafale,VEV_direction,VEV_temp,VEV_pluie,VEV_humidite,VEV_QFE,VEV_QFF,VEV_QNH,VIO_moyenne,VIO_rafale,VIO_direction,VIO_temp,VIO_pluie,VIO_humidite,VIO_QFE,VIO_QFF,VIO_QNH,VIT_moyenne,VIT_rafale,VIT_direction,VIT_temp,VIT_pluie,VIT_humidite,VIT_QFE,VIT_QFF,VIT_QNH,VIS_moyenne,VIS_rafale,VIS_direction,VIS_temp,VIS_pluie,VIS_humidite,VIS_QFE,VIS_QFF,VIS_QNH,WFJ_moyenne,WFJ_rafale,WFJ_direction,WFJ_temp,WFJ_pluie,WFJ_humidite,WFJ_QFE,WFJ_QFF,WFJ_QNH,WYN_moyenne,WYN_rafale,WYN_direction,WYN_temp,WYN_pluie,WYN_humidite,WYN_QFE,WYN_QFF,WYN_QNH,WAE_moyenne,WAE_rafale,WAE_direction,WAE_temp,WAE_pluie,WAE_humidite,WAE_QFE,WAE_QFF,WAE_QNH,PSI_moyenne,PSI_rafale,PSI_direction,PSI_temp,PSI_pluie,PSI_humidite,PSI_QFE,PSI_QFF,PSI_QNH,ZER_moyenne,ZER_rafale,ZER_direction,ZER_temp,ZER_pluie,ZER_humidite,ZER_QFE,ZER_QFF,ZER_QNH,REH_moyenne,REH_rafale,REH_direction,REH_temp,REH_pluie,REH_humidite,REH_QFE,REH_QFF,REH_QNH,SMA_moyenne,SMA_rafale,SMA_direction,SMA_temp,SMA_pluie,SMA_humidite,SMA_QFE,SMA_QFF,SMA_QNH,KLO_moyenne,KLO_rafale,KLO_direction,KLO_temp,KLO_pluie,KLO_humidite,KLO_QFE,KLO_QFF,KLO_QNH,PFA_moyenne,PFA_rafale,PFA_direction,PFA_temp,PFA_pluie,PFA_humidite,PFA_QFE,PFA_QFF,PFA_QNH\n')
        for i in range(6):
            date = datetime.now() - timedelta(minutes=60-i*10)
            date = date.strftime('%Y%m%d%H%M')
            file.write(str(date)+',-'*1432+'\n')
def get_history_matrix(station_id: int, raw: bool):
    if wind_speed_coef == 1:
        unit = language_dict['Infos']['kph'][lang_index]
    else:
        unit = language_dict['Infos']['knots'][lang_index]
    abr = coord_station_meteosuisse[station_id-1][0]
    matrix = []
    try:
        urllib.request.urlretrieve(URL_HISTORY_MESUREMENT, 'mesurement_history.csv')
    except urllib.error.URLError:
        create_mesurement_errored_file()
    with open('mesurement_history.csv', 'r') as fichier_csv:
        reader = csv.DictReader(fichier_csv, delimiter=',')
        for row in reader:
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
        matrix.append([language_dict['Stations']['favorites_segmented_btn'][lang_index]])
        matrix.append([
            language_dict['Station_Frame']["history_title_1"][lang_index],
            language_dict['Station_Frame']["history_title_2"][lang_index],
            language_dict['Station_Frame']["history_title_3"][lang_index]
            ]
            )
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

    ax.set_xlabel(language_dict['Station_Frame']["chart_label_1"][lang_index], fontsize=10)
    ax.set_ylabel(language_dict['Station_Frame']['chart_label_2'][lang_index]+' ('+unit+')', fontsize=10)
    ax2.set_ylabel(language_dict['Station_Frame']["chart_label_3"][lang_index], fontsize=10)
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

    max_gust_point = max(y_values[1])
    try:
        threshold_hover_dist = 1/20*max_gust_point
    except:
        threshold_hover_dist = 0

    lines = []
    labels = []


    if history_bool:
        moyenne_line = ax.plot(x_numeric, y_values[0], label=language_dict['Station_Frame']['chart_legend_1'][lang_index], linewidth=2.0)[0]
        lines.append(moyenne_line)
        labels.append(language_dict['Station_Frame']['chart_legend_1'][lang_index])

        rafale_line = ax.plot(x_numeric, y_values[1], label=language_dict['Station_Frame']['chart_legend_2'][lang_index], linewidth=1.0)[0]
        lines.append(rafale_line)
        labels.append(language_dict['Station_Frame']['chart_legend_2'][lang_index])

        direction_line = ax2.plot(x_numeric, y_values[2], label=language_dict['Station_Frame']['chart_legend_3'][lang_index], linewidth=0.5, color='red', linestyle='--')[0]
        lines.append(direction_line)
        labels.append(language_dict['Station_Frame']['chart_legend_3'][lang_index])

        ax2.set_ylim(0, 360)
        ax2.set_yticks([0, 90, 180, 270, 360])
        ax2.tick_params(axis='y', which='both', length=0)
    else:
        moyenne_line = ax.plot(x_numeric, y_values[0], label=language_dict['Station_Frame']['chart_legend_4'][lang_index], linewidth=2.0)[0]
        lines.append(moyenne_line)
        labels.append(language_dict['Station_Frame']['chart_legend_4'][lang_index])

        fill_between = ax.fill_between(x_numeric, y_values[1], y_values[2], alpha=0.5, label=language_dict['Station_Frame']['chart_legend_5'][lang_index])
        lines.append(fill_between)
        labels.append(language_dict['Station_Frame']['chart_legend_5'][lang_index])

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
        logger.info('Chart motion_notify_event(), event : ' + str(event))
        if event.inaxes in (ax, ax2) and event.xdata is not None and event.ydata is not None:
            idx = min(range(len(x_numeric)), key=lambda i: abs(x_numeric[i] - event.xdata))
            if history_bool:
                try:
                    text = (f"{language_dict['Station_Frame']['chart_legend_8'][lang_index]}: {x_values[idx]}\n"
                            f"{language_dict['Station_Frame']['chart_legend_1'][lang_index]}: {y_values[0][idx]:.1f}\n"
                            f"{language_dict['Station_Frame']['chart_legend_2'][lang_index]}: {y_values[1][idx]:.1f}\n"
                            f"{language_dict['Station_Frame']['chart_legend_3'][lang_index]}: {y_values[2][idx]:.0f}°")
                except ValueError:
                    text = (f"{language_dict['Station_Frame']['chart_legend_8'][lang_index]}: - \n"
                            f"{language_dict['Station_Frame']['chart_legend_1'][lang_index]}: - \n"
                            f"{language_dict['Station_Frame']['chart_legend_2'][lang_index]}: - \n"
                            f"{language_dict['Station_Frame']['chart_legend_3'][lang_index]}: - \n")
                main_ydata = ax.transData.inverted().transform((event.x, event.y))[1]
                try:
                    dist_0 = abs(main_ydata - y_values[0][idx])
                    dist_1 = abs(main_ydata - y_values[1][idx])
                    dist_2 = abs(event.ydata - y_values[2][idx])/20 # 360° but mostly max 20kph so ~ /20

                    logger.info('all the dists')
                    logger.info(dist_0, dist_1, dist_2)

                    def set_lines_thick(moyenne, rafale, direction):
                        if moyenne:
                            moyenne_line.set_linewidth(4.0)
                        else:
                            moyenne_line.set_linewidth(2.0)
                        if rafale:
                            rafale_line.set_linewidth(4.0)
                        else:
                            rafale_line.set_linewidth(2.0)
                        if direction:
                            direction_line.set_linewidth(2.0)
                        else:
                            direction_line.set_linewidth(0.5)
                    if threshold_hover_dist > min(dist_0, dist_1, dist_2):
                        if dist_0 < min(dist_1, dist_2):
                            set_lines_thick(True, False, False)
                        elif dist_1 < min(dist_0, dist_2):
                            set_lines_thick(False, True, False)
                        elif dist_2 < min(dist_1, dist_0):
                            set_lines_thick(False, False, True)
                    else:
                        set_lines_thick(False, False, False)

                except Exception as e:
                    if str(e.__class__) == "<class 'numpy.core._exceptions._UFuncNoLoopError'>":
                        pass
                    else:
                        logger.error('Chart motion_notify_event()')
                        logger.error(e)
            else:
                text = (f"{language_dict['Station_Frame']['chart_legend_8'][lang_index]}: {x_values[idx]}\n"
                        f"{language_dict['Station_Frame']['chart_legend_4'][lang_index]}: {y_values[0][idx]:.1f}\n"
                        f"{language_dict['Station_Frame']['chart_legend_6'][lang_index]}: {y_values[1][idx]:.1f}\n"
                        f"{language_dict['Station_Frame']['chart_legend_7'][lang_index]}: {y_values[2][idx]:.1f}")
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
def toggle_star(station_id, star_button):
    if station_id_active in preferences['favorites']:
        preferences['favorites'].remove(station_id)
        star_img = star_dark_empty_img
    else:
        preferences['favorites'].append(station_id)
        star_img = star_dark_full_img
    star_button.configure(image=star_img)
    dump_preferences()
def station_frame_setup(pack: bool, station_id: int):
    logger.info(f'station_frame_setup() called -> pack: {pack}, station_id: {station_id}')
    global wind_speed_coef, station_id_active, station_frame, station_frame_active, table_frame, table_frame_active, map_active, settings_active, alphabetical_sort_box, table, fav_active, all_station_active, search_entry, entry_as_display
    station_id_active = station_id
    # try:
    #     station_frame.pack_forget()
    # except:
    #     pass
    # try:
    #     table_frame.pack_forget()
    # except: pass
    # try:
    #     map_frame.pack_forget()
    # except: pass
    # try:
    #     settings_scrollable_frame.pack_forget()
    # except: pass
    frame_navigator.forget_active_frame()
    station_frame = CTkScrollableFrame(window)

    if pack:
        station_frame.pack(fill='both', expand=True, padx=20, pady=20)
        star_frame = CTkFrame(station_frame)
        star_frame.pack(fill=X)
        
        try: 
            preferences['favorites']
        except:
            preferences['favorites'] = []
        if station_id in preferences['favorites']:
            star_img = star_dark_full_img
        else:
            star_img = star_dark_empty_img
        star_button = CTkButton(star_frame, image=star_img, text='', fg_color='transparent', hover=False, command=lambda id=station_id :[toggle_star(id, star_button)])
        star_button.pack(side=RIGHT, padx=10)
        station_name = reversed_station_dict[station_id]
        CTkLabel(station_frame, text=station_name, font=H1_FONT).pack(pady=20)
        if os == 'windows':
            pywinstyles.set_opacity(station_frame, 1)

        button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        button2.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
        button3.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)

        reload_preferences()
        if preferences['wind_speed_unit'] == 'kph':
            wind_speed_coef = 1
            unit = language_dict['Infos']['kph'][lang_index]
        else:
            wind_speed_coef = 1/1.852
            unit = language_dict['Infos']['knots'][lang_index]

        def show_history_table():
            nonlocal history_table_showed
            if not history_table_showed:
                table_history.pack(expand=True, fill="both", padx=20, pady=20)
                history_btn.configure(text=language_dict['Station_Frame']['full_data_up_btn'][lang_index])
                history_table_showed = True
            else:
                table_history.pack_forget()
                history_btn.configure(text=language_dict['Station_Frame']['full_data_down_btn'][lang_index])
                history_table_showed = False

        def show_prevision_table():
            nonlocal prevision_table_showed
            if not prevision_table_showed:
                table_prevision.pack(expand=True, fill="both", padx=20, pady=20)
                prevision_btn.configure(text=language_dict['Station_Frame']['full_data_up_btn'][lang_index])
                prevision_table_showed = True
            else:
                table_prevision.pack_forget()
                prevision_btn.configure(text=language_dict['Station_Frame']['full_data_down_btn'][lang_index])
                prevision_table_showed = False

        quick_info_frame = CTkFrame(station_frame, fg_color='transparent')
        quick_info_frame.pack(expand=True, fill="x", padx=20, pady=20)
        info, date = get_active_wind(station_id)
        try:
            moyenne = round(info[0]*wind_speed_coef, 1)
            rafale = round(info[1]*wind_speed_coef, 1)
        except:
            moyenne, rafale = info[0], info[1]
        wind_label = CTkLabel(quick_info_frame, text=f"{moyenne} | {rafale} {unit}", font=H2_FONT)
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
        direction_label = CTkLabel(quick_info_frame, text=direction_content, font=H2_FONT)
        direction_label.pack(padx=10, side=LEFT)


        arrow_img = CTkImage(arrow_img, size=(80, 80))
        image_label = CTkLabel(quick_info_frame, text='', image=arrow_img)
        image_label.pack(padx=30, side=RIGHT)

        history_frame = CTkFrame(station_frame, fg_color='transparent')
        history_frame.pack(expand=True, fill="both", padx=20, pady=20)#, side=LEFT)
        display_loading(station_frame)
        window.update()
        prevision_frame = CTkFrame(station_frame, fg_color='transparent')
        prevision_frame.pack(expand=True, fill="both", padx=20, pady=20)#, side=RIGHT)

        CTkLabel(history_frame, text=language_dict['Station_Frame']['history'][lang_index], font=H2_FONT).pack(pady=20)
        CTkLabel(prevision_frame, text=language_dict['Station_Frame']['prevision'][lang_index], font=H2_FONT).pack(pady=20)

        chart_setup(history_frame, station_id, True, unit=unit)
        history_table_showed = False
        table_history = CTkTable(history_frame, values=get_history_matrix(station_id, raw=False), header_color=BUTTON_NOT_PRESSED_COLOR)
        history_btn = CTkButton(history_frame, text=language_dict['Station_Frame']['full_data_down_btn'][lang_index], command=show_history_table)
        history_btn.pack(pady=10)


        chart_setup(prevision_frame, station_id, False, unit=unit)
        prevision_table_showed = False
        table_prevision = CTkTable(prevision_frame, values=get_prevision_matrix(station_id, raw=False), header_color=BUTTON_NOT_PRESSED_COLOR)
        prevision_btn = CTkButton(prevision_frame, text=language_dict['Station_Frame']['full_data_down_btn'][lang_index], command=show_prevision_table)
        prevision_btn.pack(pady=10)

        loading_img.pack_forget()
        # station_frame_active = True
        active_frame_manager.set_active_frame(station_frame, 'station_frame')

        # fav_active, all_station_active, table_frame_active, map_active, settings_active = False, False, False, False, False

def settings_frame_setup(pack:bool):
    logger.info(f'settings_frame_setup() called -> pack: {pack}')
    global settings_scrollable_frame, alert_frame_dict, last_alert_frame, plus_button, station_frame_active, map_active, fav_active, all_station_active, settings_active, alert_horiz_scrollframe, alert_nonscroll_frame, frame_len, frame_id_list, station_to_add
    reload_preferences()

    frame_navigator.forget_active_frame()
    settings_scrollable_frame = CTkScrollableFrame(window)
    if pack:
        alert_frame_dict = {}
        settings_scrollable_frame.pack(fill='both', expand=True, padx=20, pady=20)
        if os == 'windows':
            pywinstyles.set_opacity(settings_scrollable_frame, 1)
        settings_title = CTkLabel(settings_scrollable_frame, text=language_dict['Settings']['settings'][lang_index], font=H1_FONT)
        settings_title.pack(padx=20, pady=30)

        display_loading(settings_scrollable_frame, True)
        window.update()
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

        CTkLabel(right_plus_frame, text=language_dict['Settings']['notif_title'][lang_index], font=H2_FONT).pack(side=LEFT, expand=True, fill='x', padx=20)

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
            logger.info('stations to add', stations_to_add)
            for station in stations_to_add:
                logger.info(f'adding station Num{station}')
                add_alert_frame(station)
        def change_wind_speed_unit(e):
            global wind_speed_coef
            if e == language_dict['Infos']['kph'][lang_index]:
                preferences['wind_speed_unit'] = 'kph'
            elif e == language_dict['Infos']['knots'][lang_index]:
                preferences['wind_speed_unit'] = 'knots'
            dump_preferences()
            if e == language_dict['Infos']['kph'][lang_index]:
                wind_speed_coef = 1
            elif e == language_dict['Infos']['knots'][lang_index]:
                wind_speed_coef = 1/1.852
            button3_pressed()

        def update_location(event):
            global LOCATION, LOCATION_COORDINATES
            search_term = location_entry.get()
            headers = {'User-Agent': f'Winfo/{CURRENT_VERSION}'}#' (winfo.projet@gmail.com)'}
            url_nominatim_OSM = f'https://nominatim.openstreetmap.org/search.php?q={search_term}&format=jsonv2'
            logger.info(f'update_location url {url_nominatim_OSM}')
            try:
                r = requests.get(url_nominatim_OSM, headers=headers)
            except:
                r = None
                location_entry.delete(0, END)
                location_entry.insert(0, language_dict['Infos']['request_error'][lang_index])
            if r is not None:
                data = json.loads(r.text)

                best_importance = 0
                for response in data:
                    place_importance = response['importance']
                    if place_importance > best_importance:
                        best_importance = place_importance

                logger.info(f'best importance: {best_importance}')

                if best_importance != 0:
                    for response in data:
                        if response['importance'] == best_importance:
                            LOCATION = response['display_name']
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

        def remove_last_word_entry(*e):
            text = location_entry.get()
            last_space_index = text.rstrip().rfind(' ')  # find the last space
            if last_space_index != -1:  # if there is a space
                location_entry.delete(last_space_index+2, END)
            else:  # if there is only one word
                location_entry.delete(0, END)
        def empty_location_entry(*e):
            location_entry.delete(0, END)
        def language_menu_callback(choice):
            global lang_index
            preferences['language'] = choice
            dump_preferences()
            if choice == 'English':
                lang_index = 0
            elif choice == 'Français':
                lang_index = 1
            button1.configure(text=language_dict['Stations']['stations'][lang_index])
            button2.configure(text=language_dict['Map']['map'][lang_index])
            button3.configure(text=language_dict['Settings']['settings'][lang_index])
            button3_pressed()
        wind_speed_unit_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        wind_speed_unit_frame.pack(pady=20)
        CTkLabel(wind_speed_unit_frame, text=language_dict['Settings']['wind_unit_label'][lang_index]).pack(padx=10, side=LEFT)
        wind_speed_unit = CTkOptionMenu(wind_speed_unit_frame, values=[language_dict['Infos']['kph'][lang_index], language_dict['Infos']['knots'][lang_index]], command=change_wind_speed_unit)
        try:
            global wind_speed_coef
            if preferences['wind_speed_unit'] == 'kph':
                wind_speed_coef = 1
                wind_speed_unit.set(language_dict['Infos']['kph'][lang_index])
            else:
                wind_speed_coef = 1/1.852
                wind_speed_unit.set(language_dict['Infos']['knots'][lang_index])
        except:
            pass
        wind_speed_unit.pack(padx=10, side=RIGHT)
        location_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        location_frame.pack(pady=20)
        CTkLabel(location_frame, text=language_dict['Settings']['location_label'][lang_index]).pack(padx=10, side=LEFT)
        #CTkLabel(location_frame, text='', width=10).pack(padx=10, side=RIGHT)
        location_entry = CTkEntry(location_frame, placeholder_text=language_dict['Settings']['placeholder_location'][lang_index], width=250)
        location_entry.bind('<Return>', update_location)
        location_entry.bind('<Control-BackSpace>', remove_last_word_entry)
        location_entry.pack(padx=10, side=LEFT)
        bin_img = CTkImage(light_image=Image.open('images/bin.png'), dark_image=Image.open('images/bin.png'), size=(20, 20))
        CTkButton(location_frame, text='', image=bin_img, width=10, command=empty_location_entry).pack(side=RIGHT, padx=0)

        default_tile_server_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        default_tile_server_frame.pack(pady=20)
        CTkLabel(default_tile_server_frame, text=language_dict['Settings']['tile_server_label'][lang_index]).pack(padx=10, side=LEFT)
        default_map_tile_server = CTkOptionMenu(default_tile_server_frame, values=MAP_TILE_SERVER_LIST, command=change_default_tile_server)
        default_map_tile_server.pack(padx=10, side=RIGHT)
        try:
            default_map_tile_server.set(preferences['map_tile_server'])
        except:
            pass
        theme_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        theme_frame.pack(pady=20)
        CTkLabel(theme_frame, text=language_dict['Settings']['app_theme_label'][lang_index]).pack(padx=10, side=LEFT)
        theme_color_option_menu = CTkOptionMenu(theme_frame, values=[language_dict['Infos']['theme_system'][lang_index], language_dict['Infos']['theme_light'][lang_index], language_dict['Infos']['theme_dark'][lang_index]], command=change_theme)
        try:
            if preferences['theme'] == 'System':
                theme_color_option_menu.set(language_dict['Infos']['theme_system'][lang_index])
            elif preferences['theme'] == 'Dark':
                theme_color_option_menu.set(language_dict['Infos']['theme_dark'][lang_index])
            elif preferences['theme'] == 'Light':
                theme_color_option_menu.set(language_dict['Infos']['theme_light'][lang_index])
        except:
            theme_color_option_menu.set(language_dict['Infos']['theme_system'][lang_index])
        theme_color_option_menu.pack(padx=10)
        language_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        language_frame.pack(pady=20)
        CTkLabel(language_frame, text=language_dict['Settings']['language_label'][lang_index]).pack(side=LEFT, padx=10)
        language_option_menu = CTkOptionMenu(language_frame, values=['Français', 'English'], command=language_menu_callback)
        try:
            language_option_menu.set(preferences['language'])
        except:
            pass
        language_option_menu.pack(side=RIGHT, padx=10)
        CTkButton(settings_scrollable_frame, text=language_dict['Settings']['web_site_btn'][lang_index], command=open_website).pack(padx=20, pady=20)
        CTkLabel(settings_scrollable_frame, text=language_dict['Settings']['meteosuisse_credit_label'][lang_index]).pack(pady=20)
        CTkLabel(settings_scrollable_frame, text=language_dict['Settings']['app_version_label'][lang_index]+str(CURRENT_VERSION)).pack(pady=20)

        loading_img.pack_forget()

        active_frame_manager.set_active_frame(settings_scrollable_frame, 'settings')
        # station_frame_active = False
        # map_active = False
        # fav_active = False
        # all_station_active = False
        # settings_active = True


def add_alert_frame(*args):
    global last_alert_frame, frame_len, frame_id_list
    alert_visible = None
    shortcut_visible = None
    # try:
    #     plus_button.pack_forget()
    # except:
    #     pass
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
            logger.info('select_station_event() called -> No station selected => cannot save frame_order')
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
                logger.info('enable_alert() called -> No station selected => cannot remove wind limit')
            slider.set(25)
            value_entry.delete(0, 'end')
            if unit == language_dict['Infos']['kph'][lang_index]:
                value_entry.insert(0, str(25)+'  '+language_dict['Infos']['kph'][lang_index])
            else:
                value_entry.insert(0, str(round(25/1.852, 1))+'  '+language_dict['Infos']['knots'][lang_index])
        else:
            alert_frame_1.pack(expand=True, fill='both')
            alert_visible = True
            try:
                wind = preferences['notification'][str(station_dict[combobox.get()])]['wind_limit']*wind_speed_coef
                if wind == int(wind):
                    wind = int(wind)
                else:
                    wind = round(wind, 1)
                slider.set(wind)
                value_entry.delete(0, 'end')
                value_entry.insert(0, str(wind)+'  '+unit)
            except:
                pass
            if str(combobox.get()) in station_dict.keys():
                if not initializing_bool:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(slider.get()))
            else:
                logger.info('enable_alert() called -> No station selected => cannot save wind limit')
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
                logger.info('enable_shortcut() called -> No station selected => cannot remove shortcut')
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
            logger.info('entry_changed() called -> No station selected => cannot save wind limit')
        frame.focus()
    def slider_changed(event):
        value_entry.delete(0, 'end')
        value_entry.insert(0, str(int(slider.get()))+'  '+unit)
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(event/wind_speed_coef))
        else:
            logger.info('slider_changed() called -> No station selected => cannot save wind limit')
    def shortcut_entry_entered(event):
        if event.keysym != 'Escape':
            if event.keysym not in shortcut:
                shortcut.append(event.keysym)
        else:
            for _ in range(len(shortcut)):
                shortcut.pop(0)
        entry.delete(0, 'end')
        entry.insert(0, ' + '.join(shortcut))
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'shortcut', shortcut)
        else:
            logger.info('shortcut_entry_entered() called -> No station selected => cannot save shortcut')
    def send_alert():
        content, local_time = alert_content()

        hour, minute, date = strafe_date_from_csv(local_time=local_time)
        date = f"{hour}h{minute}  {date}"

        if wind_speed_coef == 1:
            unit = language_dict['Infos']['kph'][lang_index]
        else:
            unit = language_dict['Infos']['knots'][lang_index]
        
        img = set_icon(float(content[station_dict[combobox.get()]][0].split('|')[0]), float(content[station_dict[combobox.get()]][0].split('|')[1]))
        img = img.resize((350, 350), Image.Resampling.HAMMING)
        img = img.rotate(-int(content[station_dict[combobox.get()]][1].split('°')[0]))

        background = Image.new('RGBA', (400, 400), (0, 0, 0, 0))  # larger transparent background
        position = ((background.width - img.width) // 2,
                (background.height - img.height) // 2)
        background.paste(img, position, img)
        background.save('wind_arrow_alert.png', 'PNG')

        checkmark_img = CTkImage(light_image=Image.open('images/checkmark.png'), dark_image=Image.open('images/checkmark.png'), size=(20, 20))
        checkmark_img_label = CTkLabel(test_btn_frame, image=checkmark_img, text='')

        try:
            text_fields = [combobox.get(), content[station_dict[combobox.get()]][0] + unit + '     ' + date, content[station_dict[combobox.get()]][1]]
        except:
            text_fields = ['Veuillez selectionner une station', 'pour obtenir les données']

        if platform.system().lower() == 'windows':
            newToast = Toast()
            newToast.AddImage(ToastDisplayImage.fromPath('wind_arrow_alert.png'))
            # ToastImagePosition('appLogoOverride')

            newToast.text_fields = text_fields
            #check.pack() in def activated_callback()

            # toaster = InteractableWindowsToaster('Winfo') # for the btns but very high
            toaster = WindowsToaster('Winfo') # without btn but nicer
        elif platform.system().lower() == 'linux':
            subprocess.Popen(['notify-send', 'Winfo', '\n'.join(text_fields)], '-i wind_arrow_alert.png')
        elif platform.system().lower() == 'darwin':
            subprocess.run(["osascript", "-e", '\n'.join(text_fields)], check=True)

        def activated_callback(activatedEventArgs: ToastActivatedEventArgs):
            if activatedEventArgs.arguments == 'delete':
                toaster.remove_toast(newToast)
            elif activatedEventArgs.arguments == 'snooze':
                pass # logger.info('snooze (TODO)') # TODO
            else:
                checkmark_img_label.pack(side=LEFT, padx=10, pady=10)
        
        '''
        # needs to be InteractableWindowsToaster()
        newToast.AddAction(ToastButton('Supprimer', 'delete'))
        newToast.AddAction(ToastButton('Bloquer pour 1h', 'snooze'))
        '''

        newToast.on_activated = activated_callback

        toaster.show_toast(newToast)
        logger.info('notification sent to', combobox.get())
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
    title_lab = CTkLabel(cross_frame, text=language_dict['Settings']['notif_card_title'][lang_index] + str(frame_id))
    title_lab.pack(side=LEFT, expand=True, padx=10)
    values = station_list[:]
    values.insert(0, language_dict['Settings']['notif_card_combobox'][lang_index])

    combobox = CTkOptionMenu(frame, values=values, width=200, command=select_station_event)
    combobox.pack(padx=10, pady=10)

    CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text=language_dict['Settings']['notif_card_option_1_title'][lang_index], width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover_color=LIGHT_3, hover=False, command=enable_alert).pack()
    alert_frame = CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=50)
    alert_frame.pack()
    alert_frame_1 = CTkFrame(alert_frame, fg_color=(LIGHT_3, DARK_3))
    if preferences['wind_speed_unit'] == 'kph':
        unit = language_dict['Infos']['kph'][lang_index]
        wind_speed_coef = 1
    else:
        unit = language_dict['Infos']['knots'][lang_index]
        wind_speed_coef = 1/1.852
    CTkLabel(alert_frame_1, text=language_dict['Settings']['notif_card_option_1_label'][lang_index]).pack()
    value_and_slider_frame = CTkFrame(alert_frame_1, fg_color='transparent', corner_radius=50)
    value_and_slider_frame.pack(padx=10, pady=5)
    slider = CTkSlider(value_and_slider_frame, from_=0, to=50, number_of_steps=30, command=slider_changed)
    slider.pack(padx=5, pady=5, side=RIGHT)
    font_on_blue_color = combobox.cget('text_color') # TODO set and use a defined global variable
    value_entry = CTkEntry(value_and_slider_frame, text_color=font_on_blue_color, width=100, justify=CENTER, fg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=50)
    value_entry.insert(0, str(int(slider.get()))+'  '+unit)
    value_entry.bind('<Button-1>', select_entry)
    value_entry.bind("<Return>", entry_changed)
    value_entry.pack(padx=5, pady=5, side=LEFT)

    CTkFrame(frame, fg_color=(DARK_1, LIGHT_1), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text=language_dict['Settings']['notif_card_option_2_title_1'][lang_index], width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover=False, corner_radius=10, command=enable_shortcut).pack()
    CTkButton(frame, text=language_dict['Settings']['notif_card_option_2_title_2'][lang_index], width=300, font=h2_font, fg_color='transparent', text_color=(DARK_3, LIGHT_3), hover=False, command=enable_shortcut).pack()
    shortcut_frame = CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=50)
    shortcut_frame.pack()
    shortcut_frame_1 = CTkFrame(shortcut_frame, fg_color=(LIGHT_3, DARK_3))
    CTkLabel(shortcut_frame_1, text='', height=15).pack()
    entry = CTkEntry(shortcut_frame_1, width=250, placeholder_text=language_dict['Settings']['placeholder_option_2'][lang_index])
    entry.bind("<KeyPress>", shortcut_entry_entered)
    entry.pack(padx=10, pady=10)

    test_btn_frame = CTkFrame(frame, fg_color='transparent')
    test_btn_frame.place(rely=0.92, relx=0.5, anchor=CENTER)
    CTkButton(test_btn_frame, text=language_dict['Settings']['notif_card_test_btn'][lang_index], width=60, command=send_alert).pack(side=RIGHT, padx=10, pady=10)

    skip = False
    if args == ():
        skip = True
    if not skip:
        reload_preferences()
        station_to_add = args[0]
        title_lab.configure(text=language_dict['Settings']['notif_card_title'][lang_index]+str(preferences['notification'][station_to_add]['frame_order']))
        logger.info(station_to_add, values[int(station_to_add)], f'\n -> {coord_station_meteosuisse[int(station_to_add)-1] = } ')
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
    logger.info(f'preferences["notification"][{station_id}] -> type: {type}, value: {value}')
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
def update_tab_button_color():
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    button1.configure(fg_color=BUTTON_NOT_PRESSED_COLOR)
    
    if active_frame_manager.active_frame_type == 'fav_station' or active_frame_manager.active_frame_type == 'all_station':
        button1.configure(fg_color=BUTTON_PRESSED_COLOR)
def left_arrow_button_pressed():
    frame_navigator.go_back()
def right_arrow_button_pressed():
    frame_navigator.go_forward()
def launch_customtkinter(*args):
    global preferences, station_id_active, station_frame_active, map_active, fav_active, all_station_active, settings_active, wind_sorted_btn_activated, wind_speed_coef, LOCATION, LOCATION_COORDINATES, LATEST_VERSION, LATEST_VERSION_INFO, h1_font, h2_font, p_font, station_dict, abreviation_list, station_list, button1, button2, button3, last_frames_closed, last_frames_closed_txt, retrieve_frame_index, star_dark_full_img, star_dark_empty_img, star_light_full_img, star_light_empty_img
    # station_frame_active = map_active = fav_active = all_station_active = settings_active = False
    wind_sorted_btn_activated = False
    station_id_active = 1
    reload_preferences()
    last_frames_closed = []
    last_frames_closed_txt = []
    retrieve_frame_index = 0

    if wind_speed_coef == 1:
        preferences['wind_speed_unit'] = 'kph'
    else:
        preferences['wind_speed_unit'] = 'knots'
    dump_preferences()

    window.bind('<Alt-Left>', frame_navigator.go_back)
    window.bind('<Alt-Right>', frame_navigator.go_forward)
    def set_location_by_ip():
        try:
            ip_location = geocoder.ip('me')
            preferences['location'] = []
            preferences['location'].append(ip_location.city) # index : 0
            preferences['location'].append(ip_location.lat) # index : 1
            preferences['location'].append(ip_location.lng) # index : 2
            preferences['location'].append('created_by_ip') # index : 3
            dump_preferences()

        except:
            pass
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

    star_dark_full_img = CTkImage(Image.open('images/star_full_dark.png'), size=(40, 40))
    star_dark_empty_img = CTkImage(Image.open('images/star_empty_dark.png'), size=(40, 40))
    star_light_full_img = CTkImage(Image.open('images/star_full_light.png'), size=(40, 40))
    star_light_empty_img = CTkImage(Image.open('images/star_empty_light.png'), size=(40, 40))


    left_column_frame = CTkFrame(window, width=150, height=window.winfo_screenheight())
    left_column_frame.pack(side="left", fill="y")
    if os == 'windows':
        pywinstyles.set_opacity(left_column_frame, 1)

    arrow_btn_frame = CTkFrame(left_column_frame, fg_color='transparent')
    arrow_btn_frame.pack()
    left_arrow_button = CTkButton(arrow_btn_frame, text='<', command=left_arrow_button_pressed, width=60)
    left_arrow_button.pack(side=LEFT, padx=10, pady=10)

    right_arrow_button = CTkButton(arrow_btn_frame, text='>', command=right_arrow_button_pressed, width=60)
    right_arrow_button.pack(side=RIGHT, padx=10, pady=10)

    button1 = CTkButton(left_column_frame, text=language_dict['Stations']['stations'][lang_index], command=button1_pressed)
    button1.pack(padx=20, pady=10)

    button2 = CTkButton(left_column_frame, text=language_dict['Map']['map'][lang_index], command=button2_pressed)
    button2.pack(padx=20, pady=10)

    button3 = CTkButton(left_column_frame, text=language_dict['Settings']['settings'][lang_index], command=button3_pressed)
    button3.pack(padx=20, pady=10)

    frame_navigator.button1 = button1
    frame_navigator.button2 = button2
    frame_navigator.button3 = button3

    if 'theme' in preferences.keys():
        set_appearance_mode(preferences['theme'])
        logger.info(f'preferences["theme"] = {preferences["theme"]}')
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
        logger.error(error)
        LATEST_VERSION = 'error'
    start_version_top_level = False
    logger.info('Version check :')
    if CURRENT_VERSION == LATEST_VERSION:
        logger.info(f'you are on the latest version ({CURRENT_VERSION})')
    elif LATEST_VERSION == 'error':
        logger.info(f'you are on version {CURRENT_VERSION} but cannot check latest version')
    else:
        logger.info(f'not the last version, you are on version {CURRENT_VERSION} and the latest version is {LATEST_VERSION}')
        if 'not_show_update' not in preferences.keys():
            start_version_top_level = True
    get_csv()
    button1_pressed()
    if first_boot:
        preferences = winfo_import_json_preferences.start_importation_toplevel(window)
        create_shortcut_top_level()
    if start_version_top_level:
        new_version_top_level()

    if os == 'windows':
        pywinstyles.apply_style(window, 'acrylic')
        
        pywinstyles.set_opacity(window, 0.9)

        window.configure(fg_color=(WINDOW_BACKGROUND_LIGHT, WINDOW_BACKGROUND_DARK))
    window.mainloop()

if __name__ == "__main__":
    window = CTk()
    window.geometry("1200x800+200+50")
    window.title(f'Winfo {CURRENT_VERSION}')

    launch_customtkinter()