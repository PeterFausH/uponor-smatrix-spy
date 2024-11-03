# -*- coding: utf-8 -*-
# erstellt: Peter Fürle
# Uponor @ Home Fussbodenheizung
# holt Leistungswerte aus den JSON-Daten der Uponor im KM6
# setzt Fehler/Alarme auf 0 statt mit empty weiterzugeben.
# ein Cronjob startet Skript jede 5 Minuten

import json
#import urllib2 nur für Python2.7
import requests
from influxdb import InfluxDBClient


# Configure InfluxDB connection variables
host = "127.0.0.1" 
port = 8086 
user = "spy"
password = "home"
dbname = "km6_uponor" 


# Influx Datenbank verbinden
#influx
#> create database km6_uponor
#> use uponor
#> create user spy with password 'home' with all privileges
#> grant all privileges on km6_uponor to spy
client = InfluxDBClient(host, port, user, password, dbname)

#Fehler abfragen:
#{"jsonrpc":"2.0","id":26,"method":"readactivealarms","params":{}}

#arrays anlegen mit meinen Raumbezeichnungen und den Werten.
#          0              1                2    
Raum_T = ["Studio-WoZi","Studio-Kueche","Studio-Bad"]
Raum_N = [80,80+40,80+40+40]
#Systemweite Werte, Raumunabhängig
System_N = [20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,60,61,62,63,64,65,66,67,68,69,70,100]
print("Systemnummern:  ",len(System_N))
System_T = ["module_id","cooling_available","holiday_mode","forced_eco_mode","hc_mode","hc_masterslave","ts_sv_version","holiday_setpoint","average_temp_low",
            "low_temp_alarm_limit","low_temp_alarm_hysteresis","remote_access_alarm","device_lost_alarm","no_comm_controller1","no_comm_controller2",
            "no_comm_controller3","no_comm_controller4","average_room_temperature","controller_presence","allow_hc_mode_change","hc_master_type",
            "output_module","rh_deadzone","controller_sv_version","thermostat_presence","supply_high_alarm","supply_low_alarm","average_room_temperature_NO",
            "measured_outdoor_temperature","supply_temp","dehumidifier_status","outdoor_sensor_presence","last"]
print("Systemtexte:   ",len(System_T))
#Zone-array sind die Thermostat-Raum-Werte von 0 bis 33
Zone_T = ["eco_profile_active_cf","dehumidifier_control_activation","rh_control_activation","eco_profile_number","setpoint_write_enable","cooling_allowed",
          "rh_setpoint","min_setpoint","max_setpoint","min_floor_temp","max_floor_temp","room_setpoint","eco_offset","eco_profile_active",
          "home_away_mode_status","room_in_demand","rh_limit_reached","floor_limit_status","technical_alarm","tamper_indication","rf_alarm","battery_alarm",
          "rh_sensor","thermostat_type","regulation_mode","room_temperature","room_temperature_ext","rh_value","ch_linked_to_th","room_name",
          "utilization_factor_24h","utilization_factor_7d","reg_mode","channel_average","radiator_heating"]
print("Zonen-Bereich: ",len(Zone_T))

print("\nRaspberry Pi fragt Uponor U@Home direkt ab")

#Datensatz für InfluxDB zusammenbauen
def add_system(name,wert):
    #Allgemein-Info die nicht Raumabhängig sind.
    info=[
        {
            "measurement": "uponor",
                "tags": {
                    "bereich": "GS_Allgemein"
                },
            "fields": {
                "GS_"+name : wert
            }
        }
        ]
    #print(info)
    client.write_points(info, time_precision='m')
    return

def add_zone(i,name,wert):
    # Zone Infos sind Raumabhängig
    info=[
        {
            "measurement": "uponor",
                "tags": {
                    "bereich": "GS_"+Raum_T[i]
                },
            "fields": {
                "GS_"+name : wert
            }
        }
        ]
    #print(info)
    client.write_points(info)
    return

