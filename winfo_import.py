import json, csv, time, pytz, subprocess, platform
if platform.system() == 'windows':
    from windows_toasts import Toast, WindowsToaster, ToastDisplayImage
from datetime import datetime
import tzlocal
from PIL import Image


CURRENT_VERSION = 1.3
URL_WIND_SPEED = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_fr.csv'
URL_WIND_GUST = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_fr.csv'
URL_VQHA80 = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'
SERVER_URL = 'https://louse-proud-raven.ngrok-free.app/'
URL_HISTORY_MESUREMENT = SERVER_URL + 'data/mesurement_history.csv'


BUTTON_PRESSED_COLOR = '#144870'
BUTTON_NOT_PRESSED_COLOR = '#1c72b0'
BUTTON_HOVER_AND_PRESSED_COLOR = '#203a4f'
LIGHT_1 = '#666666' #scrollbar
DARK_1 = '#878787' #scrollbar
LIGHT_2 = '#C0C0C0' #custom frame
DARK_2 = '#333333' #custom frame
LIGHT_3 = '#d9d9d9' #classic frame
DARK_3 = '#2b2b2b' #classic frame
LIGHT_34 = '#d7d7d7'
DARK_34 = '#282828'
LIGHT_4 = '#ebebeb' #background
DARK_4 = '#242424' #background

MAP_TILE_SERVER_LIST = ['Swisstopo', 'Swisstopo Satellite', 'Cadastre Maptiler', 'Streets Maptiler', 'OpenStreetMap', 'Google', 'Google Earth']
latest_date = None

with open('conversion_key_tkinter_to_keyboard.json', 'r') as file:
    conversion_key_tkinter_keyboard = json.load(file)
def create_errored_file(error):
    GMT_datetime = f'{time.gmtime().tm_year}{time.gmtime().tm_mon}{time.gmtime().tm_mday}{time.gmtime().tm_hour}{round(time.gmtime().tm_min, -1)}'
    with open('VQHA80.csv', 'w') as f:
        f.write('Station/Location;Date;tre200s0;rre150z0;sre000z0;gre000z0;ure200s0;tde200s0;dkl010z0;fu3010z0;fu3010z1;prestas0;pp0qffs0;pp0qnhs0;ppz850s0;ppz700s0;dv1towz0;fu3towz0;fu3towz1;ta1tows0;uretows0;tdetows0\n')
        for station in coord_station_meteosuisse:
            f.write(f'{station[0]};{GMT_datetime};-;-;-;-;-;-;{error};-;-;-;-;-;-;-;-;-;-;-;-;-\n')
def reload_preferences():
    global preferences
    try:
        with open('preferences.json', 'r') as f:
            preferences = json.load(f)
    except FileNotFoundError:
        print('no preferences have been saved yet')
        preferences = {}
    except:
        print('error loading preferences')
        preferences = {}
    return preferences
def get_text_icon_arrow(direction):
    if direction <= 360-22.5 and direction >= 360/8*7-22.5:
        output = '⬊'
    elif direction <= 360/8*7-22.5 and direction >= 360/8*6-22.5:
        output = '➞'
    elif direction <= 360/8*6-22.5 and direction >= 360/8*5-22.5:
        output = '⬈'
    elif direction <= 360/8*5-22.5 and direction >= 360/8*4-22.5:
        output = '⬆'
    elif direction <= 360/8*4-22.5 and direction >= 360/8*3-22.5:
        output = '⬉'
    elif direction <= 360/8*3-22.5 and direction >= 360/8*2-22.5:
        output = '⬅'
    elif direction <= 360/8*2-22.5 and direction >= 360/8-22.5:
        output = '⬋'
    elif (direction <= 360/8-22.5 or direction <= 360+360/8-22.5) and (direction >= 0-22.5 or direction >= 360-22.5):
        output = '⬇'
    else:
        output = ''
    return output

def alert_content():
    with open("VQHA80.csv", "r") as f_csv:
        reader = csv.DictReader(f_csv, delimiter=';')
        reload_preferences()
        if preferences['wind_speed_unit'] == 'km/h':
            wind_speed_coef = 1
        else:
            wind_speed_coef = 1/1.852
        with open("coord_station_meteosuisse.json", "r") as f_json:
            coord_reader = json.load(f_json)
            content = {}
            for ligne, coord in zip(reader, coord_reader):
                if ligne['Station/Location'] == 'MRP':
                    continue
                if coord[-1] == 1:
                    date = ligne['Date']
                value = []
                key = coord[3]
                try:
                    vent, rafale = round(float(ligne['fu3010z0']), 1), round(float(ligne['fu3010z1']), 1)
                    value.append(f'{str(round(vent*wind_speed_coef, 1))} | {str(round(rafale*wind_speed_coef, 1))}')
                    direction = int(float(ligne['dkl010z0']))
                    arrow = get_text_icon_arrow(direction)
                    value.append(f'{direction}° {arrow}')
                    content[station_dict[key]] = value
                except ValueError:
                    for i in range(2): value.append('')
            return content, date
