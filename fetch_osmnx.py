import osmnx as ox
import geopandas as gpd

print("Fetching boundaries for Kecamatans in Purwakarta...")
# admin_level 6 is Kecamatan in Indonesia
gdf = ox.features_from_place("Kabupaten Purwakarta, Jawa Barat, Indonesia", tags={"admin_level": "6"})
if not gdf.empty:
    # Filter for polygons/multipolygons only to avoid points/lines
    gdf = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    # Keep only useful columns
    if 'name' in gdf.columns:
        gdf = gdf[['name', 'geometry']]
    else:
        gdf = gdf[['geometry']]
        
    gdf.to_file("kecamatan_purwakarta.geojson", driver="GeoJSON")
    print(f"Saved {len(gdf)} kecamatans to kecamatan_purwakarta.geojson successfully!")
else:
    print("No features found.")
