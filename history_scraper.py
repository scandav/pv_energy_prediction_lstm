import datetime
import locale
import requests
from pathlib import Path
import random
import time
import csv
from bs4 import BeautifulSoup
from collections import namedtuple

locale.setlocale(locale.LC_TIME, 'it_IT.utf8')
SCRIPT_DIR = Path(__file__).parent.resolve()

def write_checkpoint(file_name, csv_list):
    with open(file_name, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['date', 'time', 'cond', 'temp', 'wind', 'hr', 'press'])
        csv_out.writerows(csv_list)

WeatherRec = namedtuple('WeatherRec', ['date', 'time', 'cond', 'temp', 'wind', 'hr', 'press'])

start = datetime.datetime.strptime("05-10-2019", "%d-%m-%Y") 
end = datetime.datetime.today()
date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days + 1)]

weather_list = []
n_pages = len(date_generated)

for idx, dat in enumerate(date_generated):
    
    url = f"https://it.tutiempo.net/record/lime/{dat.strftime('%-d-%B-%Y')}.html"
    response = requests.get(url)

    print(f'Parsed {url} ({idx+1} of {n_pages}): {response.status_code}')
    time.sleep(random.uniform(0, 2))

    soup = BeautifulSoup(response.text, "html.parser")
    try:
        table_rows = soup.find(id="HistoricosData").div.table.tbody.find_all('tr')
    except AttributeError:
        print('Error in parsing page: data non available')
        continue

    for roww in table_rows:
        d = roww.find_all('td', recursive=False)
        if not d:
            continue

        weather_list.append(WeatherRec(
            dat.strftime('%d-%m-%Y'),
            d[0].text,
            d[1].span.text,
            d[2].text.rstrip('°'),
            d[3].text.rstrip(' km/h'),
            d[4].text.rstrip('%'),
            d[5].text.rstrip(' hPa')
        ))

    if (idx + 1) % 30 != 0: continue

    print(f'Saving checkpoint history_weather_{str((idx + 1) // 30).zfill(2)}.csv')
    file_path = SCRIPT_DIR.joinpath('data', f'history_weather_{str((idx + 1) // 30).zfill(2)}.csv')
    write_checkpoint(file_path, weather_list)
    weather_list.clear()

file_path = SCRIPT_DIR.joinpath('dat', f'history_weather_{str((idx + 1) // 30 + 1).zfill(2)}.csv')
write_checkpoint(file_path, weather_list)
print('DONE')


        
