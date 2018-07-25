import json
import urllib.request


def get_latlngs(api_key):
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key="+ api_key

    obj = {
        "wifiAccessPoints": [
        {
            "macAddress": "98:f1:99:41:25:6a",
            "signalStrength": -70,
            "signalToNoiseRatio": 0
        },
        {
            "macAddress": "84:af:ec:f5:cc:81",
            "signalStrength": -89,
            "signalToNoiseRatio": 0
        },
        {
            "macAddress": "00:1b:8b:e9:e8:72",
            "signalStrength": -94,
            "signalToNoiseRatio": 0
        },
        ]
    }
    json_data = json.dumps(obj).encode("utf-8")

    req = urllib.request.Request(url=url,data=json_data,headers={'Content-type':'application/json'})

    response = urllib.request.urlopen(req)

    content = json.loads(response.read().decode('utf-8'))
    lat = content['location']['lat']    #緯度
    lng = content['location']['lng']    #経度
    radius = content['accuracy']        #正確さ（半径）
    print(lat, lng, radius)
    return lat, lng