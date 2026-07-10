import json
import requests
import time
import os

with open("referensi_wilayah.json", "r") as f:
    referensi = json.load(f)

features = []
print("Memulai proses fetch kelurahan...")

for kec, desas in referensi.items():
    if kec == "Semua" or kec == "OBJEK KHUSUS":
        continue
    for desa in desas:
        if str(desa).strip() == "" or str(desa) == "nan":
            continue
        url = f"https://nominatim.openstreetmap.org/search.php?q={desa},+{kec},+Purwakarta&polygon_geojson=1&format=json"
        headers = {'User-Agent': 'BapendaApp/1.0'}
        try:
            res = requests.get(url, headers=headers).json()
            if res and len(res) > 0:
                geojson = res[0]['geojson']
                features.append({
                    "type": "Feature",
                    "properties": {"name": desa, "kecamatan": kec},
                    "geometry": geojson
                })
                print(f"Berhasil: {desa} ({kec})")
            else:
                # Coba dengan keyword Desa/Kelurahan
                url_desa = f"https://nominatim.openstreetmap.org/search.php?q=Desa+{desa},+{kec},+Purwakarta&polygon_geojson=1&format=json"
                res_desa = requests.get(url_desa, headers=headers).json()
                if res_desa and len(res_desa) > 0:
                    geojson = res_desa[0]['geojson']
                    features.append({
                        "type": "Feature",
                        "properties": {"name": desa, "kecamatan": kec},
                        "geometry": geojson
                    })
                    print(f"Berhasil: {desa} ({kec}) - (Keyword Desa)")
                else:
                    print(f"Gagal: {desa} ({kec})")
        except Exception as e:
            print(f"Error {desa}: {e}")
        time.sleep(1.2)

if features:
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    with open("kelurahan_purwakarta.geojson", 'w') as f:
        json.dump(feature_collection, f)
    print(f"Selesai! {len(features)} kelurahan berhasil disimpan.")
