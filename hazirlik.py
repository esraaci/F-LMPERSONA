import pandas as pd
import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
# --- GOOGLE FIREBASE FIRESTORE BAĞLANTISI ---
def init_db():
    if not firebase_admin._apps:
        # VS Code'da duran JSON dosyasının adı
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            # Bulut ortamı için (Streamlit Secrets)
            cred = credentials.Certificate(dict(st.secrets["firebase_credentials"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_db()

# --- BULUT VERİ TABANI KULLANICI FONKSİYONLARI ---
def save_user(username, data):
    # merge=True sayesinde, test çözülünce kullanıcının şifresi silinmez, üzerine eklenir.
    db.collection("users").document(username).set(data, merge=True)

def get_user(username):
    doc = db.collection("users").document(username).get()
    return doc.to_dict() if doc.exists else None

# --- 30 SORULUK MBTI ANALİZ MOTORU ---
def mbti_analiz_motoru(c):
    p = {"E":0, "I":0, "S":0, "N":0, "T":0, "F":0, "J":0, "P":0}
    
    # 1, 5, 11, 15, 28 (E-I)
    if "Kalabalık" in c[0]: p["E"] += 1
    else: p["I"] += 1
    if "yeni çevrelere" in c[4]: p["E"] += 1
    else: p["I"] += 1
    if "kolaydır" in c[10]: p["E"] += 1
    else: p["I"] += 1
    if "hoşlanırım" in c[14]: p["E"] += 1
    else: p["I"] += 1
    if "hareketli ve canlı" in c[27]: p["E"] += 1
    else: p["I"] += 1

    # 2, 12, 16, 17, 22, 24, 26, 29 (S-N)
    if "somut gerçeklere" in c[1]: p["S"] += 1
    else: p["N"] += 1
    if "sıkılırım" in c[11]: p["S"] += 1
    else: p["N"] += 1
    if "yeni şeyler denemeyi" in c[15]: p["N"] += 1
    else: p["S"] += 1
    if "gerçekçi olarak" in c[16]: p["S"] += 1
    else: p["N"] += 1
    if "keşfetmeyi severim" in c[21]: p["N"] += 1
    else: p["S"] += 1
    if "hayal etmeyi severim" in c[23]: p["N"] += 1
    else: p["S"] += 1
    if "talimatları sırasıyla" in c[25]: p["S"] += 1
    else: p["N"] += 1
    if "zaman kaybı olduğunu düşünürüm" in c[28]: p["S"] += 1
    else: p["N"] += 1

    # 3, 8, 13, 18, 21, 27 (T-F)
    if "pratik bir çözüm" in c[2]: p["T"] += 1
    else: p["F"] += 1
    if "Sorumluluklarım ve görevlerim" in c[7]: p["T"] += 1
    else: p["F"] += 1
    if "Gerçekçilik, dürüstlük" in c[12]: p["T"] += 1
    else: p["F"] += 1
    if "verimlilik daha önemlidir" in c[17]: p["T"] += 1
    else: p["F"] += 1
    if "kolayca etkilenmem" in c[20]: p["T"] += 1
    else: p["F"] += 1
    if "Mantık yürütmeye" in c[26]: p["T"] += 1
    else: p["F"] += 1

    # 4, 6, 9, 10, 14, 19, 25, 30 (J-P)
    if "belirsizlikten nefret ederim" in c[3]: p["J"] += 1
    else: p["P"] += 1
    if "düzenli bir şekilde çalışırım" in c[5]: p["J"] += 1
    else: p["P"] += 1
    if "kullanmayı severim" in c[8]: p["J"] += 1
    else: p["P"] += 1
    if "çok önce tamamlamış" in c[9]: p["J"] += 1
    else: p["P"] += 1
    if "plana sadık kalırım" in c[13]: p["J"] += 1
    else: p["P"] += 1
    if "tamamen bitirdikten sonra" in c[18]: p["J"] += 1
    else: p["P"] += 1
    if "direkt uygulamaya geçerim" in c[24]: p["J"] += 1
    else: p["P"] += 1
    if "uygulamaya devam ederdim" in c[29]: p["J"] += 1
    else: p["P"] += 1

    res = ""
    res += "E" if p["E"] >= p["I"] else "I"
    res += "S" if p["S"] >= p["N"] else "N"
    res += "T" if p["T"] >= p["F"] else "F"
    res += "J" if p["J"] >= p["P"] else "P"
    return res


# --- 16 KİŞİLİK TİPİNİN TAMAMINI İÇEREN AKILLI SÜZME MOTORU ---
def dinamik_5000_filtreleme(mbti_kodu, estetik_c):
    
    # --- FIREBASE FIRESTORE BULUT VERİ ÇEKME ADIMI ---
    try:
        filmler_ref = db.collection("filmler")
        sorgu = filmler_ref.where("puan", ">", 6.0).stream()
        
        bulut_filmleri = []
        for doc in sorgu:
            bulut_filmleri.append(doc.to_dict())
            
        bulut_filmleri = sorted(bulut_filmleri, key=lambda x: x.get('puan', 0.0), reverse=True)
        
    except Exception as e:
        return {"HATA": [{"title": f"Bulut veri tabanı bağlantı hatası: {e}", "genres_clean": "Hata", "vote_average": 0.0}]}

    # --- 🎯 16 TİPİN TAMAMI İÇİN KARA LİSTE (NEFRET EDİLEN TÜRLER) ---
    kara_liste = {
        "ISTJ": ["Horror", "Gore"],
        "ISFJ": ["Horror", "War", "Gore"],
        "INFJ": ["Action", "Western"],
        "INTJ": ["Romance", "Musical"],
        "ISTP": ["Musical", "Romance"],
        "ISFP": ["War", "Horror", "History"],
        "INFP": ["War", "Western", "Action"],
        "INTP": ["Romance", "Drama"],
        "ESTP": ["Documentary", "History"],
        "ESFP": ["Documentary", "History", "War"],
        "ENFP": ["Documentary", "History"],
        "ENTP": ["Documentary", "Romance"],
        "ESTJ": ["Fantasy", "Sci-Fi"],
        "ESFJ": ["Horror", "Gore"],
        "ENFJ": ["Horror", "War"],
        "ENTJ": ["Romance", "Drama"]
    }
    
    yasakli_turler = kara_liste.get(mbti_kodu, [])

    # --- 🎯 16 TİPİN TAMAMI İÇİN BEYAZ LİSTE (ÖNCELİKLİ EN UYUMLU RAFLAR) ---
    beyaz_liste = {
        "ISTJ": ["Science Fiction", "Mystery", "Thriller", "Crime"],
        "ISFJ": ["Drama", "Family", "Romance"],
        "INFJ": ["Drama", "Mystery", "Fantasy"],
        "INTJ": ["Science Fiction", "Mystery", "Thriller"],
        "ISTP": ["Action", "Thriller", "Crime", "Adventure"],
        "ISFP": ["Drama", "Romance", "Animation", "Music"],
        "INFP": ["Fantasy", "Drama", "Animation", "Romance"],
        "INTP": ["Science Fiction", "Mystery", "Documentary"],
        "ESTP": ["Action", "Adventure", "Thriller"],
        "ESFP": ["Comedy", "Music", "Animation", "Family"],
        "ENFP": ["Adventure", "Comedy", "Fantasy", "Science Fiction"],
        "ENTP": ["Comedy", "Mystery", "Science Fiction", "Thriller"],
        "ESTJ": ["Action", "Crime", "History", "Thriller"],
        "ESFJ": ["Comedy", "Romance", "Family", "Animation"],
        "ENFJ": ["Drama", "Romance", "Family"],
        "ENTJ": ["Action", "Crime", "Adventure", "Science Fiction"]
    }
    uygun_turler = list(beyaz_liste.get(mbti_kodu, ["Drama"]))

    # --- DİNAMİK RAFLAR: ESTETİK SORULARININ ETKİSİ ---
    if "Neon ışıklar" in estetik_c[5] and "Science Fiction" not in uygun_turler:
        uygun_turler.append("Science Fiction")
    if "Flashbackler" in estetik_c[8] and "Mystery" not in uygun_turler:
        uygun_turler.append("Mystery")
    if "Görsel olarak dışa vurulan aksiyon" in estetik_c[7] and "Action" not in uygun_turler:
        uygun_turler.append("Action")

    # İngilizce tür isimlerini arayüzde ve süzme aşamasında Türkçe karşılıklarına çeviren harita
    tur_cevirici = {
        "science fiction": "Bilim Kurgu", "comedy": "Komedi", "romance": "Romantik",
        "family": "Aile", "animation": "Animasyon", "adventure": "Macera",
        "mystery": "Gizem", "action": "Aksiyon", "music": "Müzik", "musical": "Müzikal",
        "fantasy": "Fantastik", "documentary": "Belgesel", "history": "Tarih",
        "thriller": "Gerilim", "crime": "Suç", "war": "Savaş", "western": "Western", "drama": "Drama"
    }
    
    kategorize_edilmis_havuz = {}
    secilen_filmler_havuzu = set()

    # --- BULUT VERİLERİ ÜZERİNDEN FİLTRELEME DÖNGÜSÜ ---
    for ana_tur in uygun_turler:
        gecerli_kategori_listesi = []

        for film in bulut_filmleri:
            film_adi = film.get('film_adi', 'Bilinmeyen Film')
            
            # Firestore'daki ['Comedy', 'Crime'] listesini alıp hepsini küçük harfe çeviriyoruz
            film_turleri = [str(t).strip().lower() for t in film.get('turler', [])]
            film_puani = film.get('puan', 0.0)

            # Aranacak ana türü ve kara listedeki türleri de küçük harfe çevirerek karşılaştırıyoruz
            ana_tur_lower = ana_tur.lower()
            kara_liste_lower = [k.lower() for k in yasakli_turler]

            # Kara listedeki bir tür bu filmde varsa pas geç
            if any(k in film_turleri for k in kara_liste_lower):
                continue

            # Film hedeflenen ana türü içeriyorsa ve havuzda yoksa listeye ekle
            if ana_tur_lower in film_turleri and film_adi not in secilen_filmler_havuzu:
                # Orijinal büyük harfli tür listesini ekranda güzel görünmesi için birleştiriyoruz
                turler_string = ", ".join(film.get('turler', []))  

                # 🚨 DEĞİŞTİRİLEN KISIM: 'overview' ve diğer verileri garanti altına aldık!
                gecerli_kategori_listesi.append({
                    'title': film_adi,
                    'genres_clean': turler_string, 
                    'vote_average': float(film.get('puan', film.get('vote_average', 0.0))),
                    'year': int(film.get('yil', film.get('year', 2000))),
                    'runtime': int(film.get('sure', film.get('runtime', 100))),
                    
                    # İŞTE BURASI: Hem 'overview' hem 'ozet' ihtimaline karşı ikisini de arıyor, 
                    # turkce_ozet_uret'i kaldırdık çünkü ARAYÜZ DOSYAN BUNU ZATEN ÇEVİRİYOR!
                    'overview': str(film.get('overview', film.get('ozet', ''))), 
                    
                    'is_awarded': str(film.get('odullu_mu', film.get('is_awarded', '🎬 Hayır (Standart Sürüm)')))
                })

            if len(gecerli_kategori_listesi) == 50:
                break

        if gecerli_kategori_listesi:
            tur_adi_tr = ana_tur.replace("Science Fiction", "Bilim Kurgu / Siberpunk").replace("Comedy", "Komedi").replace("Romance", "Romantik").replace("Family", "Aile").replace("Animation", "Animasyon").replace("Adventure", "Macera / Aksiyon").replace("Mystery", "Gizem / Bulmaca Anlatım").replace("Action", "Aksiyon / Çatışma").replace("Music", "Müzikal / Sanatsal").replace("Fantasy", "Fantastik / Rüya Evreni").replace("Documentary", "Belgesel / Gerçek Hayat").replace("History", "Tarih / Dönem")
            kategorize_edilmis_havuz[tur_adi_tr] = gecerli_kategori_listesi

    return kategorize_edilmis_havuz