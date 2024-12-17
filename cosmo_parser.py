#https://data.geo.admin.ch/ch.meteoschweiz.prognosen/punktprognosen/Legende_COSMO-E_all_stations.txt #fielname = legend + '_' + member_id
import csv
from io import StringIO
import numpy, urllib.request, datetime

URL_COSMO = 'https://data.geo.admin.ch/ch.meteoschweiz.prognosen/punktprognosen/COSMO-E-all-stations.csv'

def cosmo_parser(station_abr: str, wind_speed_coef: float, raw: bool):
    try:
        if raw == True:
            raw = True
        else:
            raw = False
    except:
        raw = False
    if wind_speed_coef == 1:
        unit = ' km/h'
    else:
        unit = ' noeuds'
    urllib.request.urlretrieve(URL_COSMO, 'COSMO-E-all-stations.csv')

    header_to_remove = ['stn', 'time', 'leadtime', 'unit', 'member', '']
    content = open('COSMO-E-all-stations.csv', 'r').read()
    amout_of_line_to_skip = 23

    content = content.split('\n')[amout_of_line_to_skip:]

    first_row = content[0:3]
    first_row_ = ''

    for i in first_row:
        first_row_ = first_row_ + i
    first_row = first_row_
    first_row = first_row_.split(';')


    new_first_row = []
    for i in first_row:
        if i not in header_to_remove:
            new_first_row.append(i)


    fieldnames = ['stn', 'time', 'leadtime'] 
    for count, i in enumerate(new_first_row[:int(len(new_first_row)/3)]):
        name = i + '_' + new_first_row[int(count+2*len(new_first_row)/3)]
        fieldnames.append(name)
    fieldnames = ';'.join(fieldnames)

    del content[0:3]
    content.insert(0, fieldnames)
    content = '\n'.join(content)

    content = StringIO(content)
    csv_reader = csv.DictReader(content, delimiter=';')

    if not raw:
        data = [['Date', 'Moyenne', 'Médiane', 'Minimum', 'Maximum']]
    else:
        data = []
    for row in csv_reader:
        if row['stn'].upper() == station_abr.upper():
            values = []
            for i in range(20):
                i = str(i).zfill(2)
                values.append(float(row[f'FF_10M_{i}'])*3.6)
            time = datetime.datetime.strptime(row['time'], '%Y%m%d %H:%M')
            values.sort()
            mean = numpy.mean(values)
            median = numpy.median(values)
            # print(f'{time}    median: {round(median*wind_speed_coef)}  min: {round(min(values)*wind_speed_coef, 1)}  max: {round(max(values)*wind_speed_coef, 1)}')
            if not raw:
                time = time.strftime('%d/%m/%Y %Hh')
                data.append([time, round(mean*wind_speed_coef, 1), round(median*wind_speed_coef, 1), round(min(values)*wind_speed_coef, 1), str(round(max(values)*wind_speed_coef, 1)) + unit])
            else:
                values = values[2:-2]
                time = time.strftime('%d/%m %Hh')
                data.append([time, round(median*wind_speed_coef, 1), round(min(values)*wind_speed_coef, 1), round(max(values)*wind_speed_coef, 1)])
            print(f'{time}    moy: {round(mean*wind_speed_coef, 1)}  median: {round(median*wind_speed_coef, 1)}  min: {round(min(values)*wind_speed_coef, 1)}  max: {round(max(values)*wind_speed_coef, 1)}')
    return data

if __name__ == '__main__':
    abr = input('abréviation ? : ')
    cosmo_parser(abr, wind_speed_coef=1, raw=False)