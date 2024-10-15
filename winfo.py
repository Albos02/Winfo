from customtkinter import *
import tkintermapview
from CTkTable import CTkTable
import tkintermapview
import requests, urllib.request, csv, json, webbrowser
import geocoder
from math import sqrt
from winfo_import import *
from PIL import Image, ImageTk
from windows_toasts import Toast, WindowsToaster


def new_version_top_level():
    global toplevel
    toplevel = CTkToplevel(window)
    toplevel.title('Nouvelle version')
    toplevel.geometry('440x280+800+300')
    CTkLabel(toplevel, text="Nouvelle version disponible !", font=h1_font).pack(padx=20, pady=40)
    CTkLabel(toplevel, text=f'La dernière version est {LATEST_VERSION}', font=h2_font).pack(padx=20, pady=20)
    CTkButton(toplevel, text="Télécharger", command=open_new_version).pack(padx=20, pady=20)
    CTkButton(toplevel, text='Ne plus afficher', command=ne_plus_afficher).place(relx=0.675, rely=0.89)
    toplevel.after(200, toplevel.focus)
def open_new_version():
    webbrowser.open("https://louse-proud-raven.ngrok-free.app/")
    toplevel.destroy()
def ne_plus_afficher():
    toplevel.destroy()
    reload_preferences()
    preferences['not_show_update'] = True
    dump_preferences()
def create_file_to_send_alert(station): #only for the background scripts
    with open('need_to_send_alert_is_true_.txt', 'w') as f:
        f.write(str(station))
        print('added ', station)
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
        urllib.request.urlretrieve(URL, "VQHA80.csv")
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
    if fav_active:
        table_frame_setup(pack=True, fav_bool=True, wind_sorted=wind_sorted_btn_activated)
    if all_station_active:
        table_frame_setup(pack=True, fav_bool=False, wind_sorted=wind_sorted_btn_activated)
    if settings_active:
        print("updating values.. but in settings so idk what to do...")
        #settings_frame_setup(True)


def change_theme(theme):
    print('theme is ' + theme)
    global active_theme
    if theme == "Système":
        theme = "System"
    elif theme == "Sombre":
        theme = "Dark"
    else:
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

def set_icon(moyenne, rafale):
    if moyenne < 3:
        pixel_values = (255, 255, 255, 255)
    elif moyenne < 10:
        force_couleur = int(moyenne-3/7 * 255)
        pixel_values = (255-force_couleur, 255, 255-force_couleur, 255)
    elif moyenne <= 60:
        force_couleur = int((moyenne-10)/50 * 255)
        pixel_values = (force_couleur, 255-force_couleur, 0, 255)
    else:
        pixel_values = (255, 0, 0, 255)

    im = Image.open('wind_arrow.png').convert('RGBA')
    width, height = im.size
    data = list(im.getdata())

    new_image = Image.new("RGBA", (width, height))
    new_data = []
    for pixel in data:
        if pixel == (255, 0, 0, 255):
            new_pixel = pixel_values
            new_data.append(new_pixel)
        elif pixel == (0, 0, 0, 255):
            new_pixel = pixel
            new_data.append(new_pixel)
        else:
            new_pixel = (0, 0, 0, 0)
            new_data.append(new_pixel)

    new_image.putdata(new_data)
    #new_image.show()
    return new_image
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
        tile_server = 'https://api.maptiler.com/maps/cadastre/256/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' #cadastre maptile 256x256  'https://api.maptiler.com/maps/cadastre/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' 512x512
    elif tile_server == 'Streets Maptiler':
        tile_server = 'https://api.maptiler.com/maps/streets-v2/256/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' #maptileropenstreets-v2 256x256 'https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=SuQlGsYDvIMdJTP1qEWT' 512x512
    elif tile_server == 'OpenStreetMap':
        tile_server = 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png' #openstreetmap #default
    elif tile_server == 'Google':
        tile_server = 'https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga' # google
    elif tile_server == 'Google Earth':
        tile_server = 'https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga'# google earth
    map_widget.set_tile_server(tile_server)
