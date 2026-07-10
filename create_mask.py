import json
from shapely.geometry import shape, mapping, Polygon

with open("kab_purwakarta.geojson") as f:
    data = json.load(f)

purwakarta_geom = shape(data['features'][0]['geometry'])

# Create world bounding box
world_poly = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90), (-180, -90)])

# Mask is world minus purwakarta
mask_geom = world_poly.difference(purwakarta_geom)

mask_feature = {
    "type": "Feature",
    "properties": {"name": "Mask"},
    "geometry": mapping(mask_geom)
}
with open("mask_purwakarta.geojson", "w") as f:
    json.dump(mask_feature, f)
print("Mask created successfully.")
