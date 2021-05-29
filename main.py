from datetime import datetime
from datetime import timedelta

from bs4 import BeautifulSoup
import urllib.request
import json
import requests

urls = ['https://www.gatotv.com/canal/', 'https://www.tvpassport.com/tv-listings/stations/']
today = datetime.today()

listDays = ["","","","","","","","","","",""]

for n in range(11):
    listDays[n] = today.strftime("%Y-%m-%d")
    today = today + timedelta(days=1)

####Numero de paquetes + 1#########
paquetes = 7

def tableDataText(table):

    def rowgetDataText(tr, coltag='td'): # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]

    rows = []
    trs = table.find_all('tr')
    headerow = rowgetDataText(trs[0], 'th')

    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]

    for tr in trs: # for every table row
        rows.append(rowgetDataText(tr, 'td')) # data row

    return rows


def start(day):
    data = {}
    dataProgram = {}
    day = datetime.strptime(day, '%Y-%m-%d')
    contadorCanal = 0
    for ids in range(1, paquetes):
        payload = {'Option': 'GetChannelsInfoBypackage', 'PackageID': ids}
        x = requests.post('http://172.16.0.15/BBINCO/TV/Core/Controllers/PY.php', data=payload)

        channels = json.loads(x.content)
        #print(channels)

        ##############  GATO TV ##############
        print('GATO TV')

        for channel in channels:
            if 'GATO' in channel['STTN']:
                try:
                    raw_html = urllib.request.urlopen(
                        'https://www.gatotv.com/canal/' + channel['NAME'] + day.strftime("%Y-%m-%d")).read().decode()
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    table = soup.find("table", attrs={"class": "tbl_EPG"})
                    JSONGato = tableDataText(table)
                    JSONGato = separarGato(JSONGato)
                    for p in range(len(JSONGato)):
                        dataProgram[str(p)] = []
                        dataProgram[str(p)].append({
                            "STTN": channel['STTN'],
                            "DBKY": '',
                            "TTLE": JSONGato[p][2],
                            "DSCR": JSONGato[p][3],
                            "DRTN": '',
                            "MNTS": '',
                            "DATE": day.strftime("%Y%m%d"),
                            "STRH": JSONGato[p][0],
                            "FNLH": JSONGato[p][1],
                            "TVRT": '',
                            "STRS": '',
                            "EPSD": ''
                        })
                except:
                    print(channel['NAME'] + "   No encontrado")

                data[str(contadorCanal)] = []
                data[str(contadorCanal)].append({
                    'PSCN': channel['PSCN'],
                    'ADIO': channel['ADIO'],
                    'PRGM': channel['PRGM'],
                    'SRCE': channel['SRCE'],
                    'QLTY': channel['QLTY'],
                    'PORT': channel['PORT'],
                    'CHNL': channel['CHNL'],
                    'STTN': channel['STTN'],
                    'NAME': channel['NAME'],
                    'INDC': channel['INDC'],
                    'LOGO': channel['LOGO'],
                    'DTNU': day.strftime("%Y%m%d"),
                    'DATE': day.strftime("%c"),
                    'PROGRAMS': dataProgram
                })
                contadorCanal = contadorCanal + 1

            ##############  TV PASSPORT ##############
            if 'PASS' in channel['STTN']:
                print('PASS  ', channel['NAME'])
                dataProgram = {}
                raw_html = urllib.request.urlopen(
                    'https://www.tvpassport.com/tv-listings/stations/' + channel['NAME'] + day.strftime("%Y-%m-%d")).read().decode()
                soup = BeautifulSoup(raw_html, 'html.parser')
                for i in range(1, 100):
                    table = soup.find(id="itemheader" + str(i))
                    if table == None:
                        break
                    hora = datetime.strptime(table['data-listdatetime'], '%Y-%m-%d %H:%M:%S')
                    # print(hora.strftime("%H:%M"))
                    dataProgram[str(i - 1)] = []
                    dataProgram[str(i - 1)].append({
                        "STTN": channel['STTN'],
                        "DBKY": '',
                        "TTLE": table['data-showname'],
                        "DSCR": table['data-description'],
                        "DRTN": '',
                        "MNTS": '',
                        "DATE": day.strftime("%Y%m%d"),
                        "STRH": hora.strftime("%H:%M"),
                        "FNLH": '',
                        "TVRT": table['data-rating'],
                        "STRS": '',
                        "EPSD": table['data-episodetitle']
                    })

                data[str(contadorCanal)] = []
                data[str(contadorCanal)].append({
                    'PSCN': channel['PSCN'],
                    'ADIO': channel['ADIO'],
                    'PRGM': channel['PRGM'],
                    'SRCE': channel['SRCE'],
                    'QLTY': channel['QLTY'],
                    'PORT': channel['PORT'],
                    'CHNL': channel['CHNL'],
                    'STTN': channel['STTN'],
                    'NAME': channel['NAME'],
                    'INDC': channel['INDC'],
                    'LOGO': channel['LOGO'],
                    'DTNU': day.strftime("%Y%m%d"),
                    'DATE': day.strftime("%c"),
                    'PROGRAMS': dataProgram
                })
                contadorCanal = contadorCanal + 1


        with open(day.strftime("%Y%m%d")+'_'+str(ids)+'.json', 'w') as file:
            json.dump(data, file, indent=4)
            print('Json creado')


def separarGato(JSONGato):
    letras = ''
    JSONGato.pop(0)
    JSONGato.pop(0)
    JSONGato.pop(0)
    e = 0
    while e < len(JSONGato):
        if JSONGato[e] == []:
            JSONGato.pop(e)
            e = 0
        else:
            e += 1

    for indice in range(len(JSONGato)):

        if JSONGato[indice] != []:
            try:
                if JSONGato[indice][2] == '' or JSONGato[indice][3] == '':
                    continue
            except:
                JSONGato[indice].append('')

    for indice in range(len(JSONGato)):
        desc = ''
        title = ''
        if JSONGato[indice][2] == '':
            letras = JSONGato[indice][3]
        else:
            letras = JSONGato[indice][2]


        for ind in range(len(letras)):
            if ind < len(letras) - 1:
                if (letras[ind].islower() and letras[ind + 1].isupper()) or (letras[ind].isnumeric() and letras[ind + 1].isupper()):
                    for y in range(ind + 1):
                        title = title + letras[y]
                    for x in range(ind + 1, len(letras)):
                        desc = desc + letras[x]
                    break
        if title != '':
            JSONGato[indice][2] = title
            JSONGato[indice][3] = desc
    return JSONGato

for day in range(len(listDays)):
    start(listDays[day])