def map_frame_setup(pack: bool, displaying_values : bool):
    global map_frame, map_widget, map_active, fav_active, all_station_active, settings_active
    print('starting map, pack = ', pack)
    try:
        map_frame.pack_forget()
    except:
        pass
    map_frame = CTkFrame(window)
    def display_values():
        map_frame_setup(pack=True, displaying_values=display_values_switch.get())

    if pack:
        map_options_frame = CTkFrame(map_frame, bg_color='transparent', fg_color='transparent')
        map_options_frame.pack(fill="x", expand=False, padx=10, pady=0)
        titre_carte = CTkLabel(map_options_frame, text="Carte des Stations", font=h1_font)
        titre_carte.pack(pady=20)
        display_loading(map_frame)
        map_frame.pack(fill='both', expand=True, padx=20, pady=10)
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
        try:
            urllib.request.urlretrieve(URL_WIND, "ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv")
            urllib.request.urlretrieve(URL_WIND_RAFALE, "ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv")
        except:
            with open('ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv', 'w') as f:
                f.write('')
            with open('ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv', 'w') as f:
                f.write('')
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
                    if line['Abr.'] == coor[0]:
                        print(content_moyenne[i])
                        for j in content_moyenne[i].keys():
                            if 'Direction du vent' in j:
                                try:
                                    direction = int(-float(content_moyenne[i][j]))
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
                                direction = content_rafale[i]['Direction du vent']
                            except KeyError:
                                direction = 0
                        break
            elif direction is None or moyenne is None or rafale is None:
                if direction is None:
                    direction = 0
                if rafale is None or moyenne is None:
                    moyenne = '-'
                    rafale = '-'


            vent = str(moyenne) + '/' + str(rafale)
            if moyenne == '-' and rafale == '-':
                new_image = Image.open('cross.png')
                icon = ImageTk.PhotoImage(new_image.resize((15, 15)))
            else:
                new_image = set_icon(moyenne, rafale)
                icon = ImageTk.PhotoImage(new_image.rotate(direction).resize((25, 25)))
            if not displaying_values:
                vent = ''
            map_widget.set_marker(float(coor[1]), float(coor[2]), text=vent, text_color="black", icon=icon)

        map_widget.set_position(float(LOCATION_COORDINATES[0]), float(LOCATION_COORDINATES[1]))
        map_widget.set_zoom(8)#7
        loading_img_label.pack_forget()
        map_widget.pack(fill="both", expand=True, padx=10)
        print('all packed up')
        map_active = True
        fav_active = False
        all_station_active = False
        settings_active = False


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
    '''Distance (km) = √((lat2 - lat1)^2 * 111.32^2 + (lon2 - lon1)^2 * 111.32^2 * cos((lat1 + lat2)/2))'''
    '''distance = sqrt(((a - c)^2) + ((b - d)^2))

        a, b = coordonnées point question

        c, d = coordonnées centre

        distance = distance entre les deux points'''
    pos_lat, pos_lon, station_lat, station_lon = float(pos_lat), float(pos_lon), float(station_lat), float(station_lon)
    distance = sqrt(((pos_lat - station_lat) ** 2) + ((pos_lon - station_lon) ** 2))
    output = round(distance * 91.8855029586, 5)
    return output
