import urllib.request
import zipfile
import json
import os

url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IDN_3.json.zip"
zip_path = "gadm_idn3.zip"

print(f"Downloading {url} ...")
try:
    urllib.request.urlretrieve(url, zip_path)
    print("Download complete. Extracting...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        json_filename = zip_ref.namelist()[0]
        zip_ref.extract(json_filename, ".")
    
    print(f"Reading {json_filename} ...")
    with open(json_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    purwakarta_features = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        # NAME_2 is typically the Regency/Kabupaten
        if props.get("NAME_2", "").upper() == "PURWAKARTA":
            # Map NAME_3 to 'name' for our app
            props['name'] = props.get("NAME_3", "").upper()
            purwakarta_features.append(feature)
            
    print(f"Found {len(purwakarta_features)} kecamatans in Purwakarta.")
    
    if purwakarta_features:
        output = {"type": "FeatureCollection", "features": purwakarta_features}
        with open("kecamatan_purwakarta.geojson", "w", encoding="utf-8") as f:
            json.dump(output, f)
        print("Saved to kecamatan_purwakarta.geojson")
        
    # Cleanup
    os.remove(zip_path)
    os.remove(json_filename)
except Exception as e:
    import traceback
    traceback.print_exc()
