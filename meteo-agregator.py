from bs4 import BeautifulSoup
import urllib.parse
import urllib.request

def get_gismet(num):
    gis_page = urllib.request.urlopen("https://www.gismeteo.ru/ajax/print/4540/short/" + str(num) + "/")
    page = gis_page.read()
    soup = BeautifulSoup(page, "html.parser")
    tr = soup.html.body.table.contents #метео-поля (Т, обл итд)
    global date
    global fallout
    date = tr[1].find_all(class_="addt")
    fallout = tr[5]
    temp = tr[7]
    wind_temp = tr[9]

    date = [x.contents[0] for x in date]

    fallout = fallout.find_all("img")
    fallout = [x['src'] for x in fallout]
    for w in range(0, len(fallout)):
        if fallout[w].count("n.moon.c4.png") != 0: fallout[w] = "облачно"
        if fallout[w].count("d.sun.c2.png") != 0: fallout[w] = "переменная облачность"
        if fallout[w].count("n.moon.png") != 0: fallout[w] = "ясная ночь"
        if fallout[w].count("d.sun.c4.s1.png") != 0: fallout[w] = "немного снега"
        if fallout[w].count("d.sun.png") != 0: fallout[w] = "ясно"
        if fallout[w].count("d.sun.c4.r2.png") != 0: fallout[w] = "дождь"
        if fallout[w].count("n.moon.c2.r1.png") != 0: fallout[w] = "ночной дождик"
        if fallout[w].count("d.sun.c3.png") != 0: fallout[w] = "больше туч"
        if fallout[w].count("n.moon.c4.s2.png") != 0: fallout[w] = "снег"
        if fallout[w].count("d.sun.c2.s1.png") != 0: fallout[w] = "солнечно и снежок"
        if fallout[w].count("n.moon.c3.s1.png") != 0: fallout[w] = "ночью снежок"
        if fallout[w].count("d.sun.c2.r1.png") != 0: fallout[w] = "дождик днём"
        if fallout[w].count("n.moon.c4.s1.png") != 0: fallout[w] = "снежок"
        if fallout[w].count("n.moon.c2.s1.png") != 0: fallout[w] = "ночью снежок"
        if fallout[w].count("d.sun.c4.png") != 0: fallout[w] = "облачно"
        if fallout[w].count("n.moon.c3.png") != 0: fallout[w] = "в осн облачно"
        if fallout[w].count("d.sun.c3.s1.png") != 0: fallout[w] = "снежок/солнце"
        if fallout[w].count("n.moon.c2.png") != 0: fallout[w] = "тучки ночью"
        if fallout[w].count("d.sun.c4.s2.png") != 0: fallout[w] = "снег"
    for w in temp.find_all("td"):
        if w.span is None:      #пустой отступ, пропускаем
            continue
        if len(w.span.contents) == 1:  #надпись "температура", пропускаем
            continue
        temperature.append(int(w.span.contents[1].contents[0] + w.span.contents[2]))  #знак + значение
    for w in wind_temp.find_all("div", class_="n_wind"):
        wind.append((int(w.contents[0])))

def dt_parse(tag):
    if tag.contents == []:
        return
    global date
    date.append(tag.strong.contents[0] + tag.strong.find("span", class_="forecast-detailed__day-month").contents[0])

def dd_parse(tag):
    if tag.table is None:
        return
    global temperature
    global fallout
    global wind
    for tr in tag.table.tbody.children:
        temperature.append(tr.find("td", class_="weather-table__body-cell weather-table__body-cell_type_daypart").find("div", class_="weather-table__temp").contents[0])
        fallout.append(tr.find("td", class_="weather-table__body-cell weather-table__body-cell_type_condition").div.contents[0])
        wind.append(float(tr.find("td", class_="weather-table__body-cell weather-table__body-cell_type_wind").div.span.span.contents[0].replace(",", ".")))

def has_table_but_no_id(tag):
    return tag.name == "table" and not tag.has_attr('id')

date = []
temperature = []
fallout = []
wind = []

#распрсим gismeteo
print("обрабатываем gismeteo")
for i in range(0, 8, 2):
    get_gismet(i)
    for k in range(1,3):
        gis_file = open("gismeteo n+" + str(i + k) + ".txt", "a", encoding="utf8")
        gis_file.write(date[k] + ";")
        for j in range(k * 4, k * 4 + 4):
            gis_file.write(str(temperature[j]) + ";")
        for j in range(k * 4, k * 4 + 4):
            gis_file.write(fallout[j] + ";")
        for j in range(k * 4, k * 4 + 4):
            gis_file.write(str(wind[j]) + ";")
        gis_file.write("\n")
        gis_file.close()
    date = []
    temperature = []
    fallout = []
    wind = []