def get_station_matrix(fav_bool: bool, wind_sorted: bool):
    with open("VQHA80.csv", "r") as f_csv:
        reader = csv.DictReader(f_csv, delimiter=';')
        values = []
        search_input = search_entry.get().lower()
        reload_preferences()
        with open("coord_station_meteosuisse.json", "r") as f_json:
            coord_reader = json.load(f_json)
            print(LOCATION_COORDINATES[0], '|', LOCATION_COORDINATES[1])
            for ligne, coord in zip(reader, coord_reader):
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
                    if wind_speed_coef == 1:
                        new_line.append(f'{str(vent)} / {str(rafale)}  km/h')
                    else:
                        new_line.append(f'{str(vent)} / {str(rafale)}  noeuds')
                except ValueError:
                    new_line.append('')
                try:
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
                except ValueError:
                    if 'error' in ligne['dkl010z0']:
                        new_line.append(ligne['dkl010z0'])
                    else:
                        new_line.append('')
                new_line.append(coord[4])
                if 'favorites' in preferences.keys():
                    if coord[5] in preferences['favorites']:
                        new_line.append('⬛')
                    else:
                        new_line.append('⬜')
                else:
                    new_line.append('⬜')
                values.append(new_line)
            if wind_sorted:
                values = sorted(values, key=lambda item_in_values: (-5 if item_in_values[1] == '' else float(item_in_values[1].split('/')[0])), reverse=True)
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
def empty_search(e): #called if backspace is pressed. So checking if Ctrl is pressed. if so, empty search
    global search_input
    if e.state == 12: #state 12 is control
        search_input = ''
        search_entry.delete(0, 'end')



def table_frame_setup(pack: bool, fav_bool: bool, wind_sorted: bool):
    global table_frame, table_frame_active, map_active, settings_active, alphabetical_sort_box, table, fav_active, all_station_active, search_entry, entry_as_display
    try:
        table_frame.pack_forget()
    except:
        pass
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
    display_loading(table_frame)
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
        if column == 4:
            reload_preferences()
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
        except ValueError: #si un caractère pas nombre, un prends tous les chiffres avant le caractère
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
            entry_as_display.configure(placeholder_text=f'N/A')
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
            entry_as_display.configure(placeholder_text=f'N/A')
        else:
            entry_as_display.configure(placeholder_text=f'{value} KM')
        preferences['distance_slider'] = value
        dump_preferences()

    set_segmented_btn(fav_bool=fav_bool)
    alphabetical_sort_box = CTkCheckBox(table_frame, text="Ordre alphabétique", command=changed_wind_sorted)
    if not wind_sorted: alphabetical_sort_box.select()
    alphabetical_sort_box.pack()
    scrollframe = CTkScrollableFrame(table_frame)
    scrollframe.pack(expand=True, fill="both", padx=20, pady=20)
    distance_slider_and_search_frame = CTkFrame(scrollframe, fg_color='transparent')
    distance_slider_and_search_frame.pack(pady=10)
    CTkLabel(distance_slider_and_search_frame, text=f"Rayon d'affichage autour de : {LOCATION.upper()}", width=100).pack(side=LEFT, padx=10)
    entry_as_display = CTkEntry(distance_slider_and_search_frame, placeholder_text="", width=80)
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
        entry_as_display.configure(placeholder_text=f'N/A')
    else:
        entry_as_display.configure(placeholder_text=f'{value} KM')
    entry_as_display.pack(padx=10, side=LEFT)
    distance_slider = CTkSlider(distance_slider_and_search_frame, from_=10, to=500, command=distance_slider_changed)
    distance_slider.set(value)
    distance_slider.bind("<ButtonRelease-1>", setup_table_stations)

    distance_slider.pack(padx=10, side=LEFT)
    CTkLabel(distance_slider_and_search_frame, text="", width=20).pack(side=LEFT, padx=20)
    search_entry = CTkEntry(distance_slider_and_search_frame, placeholder_text="Rechercher une station", width=300)
    search_entry.bind('<BackSpace>', empty_search)
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
    map_active, settings_active = False, False