def strafe_date_from_csv(local_time: str):
    gmt_time = datetime.strptime(local_time, '%Y%m%d%H%M')
    gmt_time = pytz.timezone('GMT').localize(gmt_time)

    try: 
        local_tz = pytz.timezone(str(tzlocal.get_localzone()))
    except:
        local_tz = pytz.timezone('UTC')
    local_time = gmt_time.astimezone(local_tz)

    date = local_time
    hour = str(int(local_time.strftime('%H'))) 
    minute = local_time.strftime('%M')
    date = local_time.strftime('%d/%m/%Y')
    return hour, minute, date
def send_alert(station, *args):
    try:
        date = args[0]
        if date != '':
            with open(f'notification_sent_{station}.txt', 'w') as f:
                f.write(str(date))
        from_shortcut = False
    except:
        from_shortcut = True
    content, local_time = alert_content()

    hour, minute, date = strafe_date_from_csv(local_time=local_time)

    if from_shortcut:
        date = f"{hour}h{minute}"
    else:
        date = f"{hour}h{minute}  {date}"

    station_name = reversed_station_dict[int(station)]
    reload_preferences()
    if preferences['wind_speed_unit'] == 'km/h':
        unit = 'km/h'
    else:
        unit = 'noeuds'

    img = set_icon(float(content[int(station)][0].split('|')[0]), float(content[int(station)][0].split('|')[1]))
    img = img.rotate(-int(content[int(station)][1].split('°')[0]))
    img = img.resize((350, 350), Image.Resampling.LANCZOS)

    background = Image.new('RGBA', (400, 400), (0, 0, 0, 0))  # Larger transparent background
    position = ((background.width - img.width) // 2,
               (background.height - img.height) // 2)
    background.paste(img, position, img)
    background.save('wind_arrow_alert.png', 'PNG')
    
    try:
        text_fields = [station_name, content[station_dict[station_name]][0] + unit + '     ' + date, content[station_dict[station_name]][1]]
    except:
        text_fields = ['Veuillez selectionner une station', 'pour obtenir les données']

    if platform.system().lower() == 'windows':
        newToast = Toast()
        newToast.text_fields = text_fields
        newToast.AddImage(ToastDisplayImage.fromPath('wind_arrow_alert.png'))
        newToast.on_activated = lambda _: launch_winfo()
            
        WindowsToaster('Winfo').show_toast(newToast)

    elif platform.system().lower() == 'linux':
        subprocess.Popen(['notify-send', 'Winfo', '\n'.join(text_fields)])
    elif platform.system().lower() == 'darwin':
        subprocess.run(["osascript", "-e", '\n'.join(text_fields)], check=True)

    print('notification sent to ', station)

def launch_winfo():
    subprocess.Popen(['Winfo.exe'])
def set_icon(moyenne, rafale):

    if moyenne <= 3:
        force_couleur = int((moyenne)/3 * 255)
        pixel_values = (int(255-force_couleur/4), int(255-force_couleur/8), 255, 255) # to full light blue (255/4*3, 255/8*7, 255, 255)
    elif moyenne <= 15:
        force_couleur = int((moyenne-3)/12 * 255)
        pixel_values = (int(255/4*3-force_couleur/2), int(255/8*7+force_couleur/4), int(255-force_couleur), 255) # to full green (0, 255, 0, 255)
    elif moyenne <= 25:
        force_couleur = int((moyenne-15)/10 * 255)
        pixel_values = (force_couleur, 255, 0, 255) # to full yellow (255, 255, 0, 255)
    elif moyenne <= 35:
        force_couleur = int((moyenne-25)/10 * 255) # to full orange (255, 128, 0, 255)
        pixel_values = (255, int(255-force_couleur/2), 0, 255)
    elif moyenne <= 40:
        force_couleur = int((moyenne-35)/15 * 255)
        pixel_values = (255, int(255/2-force_couleur/2), 0, 255) # to full red (255, 0, 0, 255)
    elif moyenne <= 60:
        force_couleur = int((moyenne-40)/20 * 255)
        pixel_values = (int(255-force_couleur/8*7), int(force_couleur/16), 0, 255) # to full brown (255/8, 255/16, 0, 255)
    else:
        force_couleur = int((moyenne-60)/25 * 255)
        pixel_values = (int(255/8-force_couleur/8), int(255/16-force_couleur/16), 0, 255) # to full black

    print(f'{moyenne}\n {force_couleur = } | -> {pixel_values = }')
    im = Image.open('images/wind_arrow.png').convert('RGBA')
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

station_dict = {}
abreviation_list = []
with open('coord_station_meteosuisse.json', 'r') as f:
    coord_station_meteosuisse = json.load(f)
    for station in coord_station_meteosuisse:
        station_dict[station[3]] = station[5]
        abreviation_list.append(station[0])
reversed_station_dict = {v: k for k, v in station_dict.items()}
station_list = []
for station in station_dict.keys(): station_list.append(str(station))

reload_preferences()
try:
    if preferences['wind_speed_unit'] == 'km/h':
        wind_speed_coef = 1
    else:
        wind_speed_coef = 1/1.852
except KeyError:
    wind_speed_coef = 1
    preferences['wind_speed_unit'] = 'km/h'
