from winfo_import import reload_preferences, URL_VQHA80, coord_station_meteosuisse, wind_speed_coef, send_alert, create_errored_file
import urllib.request, csv, time

while True:
    preferences = reload_preferences()
    try:
        preferences['notification']
    except:
        preferences['notification'] = {}
    try:
        urllib.request.urlretrieve(URL_VQHA80, "VQHA80.csv")
    except Exception as error:
        create_errored_file(error)

    for station in list(preferences['notification']):
        if 'wind_limit' in preferences['notification'][str(station)]:
            station = int(station)
            for i, content in enumerate(coord_station_meteosuisse):
                if content[-1] == station:
                    with open("VQHA80.csv", "r") as fichier_csv:
                        reader = csv.DictReader(fichier_csv, delimiter=';')

                        station_data_dict = dict(list(reader)[i])
                        try:
                            vent = float(station_data_dict['fu3010z0'])
                        except ValueError:
                            vent = None
                        if vent is not None:
                            if vent >= preferences['notification'][str(station)]['wind_limit']:
                                print('enough wind station', station, station_data_dict['fu3010z0'])
                                try:
                                    with open(f'notification_sent_{station}.txt', 'r') as f:
                                        content = f.read()
                                        if content == str(station_data_dict['Date']): # a notif has been sent before (because file exists) and the csv file hasn't changed since
                                            print(f"file 'notification_sent_{station}.txt' exists and the date is the same ({content}) so not sending notif")
                                        else: # a notif has been sent before (because file exists) but it's a new file
                                            print(f"file 'notification_sent_{station}.txt' exists, but the date is not the same (file.txt != VQHA80.csv) : ({content} != {station_data_dict['Date']}")
                                            send_alert(station, station_data_dict['Date'])
                                except FileNotFoundError as error: # file 'notification_sent_{station}.txt' doesn't exist => fileNotFound when opening it
                                    # no file => never saved the date => no notif sent yet => must send notif
                                    print(f"Expected and normal error : {error}")
                                    send_alert(station, station_data_dict['Date'])
                                except Exception as error:
                                    print(f"Unexpected error : {error}")
                            else:
                                print('not enough wind station', station, station_data_dict['fu3010z0'])
    time.sleep(120)