#распарсим yandex
print("обработка yandex")
yandex_page = urllib.request.urlopen("https://yandex.ru/pogoda/verhniy-ufaley/details")
page = yandex_page.read()
soup = BeautifulSoup(page, "html.parser")
tag1 = soup.html.body.find("div", class_="content")
tag2 = tag1.find("div", class_="forecasts forecasts_my-location i-bem")
tag3 = tag2.find("div", class_="tabs-panes i-bem")
tag4 = tag3.find("div", class_="tabs-panes__pane tabs-panes__pane_active_yes")
tag5 = tag4.find("dl")

dt = tag5.find_all("dt")
dd = tag5.find_all("dd")

for i in dt:
    dt_parse(i)
for i in dd:
    dd_parse(i)

for d in range(1, len(date)):
    f = open("yandex n+" + str(d) +".txt", "a", encoding="utf8")
    f.write(date[d] + ";")
    for i in range(d * 4, d * 4 + 4):
        f.write(temperature[i] + ";")
    for i in range(d * 4, d * 4 + 4):
        f.write(fallout[i] + ";")
    for i in range(d * 4, d * 4 + 4):
        f.write(str(wind[i]) + ";")
    f.write("\n")
    f.close()

# прасим Росгидромет
print("обработка гидромета")
date = []
temperature = []
fallout = []
probability = []
wind = []

req = urllib.request.Request(
    "http://www.meteoinfo.ru/forecasts5000/russia/chelyabinsk-area/verhnij-ufalej/print", 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    }
)
req.add_header('Referer', 'http://www.meteoinfo.ru/forecasts5000/russia/chelyabinsk-area/verhnij-ufalej')
# антизащита =))
page = urllib.request.urlopen(req)
soup = BeautifulSoup(page, "html.parser")
all_pogoda = soup.html.body.table.find_all("tr")

for td in all_pogoda[0].find_all("td", class_="pogodadate"):  #parse date
    date.append(td.nobr.contents[0])

for td in all_pogoda[3].find_all("td", class_="pogodacell"):  #parse temp
    temperature.append(td.contents[0].replace(" ", "").replace("\xa0", ""))

for td in all_pogoda[5].find_all("td", class_="pogodacell"):  #описание погоды/осадки
    fallout.append(td.contents[0].replace(";", ","))

for td in all_pogoda[7].find_all("td", class_="pogodacell"):  #вероятность осадков %
    probability.append(td.contents[0] + "%")

for td in all_pogoda[9].find_all("td", class_="pogodacell"):  # скорость ветра
    wind.append(td.contents[0])

for i in range(0, len(date)):
    f = open("rosHyd n+" + str(i + 1) + ".txt", "a", encoding="utf8")
    f.write(date[i] + ";")
    f.write(temperature[i] + ";")
    f.write(fallout[i] + ";")
    f.write(wind[i] + ";")
    f.write(probability[i] + ";\n")
    f.close()

# парсим rp5
print("парсим rp5")
date = ""
temperature = []
fallout = []
wind = []

for n in range(0, 5):
    req = urllib.request.Request(
        "http://pda.rp5.ru/2155." + str(n) + "/ru", 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        }
    )
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, "html.parser")
    tr = soup.html.body.find_all(has_table_but_no_id)[0].find_all("tr") #погодные данные

    if len(tr[0].td.contents) > 1: #  если в первом блоке последнее состояние на мет.станции, а не дата
         tr.remove(tr[0])
         
    date = tr[0].td.b.contents[0].split(",")[1].strip()
    
    temperature.append(tr[3].td.b.span.contents[0].replace("ºC", ""))
    fallout.append(tr[3].td.b.contents[1].replace(", ", "") + " " + tr[4].td.b.contents[0])
    wind.append(tr[4].td.contents[0].split(",")[1].replace("м/с", "").strip())

    temperature.append(tr[8].td.b.span.contents[0].replace("ºC", ""))
    fallout.append(tr[8].td.b.contents[1].replace(", ", "") + " " + tr[9].td.b.contents[0])
    wind.append(tr[9].td.contents[0].split(",")[1].replace("м/с", "").strip())

    temperature.append(tr[13].td.b.span.contents[0].replace("ºC", ""))
    fallout.append(tr[13].td.b.contents[1].replace(", ", "") + " " + tr[14].td.b.contents[0])
    wind.append(tr[14].td.contents[0].split(",")[1].replace("м/с", "").strip())

    temperature.append(tr[18].td.b.span.contents[0].replace("ºC", ""))
    fallout.append(tr[18].td.b.contents[1].replace(", ", "") + " " + tr[19].td.b.contents[0])
    wind.append(tr[19].td.contents[0].split(",")[1].replace("м/с", "").strip())

    f = open("rp5 n+" + str(n + 1) + ".txt", "a", encoding="utf8")
    f.write(date + ";")
    for i in range(0, 4):
        f.write(temperature[i] + ";")
    for i in range(0, 4):
        f.write(fallout[i] + ";")
    for i in range(0, 4):
        f.write(wind[i] + ";")
    f.write("\n")
    f.close()

    date = ""
    temperature = []
    fallout = []
    wind = []
