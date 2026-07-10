import pandas as pd
df = pd.read_excel(r'C:\Users\msyaf\Downloads\petugas.xlsx')

officers = {}

for _, row in df.iterrows():
    for i in range(1, 4):
        col_name = f'[9] PETUGAS 1 ' if i == 1 else (f'[10] PETUGAS 2' if i == 2 else f'[11] PETUGAS 3')
        col_nip = f'[{8+i}.1] NIP PETUGAS {i}'
        col_jab = f'[{8+i}.2] JABATAN PETUGAS {i}'
        
        name = row.get(col_name)
        if pd.isna(name):
            continue
        name = str(name).strip()
        
        nip = str(row.get(col_nip)).strip() if not pd.isna(row.get(col_nip)) else "-"
        jabatan = str(row.get(col_jab)).strip() if not pd.isna(row.get(col_jab)) else "-"
        
        if name not in officers:
            officers[name] = {'nip': nip, 'jabatan': jabatan}

print('names = [')
for name in officers:
    print(f'    "{name}",')
print(']')

print('nips = [')
for name in officers:
    print(f'    "{officers[name]["nip"]}",')
print(']')

print('jabatans = [')
for name in officers:
    print(f'    "{officers[name]["jabatan"]}",')
print(']')