#Abfrage für Raumdaten und temp Printausgabe
#Übergabe an add_zone um in die Influx-DB zu schreiben
def raum(n,zone):
    print("Ermittlung Zonen-Werte für "+Raum_T[n])
    r = requests.post(url, data=json.dumps(zone), headers=headers)
    json_string = json.dumps(r.json())
    parsed_json = json.loads(json_string)

    i=0
    while i < len(Zone_T):
        #nur belegte values ausgeben
        if (parsed_json["result"]["objects"][i+1]["properties"] != {}):
            #print(Raum_N[n]+i,Zone_T[i]+"="+str((parsed_json["result"]["objects"][i+1]["properties"]["85"]["value"])))
            add_zone(n,Zone_T[i],parsed_json["result"]["objects"][i+1]["properties"]["85"]["value"])
        else:
            print(Raum_N[n]+i,Zone_T[i],"= not available")
            add_zone(n,Zone_T[i],0)
        i=i+1


#Systemwerte
#Abfrage-String zusammenbasteln
system_data = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "read",
        "params": {
            "objects": [
                {"id": System_N[0],"properties": {"85": {}}},
                {"id": System_N[1],"properties": {"85": {}}},
                {"id": System_N[2],"properties": {"85": {}}},
                {"id": System_N[3],"properties": {"85": {}}},
                {"id": System_N[4],"properties": {"85": {}}},
                {"id": System_N[5],"properties": {"85": {}}},
                {"id": System_N[6],"properties": {"85": {}}},
                {"id": System_N[7],"properties": {"85": {}}},
                {"id": System_N[8],"properties": {"85": {}}},
                {"id": System_N[9],"properties": {"85": {}}},
                {"id": System_N[10],"properties": {"85": {}}},
                {"id": System_N[11],"properties": {"85": {}}},
                {"id": System_N[12],"properties": {"85": {}}},
                {"id": System_N[13],"properties": {"85": {}}},
                {"id": System_N[14],"properties": {"85": {}}},
                {"id": System_N[15],"properties": {"85": {}}},
                {"id": System_N[16],"properties": {"85": {}}},
                {"id": System_N[17],"properties": {"85": {}}},
                {"id": System_N[18],"properties": {"85": {}}},
                {"id": System_N[19],"properties": {"85": {}}},
                {"id": System_N[20],"properties": {"85": {}}},
                {"id": System_N[21],"properties": {"85": {}}},
                {"id": System_N[22],"properties": {"85": {}}},
                {"id": System_N[23],"properties": {"85": {}}},
                {"id": System_N[24],"properties": {"85": {}}},
                {"id": System_N[25],"properties": {"85": {}}},
                {"id": System_N[26],"properties": {"85": {}}},
                {"id": System_N[27],"properties": {"85": {}}},
                {"id": System_N[28],"properties": {"85": {}}},
                {"id": System_N[29],"properties": {"85": {}}},
                {"id": System_N[30],"properties": {"85": {}}},
                {"id": System_N[31],"properties": {"85": {}}},
                {"id": System_N[32],"properties": {"85": {}}},
                ]
            }
        }

