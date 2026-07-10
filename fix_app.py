import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix fetch_berkas
old_fetch = '''def fetch_berkas(kecamatan=None, status=None, only_urgent=False):
    if USE_MOCK_DATA:
        init_mock_data()
        df = pd.DataFrame(st.session_state.mock_berkas)
    else:
        query = supabase.table('tabel_berkas').select('id, nomor_pelayanan, nomor_nop, nama_pemohon, keterangan_berkas, kecamatan, desa, status_survey, st_x(koordinat_lokasi) as lon, st_y(koordinat_lokasi) as lat, tanggal_input, is_urgent, petugas_1, petugas_2')
        if kecamatan and kecamatan != "Semua":
            query = query.eq('kecamatan', kecamatan)
        if status and status != "Semua":
            query = query.eq('status_survey', status)
        if only_urgent:
            query = query.eq('is_urgent', True)
        response = query.execute()
        df = pd.DataFrame(response.data)
        
    if not df.empty and kecamatan and kecamatan != "Semua":'''

new_fetch = '''def fetch_berkas(kecamatan=None, status=None, only_urgent=False):
    global USE_MOCK_DATA
    df = pd.DataFrame()
    if not USE_MOCK_DATA:
        try:
            query = supabase.table('berkas').select('*')
            if kecamatan and kecamatan != "Semua":
                query = query.eq('kecamatan', kecamatan)
            if status and status != "Semua":
                query = query.eq('status_survey', status)
            if only_urgent:
                query = query.eq('mendesak', True)
            response = query.execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        except Exception as e:
            USE_MOCK_DATA = True
            
    if USE_MOCK_DATA:
        init_mock_data()
        df = pd.DataFrame(st.session_state.mock_berkas)
        if not df.empty:
            df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        
    if not df.empty and kecamatan and kecamatan != "Semua":'''
content = content.replace(old_fetch, new_fetch)

# 2. Fix insert block
old_insert = '''            else:
                st.success("Berkas berhasil disimpan ke Database.")'''

new_insert = '''            else:
                try:
                    db_berkas = {
                        'no_pelayanan': nopel_baru,
                        'kategori_berkas': kat_baru,
                        'nomor_nop': nop_clean,
                        'nama_pemohon': pemohon_baru,
                        'mendesak': urgensi_baru,
                        'kecamatan': kecamatan_baru,
                        'kelurahan': kelurahan_baru,
                        'lokasi_map': gmaps_link,
                        'latitude': lat_val,
                        'longitude': lon_val,
                        'status_survey': 'Belum'
                    }
                    supabase.table('berkas').insert(db_berkas).execute()
                    st.success(f"Berhasil! Berkas {nopel_baru} (Kel. {kelurahan_baru}) berhasil disimpan ke Database.")
                except Exception as e:
                    st.error(f"Gagal menyimpan ke database (Pastikan tabel 'berkas' sudah dibuat di SQL Editor). Error: {e}")'''
content = content.replace(old_insert, new_insert)

# 3. Fix update penugasan
old_update = '''                        update_data = {
                            "status_survey": "Dijadwalkan",
                            "petugas_1": selected_pegawai[0] if len(selected_pegawai) > 0 else None,
                            "petugas_2": selected_pegawai[1] if len(selected_pegawai) > 1 else None
                        }
                        supabase.table("tabel_berkas").update(update_data).eq("id", b_id).execute()'''

new_update = '''                        update_data = {
                            "status_survey": "Dijadwalkan",
                            "petugas_survey": " & ".join(selected_pegawai)
                        }
                        try:
                            supabase.table("berkas").update(update_data).eq("id", b_id).execute()
                        except Exception as e:
                            st.error(f"Gagal update database: {e}")'''
content = content.replace(old_update, new_update)

# 4. Fix delete
old_delete = '''                    res = supabase.table('tabel_berkas').delete().eq('nomor_pelayanan', str(del_nopel).strip()).execute()'''
new_delete = '''                    try:
                        res = supabase.table('berkas').delete().eq('no_pelayanan', str(del_nopel).strip()).execute()
                    except:
                        res = type('obj', (object,), {'data': []})'''
content = content.replace(old_delete, new_delete)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done modifying app.py')
