# Uponor-SMatrix-Spy

python script fetches JSON from Uponor Smatrix Wave PLUS U@home. Data is sent to influx and dashboards are made with grafana

ch bin es leid, wenn Gäste meine Fussbodenheizung sabotieren – ich brauche ein Frühwarnsystem! In einer Ferienwohnung läuft eine Fussbodenheizung von Uponor. Komplett mit Einzelraumregelung und der Anbindung Uponor Smatrix Wave PLUS U@home R-167 und den Raumthermostaten T-167.

Uponor-Regelung

Leider kommen viele Gäste mit der Trägheit einer Fussbodenheizung nicht zurecht. Dann wird am Thermostat 30°C eingestellt wenn man es warm haben möchte. Ok, es wird wärmer, aber langsam – nachts wachst du dann auf weil du schwitzt. 

Dann wird auf 15°C gestellt um runterzukühlen. In dem Moment ist der ganze Fussboden aber aufgeheizt und bei einer Flächenheizung kommt da noch ordentlich Leistung raus. Jetzt wird der Verteilerkasten geöffnet. Meist wird erstmal die Antenne für die Funkmodule abgezogen. Dann wird wild auf den Tasten gedrückt, solange bis alles verstellt ist. Das dauert, Gast geht wandern, kommt zurück und es ist abgekühlt. Na siehste – klappt doch. 

Die nächsten Tage bleibt es auch kalt, der Gast reist ab, sagt aber nichts.

Irgendwann sitze ich wieder vor dem Verteilerkasten, resette alles, lerne den Regler wieder an, die Thermostaten, das Funkmodul und die externe Bedieneinheit. Das habe ich dieses Jahr schon zweimal gemacht, jetzt reicht es mir.

Ich brauche mehr Übersicht als die originale Bedienoberfläche hergibt. Ich will auf einen Blick sehen, ob es dem Gast gefällt. Sobald ich Temperatur-Vorgaben entdecke, die deutlich über oder unter etwa 20 Grad liegen, interveniere ich künftig sofort. 

Am übersichtlichsten finde ich Dashboards mit Grafana. Vielleicht auch deshalb, weil ich mich da schon eingefuchst habe. Jedenfalls möchte ich so eines haben. Dazu müssen die anzuzeigenden Daten erstmal in eine Influx-Datenbank. Um diese dort abzulegen, muss ich sie erstmal aus dem System entlocken:

Mit den Firefox Entwicklerfunktionen schreibe ich die Kommunikation der Weboberfläche mit und lasse mir die Kommunikation über JSON mitzeichnen. Alles natürlich nicht dokumentiert, mit wenig Motivation erstellt – wahrscheinlich von jemandem, der sich vorher nicht mit JSON beschäftigt hat. 
Wie auch immer, Vorgaben ändern, Werte ablesen, Werte in der JSON-Wurst suchen und nach und nach bin ich durchgestiegen. 


Die API ist trotzdem lieblos und verlangt als Payload eine Struktur, in der dann die Werte zurückgegeben werden. 

Das baue ich mir mit einem Python Skript zusammen. 

Vor den Details aber erstmal das Ergebnis:

Visualisierung in Grafana
Soll-Ist und Delta, Heizlastverteilung und Ventilzustände mit Humidity-Verlauf.
Es gibt 3 Räume und in der obersten Zeile sind geöffnete Ventile in rot-heiß hinterlegt, die geschlossenen sind blau-kalt. Die Durchschnittstemperatur ist angegeben und der Modus Home oder Away ist ersichtlich. 
Daneben habe ich aus einem anderen Dashboard die Aussentemperatur und die Vorlauftemperatur für den Fußboden-Heizkreis mit dargestellt.
Eine Freude habe ich am eingebundenen Logo über HTML-Text.
In der zweiten Zeile farbig codiert die Luftfeuchtigkeit der 3 Räume wie von den Thermostaten übermittelt.
Ganz unten die Vorgabe-Temperatur die der Gast gewählt hat. Ab 23° wird aus grün dann dunkelrot !
Viel schöner als im Original das pie-chart mit der Heizlast-Verteilung für die 3 Räume. 

Endlich entfällt das Durchblättern der Räume, das Hochschieben des Bildes um an die Statistiken zu kommen, das Auswählen der Alarme um endlich die Luftfeuchtigkeit ablesen zu können.

Natürlich zeichne ich auch Graphen mit Soll-Ist- und Durchschnittstemperatur. Die brauche ich aber nur, wenn ich sehen will, wann eine Änderung stattfand, oder wie lange es dauerte, bis die Vorgabe erreicht wurde:


Ansicht mit den Graphen der Temperaturverläufe
Jetzt zum Wesentlichen, wie komme ich an die Daten ?

