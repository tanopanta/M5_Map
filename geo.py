"""
RaspberryPiで動かすことを想定
"""
from dotenv import load_dotenv
import subprocess
import json
import urllib.request
import time
import os
import os.path 


def get_latlngs(api_key):
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key="+ api_key

    iwlist = subprocess.Popen(["sudo", "iwlist", "wlan0", "scan"], stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", "-e", "Address:", "-e", "Signal"],
                stdin=iwlist.stdout, stdout=subprocess.PIPE)
    grep = grep.communicate()[0].splitlines()

    wifiAccessPoints = []

    for add, level in zip(grep[::2], grep[1::2]):
        mac_address = add.split()[4].decode('utf-8')
        signal_level = int(level.split()[2][6:])
        wifiAccessPoints.append({"macAddress":mac_address, "signalStrength":signal_level, "age":0})

    json_data = json.dumps({"wifiAccessPoints":wifiAccessPoints}).encode("utf-8")
    print(json_data)
    req = urllib.request.Request(url=url,data=json_data,headers={'Content-type':'application/json'})

    response = urllib.request.urlopen(req)

    content = json.loads(response.read().decode('utf-8'))
    lat = content['location']['lat']    #緯度
    lng = content['location']['lng']    #経度
    radius = content['accuracy']        #正確さ（半径）
    print(lat, lng, radius)
    return lat, lng

def post(data):
    obj = json.dumps(data).encode("utf-8")
    print(obj)
    request = urllib.request.Request(url="http://192.168.1.3:5000/post_geo", data=obj, method="POST", headers={"Content-Type" : "application/json"})
    response = urllib.request.urlopen(request)
    

if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    API_KEY = os.environ.get("MAP_API_KEY") #.envファイルに記入
    try:
        for i in range(100):
            latlng = get_latlngs(API_KEY)
            post({"lat":latlng[0], "lng":latlng[1]})
            time.sleep(60 * 1)
    except KeyboardInterrupt:
        print("end")