from bs4 import BeautifulSoup
import requests
import re
import plotly.express as px
import json
import pandas as pd
from Keys import keyDict
import googlemaps
from tqdm import trange, tqdm



def location_dict(soup,state) -> dict:
    temp = "" 
    current = soup
    try:
        current = soup.h3.next_sibling
    except:
        current = soup.h2
        temp = state
    else:
        current = soup.h3
    locations = {}
    tester = True
    while tester:
        try:
            current.name
        except:
            pass
        else:
            if current.name == "h3":
                temp = current.contents[0].get_text()
                locations[temp] = None
            elif current.name == "h2":
                try:
                    c = locations[temp]
                except: 
                    locations[temp] = None
                else:
                    temp = current.contents[0].get_text()
                    locations[temp] = None

            elif current.name == "p":
                # assumes any given section will only have <p> tag not <p> followed by <li>
                print(current)
                if locations[temp] == None:
                    locations[temp] = [current.get_text()]
                else:
                    if type(locations) == list:
                        locations[temp] = [locations[temp][0] + current.get_text()]
            elif current.name == "ul":
                if locations[temp] == None:
                    locations[temp] = {}
                    bullets = current.find_all("li")
                    for x in bullets:
                        locations[temp][x.a.get_text()] = x.get_text()
                elif type(locations[temp]) == dict:
                    tempDict = {} 
                    bullets = current.find_all("li")
                    for x in bullets:
                        tempDict[x.a.get_text()] = x.get_text()
                    locations[temp].update(tempDict)
                else:
                    print("another tag present before <li>")
                    print("This is the tag:", current)

            try:
                breaker = current["class"][0]
            except:
                pass
            else:
                if breaker == "reflist":
                    tester = False
                    print("HAS BEEN STOPPED")
                
            try:
                breaker2 = current.span["id"]
            except:
                pass
            else:
                if breaker2 == "Deaths_and_crime_rate":
                    tester = False
                    print("id was death and crime rate")
        current = current.next_sibling
    return locations

def clean_string(locations) -> dict:
    keys = locations.keys()
    for x in keys:
        if type(locations[x]) == list:
            for y in range(len(locations[x])):
                locations[x][y] = re.sub('\[\d+\]\n*',"",locations[x][y])
        elif type(locations[x]) == dict:
            newkeys = locations[x].keys()
            for y in newkeys:
                locations[x][y] = re.sub('\[\d+\]\n*',"",locations[x][y])
        else:
            print("COULDN'T CLEAN BECAUSE UNKNOWN TYPE DISCOVERED. The type is:", str(type(x)), " The line is:", str(x))
    return locations

def fill_address_list(locations,state):
    state = state.replace("(state)","")
    state = state.replace("_","")
    keys = locations.keys()
    for x in keys:
        if type(locations[x]) == list:
            address_list.append(x+", "+state)
            text_list.append(locations[x][0])
        elif type(locations[x]) == dict:
            newkeys = locations[x].keys()
            for y in newkeys:
                if x != state:
                    address_list.append(y+", "+x+", "+state)
                else:
                    address_list.append(y+", "+x)
                text_list.append(locations[x][y])

def get_coordinates(address_list,file_name):
    #responce = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key="+keyDict["geocoding"])
    gmaps = googlemaps.Client(key=keyDict["geocoding"])
    for x in trange(len(address_list)):
        geocode_result = gmaps.geocode(address_list[x])
        #print(geocode_result)
        try:
            coordinates = geocode_result[0]["geometry"]["location"]
        except:
            print("Couldn't find location for: ",address_list[x])
        else:
            coordinates = geocode_result[0]["geometry"]["location"]
            coordinate_list.append([address_list[x],coordinates["lat"],coordinates["lng"],text_list[x]]) #,text_list[x]

            with open(file_name,"r") as file:
                temp = file.read()
                if temp == "":
                    with open(file_name,"w") as file2:
                        json.dump(coordinate_list,file2)
                else:
                    info = json.loads(temp)
                    info.extend(coordinate_list)
                    with open(file_name,"w") as file2:
                        json.dump(info,file2)

# Didn't include Minnesota

if __name__ == "__main__":
    #state_list = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New_Hampshire', 'New_Jersey', 'New_Mexico', 'New_York_(state)', 'North_Carolina', 'North_Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode_Island', 'South_Carolina', 'South_Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington_(state)', 'West_Virginia', 'Wisconsin', 'Wyoming']
    state_list = ['Minnesota']

    for x in trange(len(state_list)):
        state = state_list[x]
        file_name = "Data.txt"

        res = requests.get("https://en.wikipedia.org/wiki/George_Floyd_protests_in_"+ state)
        soup = BeautifulSoup(res.text,"html.parser")

        soup = soup.find("div",class_ = "mw-parser-output")

        locations = location_dict(soup,state)
        locations = clean_string(locations)
        print(locations)

        address_list = []
        text_list = []
        coordinate_list = []

        fill_address_list(locations,state)
        print("Address_list is ",len(address_list))
        print("Text list is ",len(text_list))
        get_coordinates(address_list,file_name)