def settings_frame_setup(pack:bool):
    global settings_scrollable_frame, alert_frame_dict, last_alert_frame, plus_button, map_active, fav_active, all_station_active, settings_active, alert_horiz_scrollframe, alert_nonscroll_frame, frame_len, frame_id_list, station_to_add
    reload_preferences()
    try:
        settings_scrollable_frame.pack_forget()
    except:
        pass
    settings_scrollable_frame = CTkScrollableFrame(window)
    if pack:
        alert_frame_dict = {}
        settings_scrollable_frame.pack(fill='both', expand=True, padx=20, pady=20)
        settings_title = CTkLabel(settings_scrollable_frame, text="Paramètres", font=h1_font)
        settings_title.pack(padx=20, pady=30)


        empty = True
        stations_to_add = []
        for i in range(1, 10):
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

        plus_image = CTkImage(light_image=Image.open('plus.png'), dark_image=Image.open('plus.png'), size=(30, 30))
        right_plus_icon_btn = CTkButton(right_plus_frame, text='', image=plus_image, fg_color='transparent', hover=False, command=add_alert_frame)
        right_plus_icon_btn.pack(side=RIGHT)
        frame_for_scroll_or_not_frame = CTkFrame(settings_scrollable_frame)
        frame_for_scroll_or_not_frame.pack(expand=True, fill='both')
        alert_horiz_scrollframe = CTkScrollableFrame(frame_for_scroll_or_not_frame, fg_color=(LIGHT_2, DARK_2), corner_radius=20, height=500, orientation='horizontal')#, border_color='red', border_width=1)#, ) #add transform to CTkScrollableFrame()   #fg_color=('#C0C0C0', '#333333')
        if empty:
            alert_nonscroll_frame = CTkFrame(frame_for_scroll_or_not_frame, fg_color=(LIGHT_2, DARK_2), corner_radius=20, height=500)
            alert_nonscroll_frame.pack(expand=True, fill='x', padx=20, pady=20)
            big_plus_image = CTkImage(light_image=Image.open('plus.png'), dark_image=Image.open('plus.png'), size=(200, 200))
            plus_button = CTkButton(alert_nonscroll_frame, text='', image=big_plus_image, fg_color='transparent', hover=False, command=add_alert_frame)
            plus_button.pack(anchor='center', pady=100)
        else:
            alert_horiz_scrollframe.pack(expand=True, fill='x', padx=20, pady=20)
            for station in stations_to_add:
                print(f'adding station Num{station}')
                add_alert_frame(station)
        def change_wind_speed_unit(e):
            global wind_speed_coef
            print(e)
            preferences['wind_speed_unit'] = e
            dump_preferences()
            if e == 'km/h':
                wind_speed_coef = 1
            elif e == 'noeuds':
                wind_speed_coef = 1/1.852

        def update_location(event):
            global LOCATION, LOCATION_COORDINATES
            city = location_entry.get()
            url_location = f'https://nominatim.openstreetmap.org/search.php?city={city}&format=jsonv2'
            r = requests.get(url_location)
            print(r.text)
            data = r.json()
            last_name = ''
            for response in data:
                if len(last_name) > len(response['name']) or last_name == '':
                    last_name = response['name']
                    last_coord = (response['lat'], response['lon'])

            LOCATION = last_name
            LOCATION_COORDINATES = last_coord
            preferences['location'][0] = LOCATION
            preferences['location'][1], preferences['location'][2] = LOCATION_COORDINATES
            preferences['location'][3] = 'created_by_user'
            dump_preferences()

        def empty_location(e):# called when backspace. so checking if Ctrl is pressed. if so, empty the entry
            print(e)
            if e.state == 12: #state of control = 12
                location_entry.delete(0, END)
        wind_speed_unit_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        wind_speed_unit_frame.pack(pady=20)
        CTkLabel(wind_speed_unit_frame, text='Unité de mesure').pack(padx=10, side=LEFT)
        wind_speed_unit = CTkOptionMenu(wind_speed_unit_frame, values=['km/h', 'noeuds'], command=change_wind_speed_unit)
        try:
            wind_speed_unit.set(preferences['wind_speed_unit'])
        except:
            wind_speed_unit.set('km/h')
        wind_speed_unit.pack(padx=10, side=RIGHT)
        location_frame = CTkFrame(settings_scrollable_frame, fg_color='transparent')
        location_frame.pack(pady=20)
        CTkLabel(location_frame, text='Entrez votre ville pour une localistation précise').pack(padx=10, side=LEFT)
        location_entry = CTkEntry(location_frame, placeholder_text='Lieu')
        location_entry.bind('<Return>', update_location)
        location_entry.bind('<BackSpace>', empty_location)
        location_entry.pack(padx=10, side=RIGHT)
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
            theme_color_option_menu.set(preferences['theme'])
        except:
            theme_color_option_menu.set('Système')
        theme_color_option_menu.pack(padx=10)
        CTkButton(settings_scrollable_frame, text='Accédez au site web', command=open_website).pack(padx=20, pady=20)
        CTkLabel(settings_scrollable_frame, text='Toutes les données affichées sont mises à disposition par MétéoSuisse').pack(pady=20)
        CTkLabel(settings_scrollable_frame, text=f"Version de l'application : {CURRENT_VERSION}").pack(pady=20)

        map_active = False
        fav_active = False
        all_station_active = False
        settings_active = True


