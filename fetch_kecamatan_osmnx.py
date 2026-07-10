import osmnx as ox
import json
import time
import os

print("Membaca referensi_wilayah.json...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "referensi_wilayah.json"), "r", encoding="utf-8") as f:
    referensi = json.load(f)

kecamatan_list = [k for k in referensi.keys() if k not in ["Semua", "OBJEK KHUSUS"]]
features = []

for kec in kecamatan_list:
    # Title case for better OSM matching
    query = f"Kecamatan {kec.title()}, Kabupaten Purwakarta, Jawa Barat, Indonesia"
    print(f"Mencari {query}...")
    try:
        gdf = ox.features_from_place(query, tags={"admin_level": "6"})
        if not gdf.empty:
            gdf = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]
            if not gdf.empty:
                geojson_str = gdf.to_json()
                feature_collection = json.loads(geojson_str)
                if feature_collection['features']:
                    feat = feature_collection['features'][0]
                    feat['properties']['name'] = kec
                    features.append(feat)
                    print(f"  -> Berhasil: {kec}")
                else:
                    print(f"  -> Gagal proses geometry: {kec}")
            else:
                print(f"  -> Bukan Polygon: {kec}")
        else:
            print(f"  -> Tidak ditemukan: {kec}")
    except Exception as e:
        print(f"  -> Error: {e}")
    time.sleep(2)

if features:
    res = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(os.path.join(BASE_DIR, "kecamatan_purwakarta.geojson"), "w", encoding="utf-8") as f:
        json.dump(res, f)
    print(f"Tersimpan {len(features)} kecamatan ke kecamatan_purwakarta.geojson")
else:
    print("Tidak ada kecamatan yang berhasil diunduh.")
