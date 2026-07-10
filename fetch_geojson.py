import requests
import json
import time
import os

def fetch_boundary(query, filename):
    url = f"https://nominatim.openstreetmap.org/search.php?q={query}&polygon_geojson=1&format=json"
    headers = {'User-Agent': 'BapendaApp/1.0'}
    res = requests.get(url, headers=headers).json()
    if res and len(res) > 0:
        geojson = res[0]['geojson']
        feature = {
            "type": "Feature",
            "properties": {"name": query},
            "geometry": geojson
        }
        feature_collection = {
            "type": "FeatureCollection",
            "features": [feature]
        }
        with open(filename, 'w') as f:
            json.dump(feature_collection, f)
        print(f"Saved {filename}")
    else:
        print(f"Not found: {query}")
        
print("Fetching Kabupaten...")
fetch_boundary("Kabupaten Purwakarta", "kab_purwakarta.geojson")

kecamatans = [
    "Purwakarta", "Babakan Cikao", "Campaka", "Cibatu", "Bungursari",
    "Pasawahan", "Pondoksalam", "Wanayasa", "Kiarapedes", "Bojong",
    "Darangdan", "Plered", "Tegalwaru", "Maniis", "Sukasari", "Jatiluhur", "Sukatani"
]

features = []
print("Fetching Kecamatan...")
for kec in kecamatans:
    url = f"https://nominatim.openstreetmap.org/search.php?q=Kecamatan+{kec},+Kabupaten+Purwakarta&polygon_geojson=1&format=json"
    headers = {'User-Agent': 'BapendaApp/1.0'}
    try:
        res = requests.get(url, headers=headers).json()
        if res and len(res) > 0:
            geojson = res[0]['geojson']
            features.append({
                "type": "Feature",
                "properties": {"name": kec},
                "geometry": geojson
            })
            print(f" - Fetched {kec}")
        else:
            print(f" - Not found {kec}")
    except Exception as e:
        print(f" - Error {kec}: {e}")
    time.sleep(1)

if features:
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    with open("kecamatan_purwakarta.geojson", 'w') as f:
        json.dump(feature_collection, f)
    print("Saved kecamatan_purwakarta.geojson")
