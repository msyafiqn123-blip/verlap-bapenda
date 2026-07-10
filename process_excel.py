import pandas as pd
import json

# Read the excel file
df = pd.read_excel('C:/Users/msyaf/Downloads/DHKP 31.xlsx')

# Filter out rows where nm_kecamatan or nm_kelurahan is NaN
df = df.dropna(subset=['nm_kecamatan', 'nm_kelurahan'])

# Create a mapping of Kecamatan -> List of Kelurahan
referensi = {}
for kec in df['nm_kecamatan'].unique():
    # skip OBJEK KHUSUS if necessary, but let's keep everything just in case
    if str(kec).strip() == "":
        continue
    kelurahans = df[df['nm_kecamatan'] == kec]['nm_kelurahan'].unique().tolist()
    referensi[str(kec)] = [str(k) for k in kelurahans]

# Save to JSON
with open('referensi_wilayah.json', 'w') as f:
    json.dump(referensi, f, indent=4)

print("Berhasil mengekstrak data wilayah dari Excel.")