In Python habe ich die Mitschnitt-Ergebnisse verwendet. Die Räume sind in Raumnummern versteckt. Der erste Raum hat die Nummer 81 und dann folgen die Weiteren mit einem Offset von 40. Jeder Einzelwert hat einen Offset zur Raumnummer. 
Die Solltemperatur des ersten Raumes hat eine Offset von 10 zur Raumnummer von 81.

#arrays anlegen mit meinen Raumbezeichnungen
#diese Raumnummern aus der Weboberfläche heraus mitgeschnitten
# 0 1 2 
Raum_T = ["GartenStudio","Studio-Kueche","Studio-Bad"]
Raum_N = [81,121,161]

#Raum_N = Initial
#Raum_N + 10 = Soll Temperatur am Thermostat
#Raum_N + 14 = Heizen
#Raum_N + 24 = Ist Temperatur am Thermostat
#Raum_N + 26 = Humidity
#Raum_N + 28 = Raumbezeichnung
#Raum_N + 29 = Utilization
Dann wird die Payload zusammengebaut. Dazu werden die ID-Nummern verwendet.

 #Abfrage-String zusammenbasteln
data = {
"id": 1,
"jsonrpc": "2.0",
"method": "read",
"params": {
"objects": [
{
"id": "1",
"properties": {
"85": {}
}
},
{
"id": Raum_N[i]+10,
"properties": {
"85": {}
}
},
{
"id": Raum_N[i]+24,
"properties": {
"85": {}
}
},
Wegen der „85“ habe ich gemutmaßt, dass dem Programmierer nicht wirklich klar war wie das JSON funktionieren kann. 

Jetzt holen wir die Daten:


#diesen Header beim Request mitschicken
headers = {'content-type': 'application/json', 'charset': 'utf-8'}
#mein Uponor @home Gerät
url = 'http://192.168.200.203:80/api'
#Uponor @home abfragen
r = requests.post(url, data=json.dumps(data), headers=headers)
json_string = json.dumps(r.json())
parsed_json = json.loads(json_string)
#Json auswerten
status=["NEIN","-Ja-"]
HomeAway=["Home","Away"]
Modul_ID = (parsed_json["result"]["objects"][1]["properties"]["85"]["value"])
Modus = (parsed_json["result"]["objects"][2]["properties"]["85"]["value"])
sw_version = (parsed_json["result"]["objects"][3]["properties"]["85"]["value"])
alarm_temp = (parsed_json["result"]["objects"][4]["properties"]["85"]["value"])

web_soll = float((parsed_json["result"]["objects"][5]["properties"]["85"]["value"]))
ist_temp = float((parsed_json["result"]["objects"][6]["properties"]["85"]["value"]))
Humidity = (parsed_json["result"]["objects"][7]["properties"]["85"]["value"])
Raumbez = (parsed_json["result"]["objects"][8]["properties"]["85"]["value"])
Heizantl = (parsed_json["result"]["objects"][9]["properties"]["85"]["value"])
Heizt = int((parsed_json["result"]["objects"][10]["properties"]["85"]["value"]))
D_temp = float((parsed_json["result"]["objects"][11]["properties"]["85"]["value"]))
Controller = (parsed_json["result"]["objects"][12]["properties"]["85"]["value"])
Absenkung = float((parsed_json["result"]["objects"][13]["properties"]["85"]["value"]))
In einer Schleife wir jetzt Raum für Raum abgefragt und an die Influx-Datenbank geschickt. 
Das übernimmt eine kleine Funktion:

def add(i,name,wert):
 info=[
  {
   "measurement": "uponor",
   "tags": {
   "bereich": Raum_T[i]
  },
   "fields": {
   name : wert
   }
  }
 ]
 client.write_points(info)
return
Die wird mit den gewonnenen Daten aufgerufen:

 #influx-Datenbank
add(i,"Solltemp",web_soll)
add(i,"Isttemp",ist_temp)
add(i,"Humidity",Humidity)
add(i,"Heizanteil",Heizantl)
add(i,"Heizt",Heizt)
add(i,"D-Temp",D_temp)
add(i,"Controller",Controller)
add(i,"Absenkung",Absenkung)
Das war’s dann schon. Jetzt kann ich hoffentlich schnell reagieren bevor wieder alles verstellt wird.
So war das  vorher:


Jeder Raum muss einzeln angeklickt werden.
 


Fusszeile erst nach Hochscrollen sichtbar
 


Dort versteckt, die Luftfeuchtigkeit
 

Interessiert ? Gerne unterstütze ich euch bei der Installation eines solchen Monitorings für eure Uponor Fussbodenheizung. Was es an Grundvoraussetzung braucht konntet ihr weiter oben ja schon lesen.