def add_alert_frame(*args):
    global last_alert_frame, frame_len, frame_id_list
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
                    update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(slider.get()))
            except:
                pass
            try:
                if shortcut_visible:
                    update_alert_preferences(str(station_dict[combobox.get()]), 'shortcut', shortcut)
            except:
                pass
        else:
            print('No station selected -> cannot save frame_order')
    def enable_alert():
        global alert_visible
        try:
            a = alert_visible
        except:
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
            value_entry.insert(0, '25  km/h')
        else:
            alert_frame_1.pack(expand=True, fill='both')
            alert_visible = True
            try:
                slider.set(preferences['notification'][str(station_dict[combobox.get()])]['wind_limit'])
                value_entry.delete(0, 'end')
                value_entry.insert(0, str(int(slider.get()))+'  km/h')
            except:
                pass
            if str(combobox.get()) in station_dict.keys():
                update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(slider.get()))
            else:
                print('No station selected -> cannot save wind limit')
    def enable_shortcut():
        global shortcut_visible
        try:
            a = shortcut_visible
        except:
            shortcut_visible = False
        if shortcut_visible:
            shortcut_frame_1.pack_forget()
            shortcut_frame.configure(height=50)
            if str(combobox.get()) in station_dict.keys():
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
        except ValueError: #si une virgule à la place d'un point
            try:
                value = int(value_entry.get().split(',')[0]) + float(value_entry.get().split(',')[1])/(10**len(value_entry.get().split(',')[1]))
            except:
                value = float('')
        value_entry.delete(0, 'end')
        if value == int(value): #si entier, pas de 0 après
            value_entry.insert(0, str(int(value))+'  km/h')
        else:
            value_entry.insert(0, str(value)+'  km/h')
        slider.set(int(value))
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', value)
        else:
            print('No station selected -> cannot save wind limit')
        frame.focus()
    def slider_changed(event):
        print(int(event))
        value_entry.delete(0, 'end')
        value_entry.insert(0, str(int(slider.get()))+'  km/h')
        if str(combobox.get()) in station_dict.keys():
            update_alert_preferences(str(station_dict[combobox.get()]), 'wind_limit', int(event))
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
        content = alert_content()

        newToast = Toast()
        checkmark_img = CTkImage(light_image=Image.open('checkmark.png'), dark_image=Image.open('checkmark.png'), size=(20, 20))
        checkmark_img_label = CTkLabel(test_btn_frame, image=checkmark_img, text='')

        try:
            newToast.text_fields = [combobox.get(), content[station_dict[combobox.get()]][0] + '   ' + content[station_dict[combobox.get()]][1]]
        except KeyError:
            newToast.text_fields = ['Veuillez selectionner une station', 'pour obtenir les données']
        newToast.on_activated = lambda _:[checkmark_img_label.pack(side=LEFT, padx=10, pady=10), print('Les notifications fonctionnent !')]
        
        WindowsToaster('Winfo').show_toast(newToast)
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
    cross_image = CTkImage(light_image=Image.open('cross.png'), dark_image=Image.open('cross.png'), size=(30, 30))
    cross_button = CTkButton(cross_frame, text='', width=30, image=cross_image, fg_color='transparent', hover=False, command=remove_alert_frame)
    cross_button.pack(side=RIGHT, fill='y', padx=20)
    title_lab = CTkLabel(cross_frame, text='Notification ' + str(frame_id))
    title_lab.pack(side=LEFT, expand=True, padx=10)
    values = station_list[:]
    values.insert(0, 'Sélectionnez une station')

    combobox = CTkOptionMenu(frame, values=values, width=200, command=select_station_event)
    combobox.pack(padx=10, pady=10)

    CTkFrame(frame, fg_color=(DARK_1, LIGHT_1), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text='Créer une alerte : ', width=300, font=h2_font, fg_color=(LIGHT_3, DARK_3), hover=False, command=enable_alert).pack()
    alert_frame = CTkFrame(frame, fg_color=(LIGHT_3, DARK_3), height=50)
    alert_frame.pack()
    alert_frame_1 = CTkFrame(alert_frame, fg_color=(LIGHT_3, DARK_3))
    CTkLabel(alert_frame_1, text='Déterminez un vent moyen minimum :').pack()
    value_and_slider_frame = CTkFrame(alert_frame_1, corner_radius=50)
    value_and_slider_frame.pack(padx=10, pady=5)
    slider = CTkSlider(value_and_slider_frame, from_=0, to=50, number_of_steps=30, command=slider_changed)
    slider.pack(padx=5, pady=5, side=RIGHT)
    value_entry = CTkEntry(value_and_slider_frame, width=83, justify=CENTER, fg_color=BUTTON_NOT_PRESSED_COLOR, corner_radius=50)
    value_entry.insert(0, str(int(slider.get()))+'  km/h')
    value_entry.bind('<Button-1>', select_entry)
    value_entry.bind("<Return>", entry_changed)
    value_entry.pack(padx=5, pady=5, side=LEFT)



    CTkFrame(frame, fg_color=(DARK_1, LIGHT_1), height=1).pack(padx=30, pady=10, fill='x') #thin line
    CTkButton(frame, text='Ajouter un raccourcis clavier', width=300, font=h2_font, fg_color='transparent', hover=False, corner_radius=10, command=enable_shortcut).pack()
    CTkButton(frame, text='pour afficher le vent :', width=300, font=h2_font, fg_color='transparent', hover=False, command=enable_shortcut).pack()
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
        combobox.set(values[int(station_to_add)])
        value_entry.delete(0, 'end')
        value_entry.insert(0, str(int(slider.get()))+'  km/h')
        entry.delete(0, 'end')
        try:
            try:
                value_entry.insert(0, str(preferences['notification'][station_to_add]['wind_limit']))
            except KeyError:
                pass
            slider.set(preferences['notification'][station_to_add]['wind_limit'])
            enable_alert()
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
    print(f'preferences["notification"][{station_id}]')
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
    global preferences, map_active, fav_active, all_station_active, settings_active, wind_sorted_btn_activated, wind_speed_coef, LOCATION, LOCATION_COORDINATES, LATEST_VERSION, h1_font, h2_font, p_font, station_dict, abreviation_list, station_list, button1, button2, button3
    map_active, fav_active, all_station_active, settings_active = False, False, False, False
    wind_sorted_btn_activated = False


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

    get_csv()

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
        change_theme(preferences['theme'])
    
    map_frame_setup(pack=False, displaying_values=True)
    table_frame_setup(pack=False, fav_bool=False, wind_sorted=False)
    settings_frame_setup(pack=False)
    try:
        LATEST_VERSION = float(requests.get('https://louse-proud-raven.ngrok-free.app/last_version.json').text)
    except:
        LATEST_VERSION = 'error'
    if CURRENT_VERSION == LATEST_VERSION:
        print("you're on the latest version")
    elif LATEST_VERSION == 'error':
        print("you're on version " + str(CURRENT_VERSION) + 'but cannot check latest version')
    else:
        print('not the last version', 'you are on version ' + str(CURRENT_VERSION) + ' and the latest version is ' + str(LATEST_VERSION))
        if 'not_show_update' not in preferences.keys():
            new_version_top_level()

    button1_pressed()
    window.mainloop()

window = CTk()
window.geometry("1200x800+200+50")
window.title(f'Winfo {CURRENT_VERSION}')


if __name__ == "__main__":
    launch_customtkinter()