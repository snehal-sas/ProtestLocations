import plotly.express as px
import json
import pandas as pd
from Keys import keyDict
import googlemaps


info = []
file_name = "Data.txt"

def redefine_text(place, text):
    text = text.split()
    for x in range(len(text)):
        if x%8 == 0 and len(text)<50:
            text.insert(x,"<br>")
        elif x%16 == 0:
            text.insert(x,"<br>")
    result = place + "<br>"
    for x in text:
        result+= x + " "
    return result

with open(file_name,"r") as file:
    info = json.load(file)
    for x in info:
        x[3] = redefine_text(x[0],x[3])


df = pd.DataFrame(info,columns = ["place","lat","long","text"])
px.set_mapbox_access_token(keyDict["maptoken"])
fig = px.scatter_mapbox(df, lat="lat", lon="long", hover_data={"lat":False,"long":False},hover_name="text" ,mapbox_style="dark",zoom=3)
fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
fig.write_html("./map.html")
fig.show()