#mit Raum-Index durchlaufen lassen
n=0
zone_data0 = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "read",
        "params": {
            "objects": [
                {"id": "1","properties": {"85": {}}},
                {"id": Raum_N[n]+0,"properties": {"85": {}}},
                {"id": Raum_N[n]+1,"properties": {"85": {}}},
                {"id": Raum_N[n]+2,"properties": {"85": {}}},
                {"id": Raum_N[n]+3,"properties": {"85": {}}},
                {"id": Raum_N[n]+4,"properties": {"85": {}}},
                {"id": Raum_N[n]+5,"properties": {"85": {}}},
                {"id": Raum_N[n]+6,"properties": {"85": {}}},
                {"id": Raum_N[n]+7,"properties": {"85": {}}},
                {"id": Raum_N[n]+8,"properties": {"85": {}}},
                {"id": Raum_N[n]+9,"properties": {"85": {}}},
                {"id": Raum_N[n]+10,"properties": {"85": {}}},
                {"id": Raum_N[n]+11,"properties": {"85": {}}},
                {"id": Raum_N[n]+12,"properties": {"85": {}}},
                {"id": Raum_N[n]+13,"properties": {"85": {}}},
                {"id": Raum_N[n]+14,"properties": {"85": {}}},
                {"id": Raum_N[n]+15,"properties": {"85": {}}},
                {"id": Raum_N[n]+16,"properties": {"85": {}}},
                {"id": Raum_N[n]+17,"properties": {"85": {}}},
                {"id": Raum_N[n]+18,"properties": {"85": {}}},
                {"id": Raum_N[n]+19,"properties": {"85": {}}},
                {"id": Raum_N[n]+20,"properties": {"85": {}}},
                {"id": Raum_N[n]+21,"properties": {"85": {}}},
                {"id": Raum_N[n]+22,"properties": {"85": {}}},
                {"id": Raum_N[n]+23,"properties": {"85": {}}},
                {"id": Raum_N[n]+24,"properties": {"85": {}}},
                {"id": Raum_N[n]+25,"properties": {"85": {}}},
                {"id": Raum_N[n]+26,"properties": {"85": {}}},
                {"id": Raum_N[n]+27,"properties": {"85": {}}},
                {"id": Raum_N[n]+28,"properties": {"85": {}}},
                {"id": Raum_N[n]+29,"properties": {"85": {}}},
                {"id": Raum_N[n]+30,"properties": {"85": {}}},
                {"id": Raum_N[n]+31,"properties": {"85": {}}},
                {"id": Raum_N[n]+32,"properties": {"85": {}}},
                {"id": Raum_N[n]+33,"properties": {"85": {}}},
                {"id": Raum_N[n]+34,"properties": {"85": {}}},
                {"id": Raum_N[n]+35,"properties": {"85": {}}},
                {"id": Raum_N[n]+36,"properties": {"85": {}}},
                {"id": Raum_N[n]+37,"properties": {"85": {}}}
                ]
            }
        }

n=1
zone_data1 = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "read",
        "params": {
            "objects": [
                {"id": "1","properties": {"85": {}}},
                {"id": Raum_N[n]+0,"properties": {"85": {}}},
                {"id": Raum_N[n]+1,"properties": {"85": {}}},
                {"id": Raum_N[n]+2,"properties": {"85": {}}},
                {"id": Raum_N[n]+3,"properties": {"85": {}}},
                {"id": Raum_N[n]+4,"properties": {"85": {}}},
                {"id": Raum_N[n]+5,"properties": {"85": {}}},
                {"id": Raum_N[n]+6,"properties": {"85": {}}},
                {"id": Raum_N[n]+7,"properties": {"85": {}}},
                {"id": Raum_N[n]+8,"properties": {"85": {}}},
                {"id": Raum_N[n]+9,"properties": {"85": {}}},
                {"id": Raum_N[n]+10,"properties": {"85": {}}},
                {"id": Raum_N[n]+11,"properties": {"85": {}}},
                {"id": Raum_N[n]+12,"properties": {"85": {}}},
                {"id": Raum_N[n]+13,"properties": {"85": {}}},
                {"id": Raum_N[n]+14,"properties": {"85": {}}},
                {"id": Raum_N[n]+15,"properties": {"85": {}}},
                {"id": Raum_N[n]+16,"properties": {"85": {}}},
                {"id": Raum_N[n]+17,"properties": {"85": {}}},
                {"id": Raum_N[n]+18,"properties": {"85": {}}},
                {"id": Raum_N[n]+19,"properties": {"85": {}}},
                {"id": Raum_N[n]+20,"properties": {"85": {}}},
                {"id": Raum_N[n]+21,"properties": {"85": {}}},
                {"id": Raum_N[n]+22,"properties": {"85": {}}},
                {"id": Raum_N[n]+23,"properties": {"85": {}}},
                {"id": Raum_N[n]+24,"properties": {"85": {}}},
                {"id": Raum_N[n]+25,"properties": {"85": {}}},
                {"id": Raum_N[n]+26,"properties": {"85": {}}},
                {"id": Raum_N[n]+27,"properties": {"85": {}}},
                {"id": Raum_N[n]+28,"properties": {"85": {}}},
                {"id": Raum_N[n]+29,"properties": {"85": {}}},
                {"id": Raum_N[n]+30,"properties": {"85": {}}},
                {"id": Raum_N[n]+31,"properties": {"85": {}}},
                {"id": Raum_N[n]+32,"properties": {"85": {}}},
                {"id": Raum_N[n]+33,"properties": {"85": {}}},
                {"id": Raum_N[n]+34,"properties": {"85": {}}},
                {"id": Raum_N[n]+35,"properties": {"85": {}}},
                {"id": Raum_N[n]+36,"properties": {"85": {}}},
                {"id": Raum_N[n]+37,"properties": {"85": {}}}
                ]
            }
        }

