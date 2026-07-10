import json
import time
from geopy.geocoders import Nominatim

with open('referensi_wilayah.json', 'r') as f:
    d = json.load(f)

geolocator = Nominatim(user_agent="bapenda_pwk_geocoder_batch")
results = {}

for kec, desas in d.items():
    for desa in desas:
        key = f"{kec}_{desa}"
        print(f"Geocoding {desa}, {kec}...")
        
        queries = [
            f"Kelurahan {desa}, Kecamatan {kec}, Purwakarta, Indonesia",
            f"Desa {desa}, Kecamatan {kec}, Purwakarta, Indonesia",
            f"{desa}, {kec}, Purwakarta, Indonesia",
            f"{desa}, Purwakarta, Indonesia"
        ]
        
        loc = None
        for q in queries:
            try:
                loc = geolocator.geocode(q, timeout=10)
                if loc:
                    break
            except Exception as e:
                print(f"  Error on {q}: {e}")
            time.sleep(1) # Be nice to OSM
            
        if loc:
            results[key] = {"lat": loc.latitude, "lon": loc.longitude}
            print(f"  SUCCESS: {loc.latitude}, {loc.longitude}")
        else:
            # Fallback to Bapenda if totally failed, just so it's not empty, or leave None
            results[key] = {"lat": -6.553618, "lon": 107.451278}
            print(f"  FAILED: Used Bapenda default fallback")

with open('koordinat_desa.json', 'w') as f:
    json.dump(results, f, indent=4)
print("DONE! Saved to koordinat_desa.json")