n=2
zone_data2 = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "read",
        "params": {
            "objects": [
                {"id": "1","properties": {"85": {}}},
                {"id": Raum_N[n]+0,"properties": {"85": {}}},
                {"id": Raum_N[n]+1,"properties": {"85": {}}},
                {"id": Raum_N[n]+2,"properties": {"85": {}}},
                {"id": Raum_N[n]+3,"properties": {"85": {}}},
                {"id": Raum_N[n]+4,"properties": {"85": {}}},
                {"id": Raum_N[n]+5,"properties": {"85": {}}},
                {"id": Raum_N[n]+6,"properties": {"85": {}}},
                {"id": Raum_N[n]+7,"properties": {"85": {}}},
                {"id": Raum_N[n]+8,"properties": {"85": {}}},
                {"id": Raum_N[n]+9,"properties": {"85": {}}},
                {"id": Raum_N[n]+10,"properties": {"85": {}}},
                {"id": Raum_N[n]+11,"properties": {"85": {}}},
                {"id": Raum_N[n]+12,"properties": {"85": {}}},
                {"id": Raum_N[n]+13,"properties": {"85": {}}},
                {"id": Raum_N[n]+14,"properties": {"85": {}}},
                {"id": Raum_N[n]+15,"properties": {"85": {}}},
                {"id": Raum_N[n]+16,"properties": {"85": {}}},
                {"id": Raum_N[n]+17,"properties": {"85": {}}},
                {"id": Raum_N[n]+18,"properties": {"85": {}}},
                {"id": Raum_N[n]+19,"properties": {"85": {}}},
                {"id": Raum_N[n]+20,"properties": {"85": {}}},
                {"id": Raum_N[n]+21,"properties": {"85": {}}},
                {"id": Raum_N[n]+22,"properties": {"85": {}}},
                {"id": Raum_N[n]+23,"properties": {"85": {}}},
                {"id": Raum_N[n]+24,"properties": {"85": {}}},
                {"id": Raum_N[n]+25,"properties": {"85": {}}},
                {"id": Raum_N[n]+26,"properties": {"85": {}}},
                {"id": Raum_N[n]+27,"properties": {"85": {}}},
                {"id": Raum_N[n]+28,"properties": {"85": {}}},
                {"id": Raum_N[n]+29,"properties": {"85": {}}},
                {"id": Raum_N[n]+30,"properties": {"85": {}}},
                {"id": Raum_N[n]+31,"properties": {"85": {}}},
                {"id": Raum_N[n]+32,"properties": {"85": {}}},
                {"id": Raum_N[n]+33,"properties": {"85": {}}},
                {"id": Raum_N[n]+34,"properties": {"85": {}}},
                {"id": Raum_N[n]+35,"properties": {"85": {}}},
                {"id": Raum_N[n]+36,"properties": {"85": {}}},
                {"id": Raum_N[n]+37,"properties": {"85": {}}}
                ]
            }
        }





#diesen Header beim Request mitschicken
headers = {'content-type': 'application/json', 'charset': 'utf-8'} 
#mein Uponor @home Gerät
url = 'http://192.168.200.203:80/api'
#Uponor @home abfragen
r = requests.post(url, data=json.dumps(system_data), headers=headers)
json_string = json.dumps(r.json())
parsed_json = json.loads(json_string)
i=0
#Allgemein-Daten abfragen.
while i < (len(System_N)-1):
    #nur belegte values ausgeben
    if (parsed_json["result"]["objects"][i]["properties"] != {}):
        #print(i,System_N[i],System_T[i]+"="+str((parsed_json["result"]["objects"][i]["properties"]["85"]["value"])))
        add_system(System_T[i],parsed_json["result"]["objects"][i]["properties"]["85"]["value"])
    else:
        print(i,System_N[i],System_T[i],"= not available")
        add_system(System_T[i],0)
    i=i+1

    
#die 3 Räume durchgehen
print("\n\n\n")
raum(0,zone_data0)
print("\n\n\n")
raum(1,zone_data1)
print("\n\n\n")
raum(2,zone_data2)



