import streamlit as st
import requests # Eğer yüklü değilse terminale: pip install requests yaz.

# --- TMDB API İLE GÖRSEL ÇEKME FONKSİYONU ---
@st.cache_data(show_spinner=False)  # KULLANICIYA KOD GÖSTERİLMESİNİ ENGELLER
def afis_getir(film_adi, film_id=None):
    api_key = "d4aeee1a7debef914b42180183d27991"
    base_image_url = "https://image.tmdb.org/t/p/w500" 
    
    if film_id:
        url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={api_key}"
        try:
            cevap = requests.get(url).json()
            if "poster_path" in cevap and cevap["poster_path"]:
                return base_image_url + cevap["poster_path"]
        except:
            pass
            
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_adi}"
    try:
        cevap = requests.get(search_url).json()
        if cevap["results"] and cevap["results"][0].get("poster_path"):
            return base_image_url + cevap["results"][0]["poster_path"]
    except:
        pass
        
    return "https://via.placeholder.com/500x750?text=Afi%C5%9F+Bulunamad%C4%B1"

# --- TMDB API İLE FRAGMAN (ALTYAZI > DUBLAJ > ORİJİNAL) ÖNCELİKLİ ÇEKME FONKSİYONU ---
@st.cache_data(show_spinner=False)  # KULLANICIYA KOD GÖSTERİLMESİNİ ENGELLER
def fragman_getir(film_adi, film_id=None):
    api_key = "d4aeee1a7debef914b42180183d27991"
    
    if not film_id:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_adi}"
        try:
            cevap = requests.get(search_url).json()
            if cevap.get("results"):
                film_id = cevap["results"][0]["id"]
        except:
            pass
            
    if not film_id:
        return None
        
    # 2. ADIM: TÜRKÇE Videoları getir (Artık daha geniş çaplı arıyor)
    url_tr = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={api_key}&language=tr-TR"
    try:
        cevap_tr = requests.get(url_tr).json()
        if "results" in cevap_tr:
            dublaj_key = None
            genel_tr_key = None
            
            for video in cevap_tr["results"]:
                # YENİLİK: Sadece Trailer değil, Teaser ve Clipleri de kontrol et
                if video["site"] == "YouTube" and video["type"] in ["Trailer", "Teaser", "Clip", "Featurette"]:
                    isim = video["name"].lower()
                    
                    if "altyaz" in isim or "alt yaz" in isim:
                        return video["key"]
                    elif "dublaj" in isim:
                        dublaj_key = video["key"]
                    elif not genel_tr_key:
                        genel_tr_key = video["key"]
            
            if dublaj_key:
                return dublaj_key
            elif genel_tr_key:
                return genel_tr_key
    except:
        pass
        
    # 3. ÖNCELİK: Türkiye bölgesinde HİÇBİR ŞEY yoksa ORİJİNAL fragmanı getir
    url_orj = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={api_key}"
    try:
        cevap_orj = requests.get(url_orj).json()
        if "results" in cevap_orj:
            for video in cevap_orj["results"]:
                if video["site"] == "YouTube" and video["type"] in ["Trailer", "Teaser"]:
                    return video["key"]
    except:
        pass
        
    return None

    # 2. ADIM: TÜRKÇE Videoları getir ve hiyerarşiye göre seç
    url_tr = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={api_key}&language=tr-TR"
    try:
        cevap_tr = requests.get(url_tr).json()
        if "results" in cevap_tr:
            dublaj_key = None
            genel_tr_key = None
            
            for video in cevap_tr["results"]:
                if video["site"] == "YouTube" and video["type"] == "Trailer":
                    isim = video["name"].lower()
                    
                    # 1. ÖNCELİK: Altyazı kelimesi geçiyorsa anında bunu döndür ve bitir
                    if "altyaz" in isim or "alt yaz" in isim:
                        return video["key"]
                        
                    # 2. ÖNCELİK: Dublaj kelimesi geçiyorsa hafızaya al (Altyazı bulamazsak bunu kullanacağız)
                    elif "dublaj" in isim:
                        dublaj_key = video["key"]
                        
                    # 3. ÖNCELİK: İsmi belirsizse ama Türkçe veritabanındaysa yedekte tut
                    elif not genel_tr_key:
                        genel_tr_key = video["key"]
            
            # Döngü bitti, altyazı bulamadık. Varsa dublajı, o da yoksa isimsiz Türkçe videoyu yolla
            if dublaj_key:
                return dublaj_key
            elif genel_tr_key:
                return genel_tr_key
    except:
        pass
        
    # 4. ÖNCELİK: Türkiye bölgesinde HİÇBİR ŞEY yoksa ORİJİNAL fragmanı getir
    url_orj = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={api_key}"
    try:
        cevap_orj = requests.get(url_orj).json()
        if "results" in cevap_orj:
            for video in cevap_orj["results"]:
                if video["site"] == "YouTube" and video["type"] == "Trailer":
                    return video["key"]
    except:
        pass
        
    return None
from deep_translator import GoogleTranslator
from hazirlik import save_user, get_user, mbti_analiz_motoru, dinamik_5000_filtreleme

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(
    page_title="FILMPERSONA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FIGMA PREMIUM FERAH UI/UX TASARIM ENJEKSİYONU (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stWidgetLabel, label {
        font-family: 'Outfit', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #1E1E2F !important;
    }
    
    h1, h2, h3, h4, h5, h6, .stSubheader {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #0F0F1A !important;
        letter-spacing: -0.5px;
    }

    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important;}
    .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}
    
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    .stForm, .auth-card {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 24px !important;
        padding: 40px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.06) !important;
    }

    .stRadio label {
        color: #0F0F1A !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        line-height: 1.5 !important;
        margin-bottom: 8px !important;
    }
    
    .stRadio div[role="radiogroup"] {
        background-color: #F3F4F6 !important;
        padding: 14px !important;
        border-radius: 12px !important;
        border: 1px solid #D1D5DB !important;
        margin-bottom: 15px !important;
    }

    .stRadio div[role="radiogroup"] label p {
        color: #374151 !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }

    .custom-navbar {
        background: #FFFFFF;
        padding: 18px 30px;
        border-radius: 16px;
        margin-bottom: 35px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #E5E7EB;
        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
    }

    /* MATRİS BUTONU (KIRMIZI) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #FF3366 0%, #FF1F4B 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(255, 51, 102, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 51, 102, 0.4) !important;
    }

    /* TEMİZLE BUTONU (GRİ OUTLINE) */
    .clear-btn-container div.stButton > button:first-child {
        background: #FFFFFF !important;
        color: #4B5563 !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
        border-radius: 12px !important;
    }
    .clear-btn-container div.stButton > button:first-child:hover {
        background: #F9FAFB !important;
        color: #1F2937 !important;
        border-color: #9CA3AF !important;
        transform: none !important;
    }

    .movie-card {
        background: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #E5E7EB;
        padding: 22px;
        margin-bottom: 25px;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03);
        transition: all 0.3s ease-in-out;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        border-color: #FF3366;
        box-shadow: 0 12px 25px rgba(255, 51, 102, 0.12);
    }
    
    .category-header {
        color: #FF3366 !important;
        border-left: 5px solid #FF3366;
        padding-left: 12px;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    
    /* TIKLANABİLİR KUSURSUZ BEYAZ KUTU STİLLERİ */
/* --- STREAMLIT BUTONUNUN İÇİNDEKİ GİZLİ BOŞLUKLARI YOK ETME KODU --- */

    /* 1. Butonu net bir yüksekliğe (32px) hapsediyoruz ve taşan beyazlıkları kesiyoruz */
    div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 32px !important;     /* NE EKSİK NE FAZLA, KESİN 32 PİKSEL */
        min-height: 32px !important; 
        max-height: 32px !important; /* Aşağı doğru uzamasını kesinlikle yasakladık */
        padding: 0px !important;
        border: 1px solid #FF3366 !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        color: #FF3366 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important; /* İŞTE O ALTTTAKİ BEYAZLIĞI KESİP ATAN SİHİRLİ KOD */
    }

    /* 2. Butonun içindeki TÜM etiketlere (*) nükleer müdahale */
    div[data-testid="stButton"] > button * {
        margin: 0px !important;      /* İçerideki tüm alt boşluklar SIFIRLANDI */
        padding: 0px !important;
        line-height: 1 !important;
        height: auto !important;
        min-height: 0px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: inherit !important;
    }

    /* 3. Hover (Üzerine gelme) efekti */
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stButton"] > button:active,
    div[data-testid="stButton"] > button:focus {
        background-color: #FF3366 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 10px rgba(255, 51, 102, 0.2) !important;
        outline: none !important;
    }
    div.movie-grid-col div.stButton > button:hover p,
    div.movie-grid-col div.stButton > button:focus p,
    div.movie-grid-col div.stButton > button:active p {
        color: #0F0F1A !important;
    }
            
    /* AÇILAN KARTIN (POP-UP) İÇ STİLLERİ */
    .pop-meta-row { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; margin: 12px 0 !important; }
    .pop-badge { font-size: 12px !important; padding: 6px 12px !important; border-radius: 8px !important; background-color: #F3F4F6 !important; color: #374151 !important; font-weight: 600 !important; border: 1px solid #E5E7EB; }
    .pop-badge-awarded-gold { background-color: #FEF3C7 !important; color: #D97706 !important; border: 1px solid #FCD34D !important; }
    .pop-overview { background: #F9FAFB; padding: 18px; border-radius: 12px; border: 1px solid #F3F4F6; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

if 'sayfa' not in st.session_state:
    st.session_state.sayfa = "Giris"

# --- ADIM 1: GİRİŞ VE KAYIT EKRANI (MİRAS HESAP KURTARMA DESTEKLİ) ---
import hashlib
import time

if st.session_state.sayfa == "Giris":
    # 🎨 NOKTA ATIŞI CSS: PEMBEYİ EZ, UZUN GRİ ÇİZGİYİ YOK ET, SEKMELERİ ORTALA
    st.markdown("""
    <style>
        /* 1. Sekmelerin altındaki şeffaf beyazlığı ve panel kutusunu yok et */
        [data-testid="stTabs"], 
        [data-baseweb="tab-panel"],
        [role="tabpanel"],
        .stTabs {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* 🚀 2. UZUN GRİ ÇİZGİYİ TAMAMEN SİL VE SEKMELERİ ORTALA */
        div[data-baseweb="tab-list"] {
            border-bottom: none !important; /* O sinir bozucu uzun gri çizgiyi siler */
            justify-content: center !important; /* İki sekmeyi formun tam ortasına alır */
            gap: 20px !important; /* İki sekme arasına şık bir boşluk bırakır */
        }
        
        /* Seçili sekmenin altındaki minik aktiflik çizgisini pembeden laciverte çevir */
        div[data-baseweb="tab-highlight"] {
            background-color: #2E5B88 !important; 
        }

        /* 3. DİKKAT: SADECE TABS İÇİNDEKİ BUTONLARI HEDEF ALIYORUZ! (Global pembeyi yener) */
        div[data-testid="stTabs"] div[data-testid="stButton"] > button {
            background: #2E5B88 !important;
            background-color: #2E5B88 !important;
            color: #FFFFFF !important;
            border: 2px solid #2E5B88 !important;
            border-radius: 8px !important;
            height: 48px !important;
            min-height: 48px !important;
            width: 100% !important;
            box-shadow: 0 4px 10px rgba(46, 91, 136, 0.2) !important;
        }
        
        /* İçindeki yazıyı beyaz yap */
        div[data-testid="stTabs"] div[data-testid="stButton"] > button p {
            color: #FFFFFF !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        
        /* 4. Butonun üzerine gelince (Hover) bir tık koyu lacivert olsun (#1A3D63) */
        div[data-testid="stTabs"] div[data-testid="stButton"] > button:hover {
            background: #1A3D63 !important;
            background-color: #1A3D63 !important;
            border: 2px solid #1A3D63 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 📐 Ekranı biraz aşağı itiyoruz (Ferah durması için)
    st.markdown("""
    <div class="custom-navbar" style="margin-bottom: 5px;">
        <h2 style="margin:0; color:#FF3366; font-size:26px;">🎬 FILMPERSONA</h2>
        <span style="color:#6B7280; font-size:14px; font-weight:500;">v3.1 Secure Edition</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 8vh;'></div>", unsafe_allow_html=True)
    # 📏 ORTALAMA VE DARALTMA
    col_l, col_m, col_r = st.columns([1, 1.2, 1]) 
    
    with col_m:
        tab_giris, tab_kayit = st.tabs(["🔐 Giriş Yap", "📝 Yeni Kayıt Ol"])
        
        # --- GİRİŞ YAP SEKME İÇERİĞİ ---
        with tab_giris:
            st.markdown("<h3 style='margin-top:5px; margin-bottom: 20px; color:#0F0F1A; font-size: 22px; text-align: center;'>🍿 Hoş Geldin</h3>", unsafe_allow_html=True)
            
            g_kullanici = st.text_input("Kullanıcı Adı", placeholder="Örn: matrix_neo", key="g_isim", label_visibility="collapsed")
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            g_sifre = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin", key="g_sif", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sisteme Giriş Yap", key="btn_giris", use_container_width=True):
                if g_kullanici and g_sifre:
                    u_data = get_user(g_kullanici)
                    if u_data:
                        if "sifre" not in u_data:
                            st.error("Bu hesap eski sistemde oluşturulmuş ve şifresi bulunmuyor! Lütfen 'Yeni Kayıt Ol' sekmesine geçip hesabınızı kurtarın.")
                        else:
                            girilen_sifre_kripto = hashlib.sha256(g_sifre.encode()).hexdigest()
                            if u_data.get("sifre") == girilen_sifre_kripto:
                                st.session_state.username = g_kullanici
                                st.session_state.user_info = u_data
                                
                                if "mbti" in u_data:
                                    st.session_state.sayfa = "Platform"
                                else:
                                    st.session_state.sayfa = "Test"
                                st.rerun()
                            else:
                                st.error("Hatalı şifre girdiniz! Lütfen tekrar deneyin.")
                    else:
                        st.error("Böyle bir kullanıcı bulunamadı. Lütfen önce kayıt olun.")
                else:
                    st.warning("Lütfen kullanıcı adı ve şifrenizi eksiksiz girin.")

        # --- KAYIT OL SEKME İÇERİĞİ ---
        with tab_kayit:
            st.markdown("<h3 style='margin-top:5px; margin-bottom: 20px; color:#0F0F1A; font-size: 22px; text-align: center;'>🚀 Sinema Evrenine Katıl</h3>", unsafe_allow_html=True)
            
            k_kullanici = st.text_input("Kullanıcı Adı Belirleyin", placeholder="Kullanıcı adı", key="k_isim", label_visibility="collapsed")
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            k_sifre1 = st.text_input("Şifre Belirleyin", type="password", placeholder="Şifre (En az 6 karakter)", key="k_sif1", label_visibility="collapsed")
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            k_sifre2 = st.text_input("Şifreyi Tekrar Girin", type="password", placeholder="Şifre tekrar", key="k_sif2", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Kayıt Ol", key="btn_kayit", use_container_width=True):
                if k_kullanici and k_sifre1 and k_sifre2:
                    if k_sifre1 != k_sifre2:
                        st.error("Şifreler uyuşmuyor, lütfen kontrol edin.")
                    elif len(k_sifre1) < 6:
                        st.warning("Güvenliğiniz için şifreniz en az 6 karakter olmalıdır.")
                    else:
                        kullanici_var_mi = get_user(k_kullanici)
                        if kullanici_var_mi and "sifre" in kullanici_var_mi:
                            st.error("Bu kullanıcı adı zaten alınmış ve şifrelenmiş. Lütfen başka bir tane deneyin.")
                        else:
                            kriptolu_sifre = hashlib.sha256(k_sifre1.encode()).hexdigest()
                            hesap_verisi = {"sifre": kriptolu_sifre}
                            save_user(k_kullanici, hesap_verisi)
                            
                            guncel_u_data = get_user(k_kullanici)
                            st.session_state.username = k_kullanici
                            st.session_state.user_info = guncel_u_data
                            
                            if guncel_u_data and "mbti" in guncel_u_data:
                                st.success("Eski hesabınız kurtarıldı! Sürpriz film raflarınıza aktarılıyorsunuz...")
                                st.session_state.sayfa = "Platform"
                            else:
                                st.success("Hesabınız başarıyla oluşturuldu! Test ekranına yönlendiriliyorsunuz...")
                                st.session_state.sayfa = "Test"
                                
                            time.sleep(1.5)
                            st.rerun()
                else:
                    st.warning("Lütfen tüm kayıt alanlarını doldurun.")

# --- ADIM 2: TAM TEST EKRANI ---
elif st.session_state.sayfa == "Test":
    st.markdown(f"""
    <div class="custom-navbar">
        <h2 style="margin:0; color:#0F0F1A; font-size:22px;">🧠 Karakter & Estetik Analiz Merkezi</h2>
        <span style="color:#FF3366; font-size:14px; font-weight:bold;">Kullanıcı: {st.session_state.username}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if "form_id" not in st.session_state:
        st.session_state.form_id = 0
        
    with st.form(key=f"dev_envanter_{st.session_state.form_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='color:#FF3366; border-bottom:2px solid #FF3366; padding-bottom:8px; margin-bottom:25px;'>📊 Bölüm 1: Bilişsel Kişilik Analizi</h3>", unsafe_allow_html=True)
            q1 = st.radio("1-Enerjini nasıl toplarsın?", ["Tek başımayken", "Hareketli ve kalabalık yerlerde"], index=None)
            q2 = st.radio("2-Zihinsel olarak hangisine daha çok odaklanırsın?", ["Çevredeki detaylara ve somut gerçeklere", "Tahminlere ve olasılıklara"], index=None)
            q3 = st.radio("3-Arkadaşının bir sorunu olduğunda ilk yapacağın şey ne olurdu?", ["Ona duygusal olarak destek olmak", "Sorununa pratik bir çözüm üretmek"], index=None)
            q4 = st.radio("4-Hayata karşı genel planlama tarzın nasıldır?", ["Her zaman planlıyımdır ve belirsizlikten nefret ederim", "Sabit planlar yapmam, duruma göre esnetirim"], index=None)
            q5 = st.radio("5-Sosyal hayatında düzenli olarak yeni arkadaşlar edinir misin?", ["Evet, düzenli olarak yeni çevrelere girerim", "Hayır, mevcut arkadaş çevrem bana yeterlidir"], index=None)
            q6 = st.radio("6-Çalısma tarzın genel olarak nasıl ilerler?", ["Anlık enerji patlamalarıyla son ana doğru çalışırım", "Planlı, gündelik ve düzenli bir şekilde çalışırım"], index=None)
            q7 = st.radio("7-Çok baskı ve stres altında kaldığında sakinliğini koruyabilir misin?", ["Evet, sakin kalabilirim", "Hayır, sakin kalmakta zorlanırım"], index=None)
            q8 = st.radio("8-Hayatında ve çalışmalarında senin için hangisi önceliklidir?", ["Sorumluluklarım ve görevlerim", "Kişisel ihtiyaçlarım ve konforum"], index=None)
            q9 = st.radio("9-Programlar, takvimler ve listeler gibi düzenleme araçlarını kullanmayı sever misin?", ["Evet, planlama araçlarını kullanmayı severim", "Hayır, bu tarz araçları kullanmaya gerek duymam"], index=None)
            q10 = st.radio("10-Sana verilen projeleri ve ödevleri ne zaman tamamlarsın?", ["Teslim tarihinden çok önce tamamlamış olurum", "Genellikle son güne ve son ana bırakırım"], index=None)
            q11 = st.radio("11-Birisine yaklaşmak ve sohbet başlatmak senin için kolay mıdır?", ["Evet, sohbet başlatmak benim için kolaydır", "Hayır, sohbet başlatmak benim için zordur"], index=None)
            q12 = st.radio("12-Tartışılan olaylar felsefi ve soyut hale geldiğinde sıkılıp ilgini kaybeder misin?", ["Evet, sıkılırım ve ilgimi kaybederim", "Hayır, aksine daha çok ilgimi çeker"], index=None)
            q13 = st.radio("13-İlişkilerinde ve kararlarında hangisi senin için daha önemlidir?", ["İnsanların hisleri ve kırılmaması", "Gerçekçilik, dürüstlük ve netlik"], index=None)
            q14 = st.radio("14-Gününün hiçbir plan yapmadan, tamamen akışta geçmesine izin verir misin?", ["Evet, plan yapmadan akışta kalabilirim", "Hayır, belirli bir plan yapıp o plana sadık kalırım"], index=None)
            q15 = st.radio("15-Kalabalık ekip etkinliklerine ve grup organizasyonlarına katılmaktan hoşlanır mısın?", ["Evet, ekip etkinliklerine katılmaktan hoşlanırım", "Hayır, bu tarz etkinliklerden pek hoşlanmam"], index=None)
            q16 = st.radio("16-Hayatında yeni ve henüz denenmemiş şeyleri tecrübe etmeyi sever misin?", ["Evet, yeni şeyler denemeyi çok severim", "Hayır, bildiğim ve güvendiğim yolları tercih ederim"], index=None)
            q17 = st.radio("17-Kendini hayata karşı daha çok nasıl bir insan olarak görürsün?", ["Tamamen ayakları yere basan bir gerçekçi olarak", "Gelecekte olabilecek olasılıklara odaklanan biri olarak"], index=None)
            q18 = st.radio("18-Duygusal yönleri göz ardı etmek bile olsa iş hayatında verimliliğe önem verir misin?", ["Evet, her koşulda verimlilik daha önemlidir", "Hayır, duygusal ve insani yönler daha önemlidir"], index=None)
            q19 = st.radio("19-Günün sonunda dinlenmeye çekilmeden önce sorumluluklarını ve işlerini bitirir misin?", ["Evet, işlerimi tamamen bitirdikten sonra dinlenirim", "Hayır, işlerimi genellikle daha sonraya ertelerim"], index=None)
            q20 = st.radio("20-Günlük hayatında ruh halin ve modun çok hızlı değişir mi?", ["Evet, ruh halim çok hızlı değişebilir", "Hayır, ruh halim genel olarak dengeli ve sabittir"], index=None)

        with col2:
            st.markdown("<h3 style='color:#FF9900; border-bottom:2px solid #FF9900; padding-bottom:8px; margin-bottom:25px;'>🎬 Bölüm 2: Sinematik Estetik ve Tercih</h3>", unsafe_allow_html=True)
            q21 = st.radio("21-Karar alırken duygusal argümanlar ve duygusal durumlar seni kolay kolay etkiler mi?", ["Evet, duygusal yaklaşımlardan kolayca etkilenirim", "Hayır, mantıklı argümanlar ararım, kolay etkilenmem"], index=None)
            q22 = st.radio("22-Alışılmadık, marjinal fikirleri ve farklı bakış açılarını keşfetmeyi sever misin?", ["Evet, farklı ve sıra dışı fikirleri keşfetmeyi severim", "Hayır, daha geleneksel ve kabul görmüş fikirleri severim"], index=None)
            q23 = st.radio("23-Uzun zaman önce yaptığın hatalar ve kaçırdığın fırsatlar seni halen daha rahatsız eder mi?", ["Evet, geçmişteki hatalarım beni halen rahatsız eder", "Hayır, geçmişe takılmam, her zaman önüme bakarım"], index=None)
            q24 = st.radio("24-Dünyanın gelecekte nasıl bir yer olabileceği hakkında konuşmayı sever misin?", ["Evet, geleceği konuşmayı ve hayal etmeyi severim", "Hayır, bu tarz konuşmalar benim için zaman kaybıdır"], index=None)
            q25 = st.radio("25-Bir kararın doğru olduğunu hissettiğinde, derinlemesine düşünmeden direkt uygulamaya geçer misin?", ["Evet, doğru hissettiğim an direkt uygulamaya geçerim", "Hayır, acele etmem, önce üzerine iyice düşünürüm"], index=None)
            q26 = st.radio("26-Kurulum talimatı olan yeni bir eşya aldığında montajı nasıl yaparsın?", ["Herhangi bir adımı atlamadan, talimatları sırasıyla izlerim", "Talimatlara bakmam, yaratıcılığımı kullanarak kurarım"], index=None)
            q27 = st.radio("27-Önemli bir seçim yaparken hangisine daha çok güvenirsin?", ["Mantık yürütmeye ve nesnel verilere", "Duygusal sezgilerime ve iç sesime"], index=None)
            q28 = st.radio("28-Nasıl bir çalışma ortamına sahip bir işte çalışmak isterdin?", ["Zamanımın çoğunu tek başıma geçirebileceğim sakin bir iş", "İnsanlarla iç içe olabileceğim, hareketli ve canlı bir yer"], index=None)
            q29 = st.radio("29-Soyut ve felsefi soruların tamamen zaman kaybı olduğunu düşünür müsünüz?", ["Evet, soyut felsefi soruların zaman kaybı olduğunu düşünürüm", "Hayır, bu tarz soruların değerli ve anlamlı olduğunu düşünürüm"], index=None)
            q30 = st.radio("30-Eğer yapacağınız bir iş kesintiye uğrarsa ilk bulduğunuz fırsatta planınızı uygulamaya devam eder miydiniz?", ["Evet, ilk fırsatta planımı kaldığı yerden uygulamaya devam ederdim", "Hayır, planım bozulduğunda adaptasyon sağlamakta zorlanırım"], index=None)
            
            st.divider()
            st.subheader("Bölüm 3: Sinematik Tercihler")
            q31 = st.radio("31-Karakter Odaklı: Bir filmde senin için en önemli olan hangisidir?", ["Kendime benzeyen, stratejik ve akılcı karakterler (Ayna Etkisi)", "Benden çok farklı, ilham veren ve duygusal kahramanlar (Tamamlayıcı Etki)"], index=None)
            q32 = st.radio("32-Türün Ruhu: Hikaye nasıl işlenmeli?", ["Sembolik anlatımlar, metaforlar ve alt metinler (Sezgisel)", "Net, anlaşılır ve aksiyon dolu bir kurgu (Duyumsayan)"], index=None)
            q33 = st.radio("33-Duygusal Derinlik: Filmin yarattığı his hangisi olmalı?", ["Melankolik, hüzünlü ama anlamlı (Hissetme)", "Adrenalin dolu, merak uyandırıcı ve mantık oyunlu (Düşünme)"], index=None)
            q34 = st.radio("34-Kurgu Temposu: İzlediğin filmin hızı senin için ne kadar önemli?", ["Yavaş ilerleyen, her detayı sindirten bir derinlik (Planlı)", "Hızlı, dinamik ve her an sürprizlere açık bir tempo (Esnek)"], index=None)
            q35 = st.radio("35-Final Beklentisi: Bir film bittiğinde sende ne bırakmalı?", ["Tüm soruların yanıtlandığı net bir kapanış", "Zihnimi kurcalayan, ucu açık ve yoruma dayalı bir son"], index=None)
            q36 = st.radio("36-Renk Paleti ve Işık: Görsel olarak hangi tarz seni daha çok içine çeker?", ["Pastel tonlar, doğal ışık ve huzurlu görseller", "Neon ışıklar, yüksek kontrast veya siyah-beyazın keskinliği"], index=None)
            q37 = st.radio("37-Müzik ve Ses: Bir filmde müziğin rolü sence ne olmalı?", ["Hikayenin önüne geçmeyen, atmosferi sessizce destekleyen melodiler", "Epik orkestralar veya baskın şarkılarla duyguyu doruğa çıkaran bir yapı"], index=None)
            q38 = st.radio("38-Siddet ve Gerilim: Ekrandaki gerilim/çatışma seviyesi ne olmalı?", ["Psikolojik baskı ve 'görünmeyen' bir tehlikenin yarattığı gerilim", "Görsel olarak dışa vurulan aksiyon, dövüş veya fiziksel çatışma"], index=None)
            q39 = st.radio("39-Kurgu Tekniği: Anlatım tarzında hangisi seni daha çok heyecanlandırır?", ["Flashbackler (geriye dönüşler) ve paralel evrenlerle dallanan karmaşık bir kurgu", "Başı sonu belli, akıcı ve tek bir kurgu çizgisi"], index=None)
            q40 = st.radio("40-Küresel Perspektif: Hikayenin geçtiği yer tercihin nedir?", ["Kendi kültürüme yakın tanıdık mekanlar", "Egzotik ülkeler, hayal ürünü diyarlar veya farklı kültürlerin derinlikleri"], index=None)

        # Butonlar İçin Alt Düzen Alt Gridi
        btn_col1, btn_col2 = st.columns(2)
        with btn_col2:
            submit_btn = st.form_submit_button("Matrisi Çalıştır ve Filmleri Kategorize Et")
        with btn_col1:
            st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
            clear_btn = st.form_submit_button("Seçimleri Temizle / Sıfırla")
            st.markdown('</div>', unsafe_allow_html=True)

        if clear_btn:
            st.session_state.form_id += 1
            st.rerun()

        if submit_btn:
            cevaplar = [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21,q22,q23,q24,q25,q26,q27,q28,q29,q30]
            estetik = [q31,q32,q33,q34,q35,q36,q37,q38,q39,q40]
            
            if None in cevaplar or None in estetik:
                st.error("Lütfen analizin eksiksiz hesaplanabilmesi için 40 sorunun tamamını işaretleyin!")
            else:
                mbti_kodu = mbti_analiz_motoru(cevaplar)
                kategori_sozlugu = dinamik_5000_filtreleme(mbti_kodu, estetik)
                
                data = {"username": st.session_state.username, "mbti": mbti_kodu, "kategoriler": kategori_sozlugu}
                save_user(st.session_state.username, data)
                st.session_state.user_info = data
                st.session_state.sayfa = "Platform"
                st.rerun()

# --- ADIM 3: GERÇEK GRUPLANMIŞ SİNEMA PLATFORMU ---
elif st.session_state.sayfa == "Platform":
    st.markdown("""
    <style>
        div.stButton > button:first-child,
        div.stButton > button {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #0F0F1A !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 16px !important;
            height: 220px !important;
            width: 100% !important;
            padding: 20px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            align-items: flex-start !important;
            text-align: left !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
            white-space: pre-wrap !important;
            transition: all 0.3s ease-in-out !important;
        }
        
        div.stButton > button:first-child p,
        div.stButton > button p {
            font-size: 14px !important;
            line-height: 1.5 !important;
            color: #0F0F1A !important;
            margin: 0 !important;
        }

        div.stButton > button:first-child:hover,
        div.stButton > button:first-child:focus,
        div.stButton > button:first-child:active,
        div.stButton > button:hover,
        div.stButton > button:focus,
        div.stButton > button:active {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            border-color: #9CA3AF !important;
            color: #0F0F1A !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
            transform: translateY(-4px) !important;
            outline: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    u = st.session_state.user_info
    mbti_kodu = u.get('mbti', 'INTJ')

    # --- 16 KİŞİLİK TİPİN SN TÜM VERİ MATRİSİ ---
    mbti_sozluk = {
        "INFP": {"unvan": "Arabulucu", "ozet": "Kişisel değerlerini önceliklendiren ve dünyayı daha iyi bir yer haline getirmeyi amaçlayan içe dönük ve idealist 'Arabulucu'lardır. Düşünceli ve samimidirler, iyi dinleyiciler ve sırdaşlar olurlar. İç dünyaları şahane hazineler ile doludur ve sanatsal yaratıları genellikle insanlığın güzelliğini ve sıcaklığını ifade eder. INFP'ler çatışmadan kaçınmayı tercih ederler, ancak değerlerine tehdit geldiğinde tutkulu savunucular haline gelebilirler.",
                 "maddeler": ["Yaratıcı hayalperest", "Ruhun sesi", "Derin sezgi", "Nazik ama güçlü", "Gerçekliğe sadık", "Sınırsız empati", "İç pusula", "Tutkuyla hareket eder", "Düşünceli ve detaycı", "Sanatsal hassasiyet", "İşinde derinlik", "Ömür boyu öğrenici", "Pozitif değişim elçisi", "Dünya vatandaşı", "Bağımsız düşünür", "Dil öğrenmede yetenekli"]},
        "INFJ": {"unvan": "Savunucu", "ozet": "İdealist ve merhametli 'Savunucu'lar olarak en nadir kişilik tipidir. Empati kurma yetenekleri ve diğer insanların niyetlerini ve duygularını anlamalarıyla bilinirler. Sağlam değer sistemleri ve kendilerini ve çevrelerini iyileştirme isteği olan gizemli ve bilge mükemmeliyetçiler olarak tarif edilirler. Yaratıcı ifade alanında başarılıdırlar ve danışmanlık veya yazı işleri gibi kariyerlere ilgi duyabilirler.",
                 "maddeler": ["Derin sezgi", "Anlam arayıcısı", "Şifalı bir varlık", "Düşünerek konuşur", "Dirençli ve kararlı", "Duygusal derinlik", "Sessiz liderlik", "Dönüştürücü etki", "Amaç odaklı", "Çok seçici", "Enerjiye karşı hassas", "İnsanları sezgisel okur", "Nadir ve gizemli", "Yaratıcı derinlik", "Ruhsal arayış", "Felsefi kafa"]},
        "ENFP": {"unvan": "Kampanyacı", "ozet": "İdealizm ve hayal kırıklığı ile tanınan hayalperest ve enerjik bir 'Kampanyacı'dır. Genellikle birçok yetenek ve beceriye sahiptirler ve diğerlerini ilham verme ve motive etme yetenekleriyle tanınırlar. ENFP'ler dış dünyaya karşı duyarlıdır ognellikle keşfetme, yaratma ve yenilik yapma konusunda güçlü bir doğaya sahiptirler. ENFP'ler çocuksu bir hayranlık ve iyimserlik, hızlı bir zihin ve sorunlara yaratıcı çözümler bulma yeteneğine sahiptirler. İlişkilerine değer verirler ve kendilerine sadık olma ihtiyacı duyarlar.",
                 "maddeler": ["Bitmeyen fikirler", "Tutkuyla yaşar", "Hayalci vizyoner", "Sınırsız merak", "Oyuncu ve genç ruh", "Yaratıcı asi", "Duygusal dönüşüm ustası", "Özgürlük sever", "Gerçek olana bağlı", "Ezilenin savunucusu", "Hızla uyum sağlar", "Cezbedici energy", "Yıkılmaz iyimser", "Yargılamaz", "Derin iletişim kurar", "Ruhsal gezgin"]},
        "ENFJ": {"unvan": "Önder", "ozet": "Başkalarıyla bağlantı kurmaya öncelik veren ve insan odaklı olan 'Protagonist'lerdir. İnsanlığın genel acılarına özellikle güçlü bir empati duygusu taşırlar. ENFJ'ler kendine güvenen ve enerjik bireylerdir ve hedeflere yaklaşımlarında genellikle yapılandırılmış bir yöntem izlerler. İnsan ilişkilerini içeren kariyerlerde genellikle başarılı olurlar. ENFJ'ler yakın ve samimi ilişkilere değer verirler ve sadakatleri ve güvenilirlikleriyle tanınırlar. Kendi ihtiyaçlarını, daha büyük bir gruba yardım etme istekleriyle dengelemekte zorluk yaşayabilirler.",
                 "maddeler": ["Ruhsal bağ kurar", "Empatik vizyoner", "Duygusal zekası yüksek", "Potansiyeli görür, gelişimi destekler", "Mantık ve duyguyu dengeler", "Geleceğe göre karar verir", "Amaca hizmet eder", "Cesur ve gerçek bir kalp", "Sarsılmaz sadakat", "Ruhları besler", "Kırılmaz direnç", "İnsanları güçlendirir", "Derin ve huzurlu bir sevgi", "Hızlı gelişim", "Sakin dışa dönük"]},
        "INTP": {"unvan": "Mantıkçı", "ozet": "Bilgi ve anlayışa öncelik veren mantıklı ve analitik 'Mantıkçı'lardır. Bir sistemin veya fikrin temel prensiplerine ulaşmak için yüzeysel ayrıntıları soyutlama konusundaki ilgileriyle tanınırlar. Yüksek zekâya sahip ve öznel anlayışlarını tutarlı sistemlere geliştirme ve düzenleme konusunda keyif alan eğitimciler olarak görülebilirler. Esnek ve hoşgörülüdürler, ancak inançları sorgulandığında katılaşabilirler.",
                 "maddeler": ["Teori ustası", "Evren meraklısı", "Gerçekğin peşinde", "Hayat boyu öğrenci", "Duygusal olarak mesafeli ama derin", "Kalıpları kolayca görür", "Duygularını gizler ama derindir", "Az ama öz sosyallik", "Bağımsız zihin", "Analizi eğlenceli hale getirir", "Çok alanlı bilgi", "Gizli dahi", "Şüpheci kafa", "Farklı çözümler üretir", "Sakin ve rahat", "Kurallara uymaz"]},
        "INTJ": {"unvan": "Mimar", "ozet": "Zekâ, ilgi ve yetkinliğe değer veren mantıklı 'Mimar'lardır. Yeni karmaşık fikirleri ve kavramları anlamak ve onları pratik olarak uygulamak için etkili stratejiler geliştirmek için kendilerini motive ederler. INTJ'ler genellikle vizyoner olarak nitelendirilir, geleceğin olanaklarına odaklanır ve fikirlerinde büyük sıçramalar yaparlar. Bağımsız, kararlı, kendine güvenen ve hırslı olarak sıklıkla tanımlanırlar ve genellikle stratejik planlama, mühendislik, bilim veya işle ilgili kariyerlerde başarılı olurlar.",
                 "maddeler": ["Zihin ustası", "Geleceğin mimarı", "Bağımsızlığına düşkün", "Kararlı ve stratejik", "Keskin mantıklı", "Verimlilik takıntılı", "Doğası gereği gizli", "Ustalığın peşinde", "10 adım ilerisini görür", "Baskıda güçlenir", "İçten içe romantik", "Sessiz ama durdurulamaz", "Mükemmeliyetçi kafa", "Sohbeti sevmez, derin konuları sever", "Sadık ama seçici", "Kedi insanı"]},
        "ENTP": {"unvan": "Tartışmacı", "ozet": "Meraklı, araştırmacı ve hızlı düşünen 'Tartışmacılar' olarak bilinirler ve sorunlara yeni olasılıklar ve çözümler bulma konusunda yeteneklidirler. Esnek, uyum sağlayabilen, ilgilendikleri birçok konuda yetenekli ve fikirlerini tartışma konusundaki coşku ve yetenekleriyle tanınırlar. ENTP'ler genellikle hayata çok yönlü bir yaklaşım sergilerler ve bir perspektifte uzmanlaşmak yerine bir fikrin tüm yönlerini keşfetmekle ilgilenirler. Doğal liderlerdir ognellikle iş dünyasında veya girişimcilikte başarılı olurlar.",
                 "maddeler": ["Yaratıcı kaos", "Jet hızında konuşur", "Düşünmeden önce konuşur", "Tartışma ustası", "Keskin zekâ", "Kural bozan", "Doğaçlama ustası", "İkna kabiliyeti yüksek", "Espiriyi silah gibi kullanır", "Kuralları test eder", "Sınırları zorlar", "Zihinsel kışkırtıcı", "Mantıkla kıvrak", "Her işten anlar", "Sürekli yeni fikir üretir", "Sonsuz meraklı"]},
        "ENTJ": {"unvan": "Buyurucu", "ozet": "Mantıklı, analitik ve kendine güvenen 'Buyurucu' olarak bilinirler ve başarıya olan güçlü bir arzuyla liderlik yapmak istemektedirler. Özellikle kurumsal ortamlarda, sorunları tespit etme ve çözme konusunda mükemmeldirler ve dışarıdan gelen, objektif bilgilere dayanarak hızlı ve kararlı kararlar alabilirler. İnsanlarla etkileşimde bulunmaktan ve onları ortak bir hedefe yönlendirmekten keyif alırlar. Verimsizlik ve hatalara karşı sabırsız olabilirler, ancak duygusal yönleri de güçlü olabilir.",
                 "maddeler": ["İşi halleder", "Çalışkan ve azimli", "Geniş düşünen", "Korkusuz problem çözücü", "Verimlilik delisi", "Girişimci ruh", "Hedef odaklı", "Kendini sürekli geliştirir", "Büyütme kafasında", "Sistem kurucu", "Hem çalışır hem eğlenir", "Seçici ama sosyaldir", "Zorluğu sever", "Direkt ve cesur", "Bağımsız dışa dönük", "Büyük düşünür, daha da büyüğünü kurar"]},
        "ISFP": {"unvan": "Maceracı", "ozet": "Bağımsız ve yaratıcı olan, içsel duyguları ve değerleriyle uyum içinde olan 'Macera Arayan' bireylerdir. Bilgiyi beş duyusu aracılığıyla elde etmeyi tercih ederler ve estetiğe ve güzelliğe duyarlıdırlar. Genellikle sessiz ve içine kapanık olurlar, kişisel alanı önemserler. İnceleyici ve düşünceli olup, eylemleri veya yaratımlarıyla olumlu bir etki yapabilirler. Mükemmeliyetçi olabilirler ve güçlü yönlerini yeterince takdir etmeyebilirler.",
                 "maddeler": ["Estetik ruh", "Sessiz gözlemci", "Olduğu gibi, sahici", "Duyusal zekâ", "Sözcüksüz hikâyeci", "Duygularla sanat yapar", "Yumuşak ama sarsılmaz", "Bağımsız gezgin", "Şefkatli eylem insanı", "Derin ve sessiz sevgi", "Öngörülemez özgür ruh", "Anlık yaratıcı", "Nazik ama güçlü", "Duygusal ve fiziksel akışkanlık", "Ana akıma ters birey", "Doğuştan cool tarz"]},
        "ISTP": {"unvan": "Becerikli", "ozet": "Mantıklı ve pratik olan 'Virtüözler' olarak bilinen kişilerdir. Mantık ve rasyonel düşünceye odaklanırken, aynı zamanda somut, pratik maceralara da büyük bir ilgi duyarlar. ISTP'ler inançlarına sadıktırlar ve güçlü kişisel değerlerine sahiptirler. Kriz durumlarında etkili olan bir eylem odaklıdırlar. İyimser ve neşeli olmalarıyla tanınırlar ve sadakatleriyle bilinirler. ISTP'ler, mantıksal analiz ve teknik becerilerini kullanmalarına ve kararlar almalarına özgürlük tanıyan kariyerlerde daha iyi başarılı olurlar.",
                 "maddeler": ["El ustası", "Baskıda bile soğukkanlı", "Tam bir gerçekçi", "Dünyayı tamir edenler", "Derin ve sessiz bir zihin", "Mekanik deha", "Dram yok, aksiyon var", "Aşırı mantıklı ve mesafeli", "Risk sever ama hesaplı", "Mesafeli ama sadık", "Soğukkanlı", "Yalnız kurt enerjisi", "Refleksleri hızlı, bedensel çevik", "Aşırı kendi kendine yeter", "Dokunsal ve duyusal hassasiyet", "Her şeyde minimalist"]},
        "ESFP": {"unvan": "Eğlendirici", "ozet": "Tutkuyla yaşamaktan ve özgür ruhlu 'Eğlendiriciler'dir; canlılıkları, pozitiflikleri ve enerjileri ile tanınırlar. Şimdiki anı yaşamaktan hoşlanırlar, estetik duyguları güçlüdür ve etraflarındaki nesnelerle doğrudan, fotoğrafsal bir ilişkiye sahiptirler. Genellikle pratik ognellikespontane olurlar ve teorik öğrenmeden çok uygulamalı öğrenmeyi tercih ederler. ESFP'ler aynı zamanda iyi takım oyuncularıdır ve sıcak, cömert ve diğer insanları kabul eden kişilerdir. Yeni durumlara iyi uyum sağlarlar ve insanların duyularını uyarma konusunda başarılıdırlar.",
                 "maddeler": ["Anlık karizma", "Bulaşıcı enerji", "Trend başlatan", "Anı dolu dolu yaşar", "Zor koşullara hızlı uyum", "Korkusuz kaşif", "Aksiyonla karar verir", "Sosyal akışta rahat", "Deneyim zekâsı", "Duygularını gösterir", "İçgüdüsel çözüm bulur", "Eşsiz duyusal farkındalık", "Derin koruyucu empati", "Oyuncu mizah", "Doğal moral kaynağı", "Maceracı ruh"]},
        "ESTP": {"unvan": "Girişimci", "ozet": "Adaptif, kaynaklı ve aksiyon odaklı olan 'Girişimciler'dir ve uzun vadeli bir planın gelişmesini beklemek yerine enerjilerini mevcut eyleme yönlendirme eğilimindedir. ESTP kişiliğinin temel yönü, deneyim için fethetme veya mücadele etme isteğidir. İnsanların tutumlarını ve motivasyonlarını algılamada iyidirler ve hızlı karar vericilerdir. Enerjiktirler, anın tadını çıkarırlar ve improvize etme ve yenilik yapma konusunda yeteneklidirler. Harika girişimciler, motive ediciler ve satış elemanları olabilirler.",
                 "maddeler": ["Korkusuz öncü", "Harekete geçer", "Anı ustalıkla yaşar", "Sokak zekâsı", "Gerçeğe odaklı çözümcü", "Hayatta kalmanın simgesi", "Baskıda bile serin", "Keskin iletişimci", "İyi riski sever", "Spontane ve esnek", "Fırsatı kaçırmaz", "Keskin gözlemci", "Yeniliklere açık", "Bağımsızlığına düşkün", "Eleştiriye takılmaz", "YOLO zihniyeti"]},
        "ISFJ": {"unvan": "Savunmacı", "ozet": "Uyum ve işbirliğine değer veren düşünceli ve güvenilir 'Savunmacılar'dır. Diğerlerinin duygularına duyarlıdırlar ve insanlardaki en iyi yönleri ortaya çıkarmaya çalışırlar. Zengin bir iç dünyaya ve önemli bilgilere güçlü bir hafızaya sahiptirler ve güvenlik, nezaket, gelenekler ve yasalara değer verirler. ISFJ'ler, teorik öğrenim yerine pratik uygulamayı tercih ederler ve mekan, fonksiyon ve estetik duygusu gerektiren görevlerde başarılı olurlar. Başkalarına yardım etme, destekleme ve düzenleme gibi rollerde üstün performans gösterirler.",
                 "maddeler": ["Güvenilir ve sadık", "Doğuştan koruyucu", "Altın kalp, çelik sınırlar", "Yumuşak ama yıkılmaz", "Geleneklere sahip çıkar", "Detaylara dikkat eder", "Adanmış ve çalışkan", "Uyum arar", "Pratik sevginin ustası", "İçten ve minnettar", "Anıların koruyucusu", "Alçakgönüllü ve zarif", "Aziz sabrı", "Sessiz güç", "Sarsılmaz sadakat", "Görünmeyen omurga"]},
        "ISTJ": {"unvan": "Lojistikçi", "ozet": "Mantıklı ve güvenilir 'Lojistikçiler'dir ve dürüstlük, bütünlük ve güvenlik değerlerine önem verirler. Aynı zamanda titiz ve görevine düşkün olmaları, detaylara dikkatli ve sabırlı olmalarıyla da bilinirler. Gerçekleri önemserler ve kendileri için önemli olan detayları güçlü bir hafızaya sahiptirler. ISTJ'ler odaklanmış ve ciddi olma eğilimindedir, ancak aynı zamanda harika bir mizah anlayışına sahiptirler. Yakınlarının duygusal ihtiyaçlarını fark ettiklerinde, destekleyici ve özenli olurlar. Detaylara büyük bir dikkatle bağımsız çalışmayı tercih ederler.",
                 "maddeler": ["Sarsılmaz dürüstlük", "Dengenin koruyucusu", "Doğal adaletli ognellike objektif", "Çalışkan ve titiz", "Kendine hâkim ve sakin", "B planı ustası", "Yürüyen ansiklopedi", "Detay avcısı", "Planlı ve düzenli", "Bağımsız ve kendi kendine yeter", "Doğuştan risk analizi", "Koruyucu ve sadık", "Kuru mizah, ince espri", "Gerçek ve mantığa odaklı", "Pratik ve mantıklı düşünen", "Lojistik ustası"]},
        "ESFJ": {"unvan": "Konsül", "ozet": "Nezaket sahibi, pratik ognellikişbirlikçi kişilerdir. İnsan odaklıdırlar ve güvenlik ve istikrarı değer verirler. Doğal olarak, başkalarının kendilerini duyulmiş ve önemsenmiş hissetmelerini sağlarlar çünkü başkalarını gerçekten anlamak istemektedirler. ESFJ'ler sorumluluk sahibi ve güvenilirdir. Detaylarda ne yapılması gerektiğini görebilme becerilerine sahiptirler. Sosyal gruplarının normlarına ve beklentilerine uyum sağlamada iyidirler. ESFJ'ler, ortak ilgi alanlarını vurgulayarak ve birlik duygusu yaratarak insanları bir araya getirme ve işbirliğini teşvik etme yeteneğine sahiptirler.",
                 "maddeler": ["Kalpten lider", "Sosyal uyumun ustası", "Gerçek bir fedakâr", "Grubun kalbi", "Güvenilir ve destekleyici", "Sarsılmaz sadakat", "İnsanlara kolay uyum sağlar", "Duygularını ifade eder", "Doğuştan uzlaştırıcı", "Duyguları kolay okur", "Sonsuz iyimser", "Yüksek çalışma disiplini", "Krizde dengeyi sağlar", "Kişiye özel ilgi", "İlişkileri sürdürebilir", "Geleneklerin koruyucusu"]},
        "ESTJ": {"unvan": "Yönetici", "ozet": "Sistemler ve planlar oluşturma konusunda başarılı olan, sorumluluk sahibi ve mantıklı 'Yöneticiler'dir. Yetenek ve verimlilik değerlerine önem verirler ve güçlü bir sorumluluk duygusu ve hesap verme beklentisi içindedirler. ESTJ'ler dürüst ve açıktır. Güvenlik ve sosyal düzene değer verirler ve bu hedefleri teşvik etmek için çalışmaktan çekinmezler. ESTJ'ler, pratik kapsamının dışındaki hedeflerin değerini görmekte zorluk yaşayabilirler, ancak bu hedeflerin önemini anladıklarında anlama ve benimseme yolunda çalışacaklardır.",
                 "maddeler": ["İcra ustası", "Liderliği içgüdüsel alır", "Sorumluluğa bağlı", "Düzen sever ve planlı", "Azimli ve çalışkan", "Gerçeğe ve mantığa odaklı", "Pratik ve rasyonel", "Krizde denge kurar", "Verimlilik uzmanı", "Kararlarını güvenle alır", "Kuralları ve adaleti sever", "Çoklu görevi iyi yönetir", "Güçlü bir omurga", "Zorlukta sağlam durur", "Beklenmedik şekilde komik", "Hedefinden şaşmaz"]}
    }

    profil_veri = mbti_sozluk.get(mbti_kodu, mbti_sozluk["INTJ"])

    # --- 🛠️ SIDEBAR İÇİN ORANTILI VE DENGELİ SON SÜRÜM ---
    st.sidebar.markdown(f"""
    <style>
        [data-testid="stSidebarContent"] {{
            padding-top: 15px !important;
            padding-bottom: 15px !important;
            overflow-y: hidden !important;
        }}
        
        .sidebar-profile-box {{
            text-align: center;
            margin-top: 0px !important;
            margin-bottom: 10px !important;
        }}
        
        .avatar-circle {{
            background: linear-gradient(135deg, #2E5B88, #4A7BB0);
            width: 50px; height: 50px;
            border-radius: 50%; margin: 0 auto 6px auto;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 18px; color: white;
        }}
        .profile-title {{
            margin: 0 !important; font-size: 15px !important; color: #0F0F1A;
            font-weight: 600;
            line-height: 1.1;
        }}
        .profile-badge {{
            background: rgba(46, 91, 136, 0.1); color: #2E5B88;
            padding: 2px 10px; border-radius: 20px;
            font-size: 11px; font-weight: bold; display: inline-block; margin-top: 4px;
        }}
        
        .profile-desc {{
            color: #4B5563; font-size: 11.5px !important; line-height: 1.4;
            text-align: justify; margin: 10px 0 !important;
        }}
        
        .features-grid {{
            display: flex; flex-wrap: wrap; gap: 6px 6px;
            margin-bottom: 12px; padding: 0 2px;
        }}
        .feature-item {{
            flex: 1 1 45%;
            font-size: 11.5px !important; color: #1F2937;
            text-align: left;
            white-space: normal !important;
            line-height: 1.2;
        }}
        
        .sidebar-divider {{
            margin: 10px 0 !important;
            border: 0;
            border-top: 1px solid #E5E7EB;
        }}
        .nav-links-box {{
            text-align: center; margin-top: 2px; margin-bottom: 6px; font-size: 11px; color: #9CA3AF;
        }}
        
        .mini-link-btn {{
            display: block !important;
            width: 100% !important;
            height: 26px !important;
            line-height: 26px !important;
            text-align: center !important;
            font-size: 11.5px !important;
            font-weight: 500 !important;
            border-radius: 5px !important;
            margin-bottom: 8px !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
            box-sizing: border-box !important;
        }}
        
        .btn-mini-gray {{
            background-color: #F3F4F6 !important;
            color: #4B5563 !important;
            border: 1px solid #D1D5DB !important;
        }}
        .btn-mini-gray:hover {{
            background-color: #E5E7EB !important;
        }}
        
        .btn-mini-blue {{
            background: #2E5B88 !important;
            color: white !important;
            border: none !important;
        }}
        .btn-mini-blue:hover {{
            background: #1A3D63 !important;
        }}
    </style>

    <div class="sidebar-wrapper">
        <div class="sidebar-profile-box">
            <div class="avatar-circle">{st.session_state.username[0].upper()}</div>
            <h3 class="profile-title">{st.session_state.username}</h3>
            <span class="profile-badge">🚀 {mbti_kodu} - {profil_veri['unvan']}</span>
            <p class="profile-desc">{profil_veri['ozet']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Özellik maddelerini basan döngü alanı
    madde_html = '<div class="features-grid">'
    for m in profil_veri["maddeler"]:
        madde_html += f'<div class="feature-item">🌿 {m}</div>'
    madde_html += '</div>'
    st.sidebar.markdown(madde_html, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.sidebar.markdown('<div class="nav-links-box">⚙️ Kişilik Testini Tekrar Çöz</div>', unsafe_allow_html=True)

    st.sidebar.markdown("""
        <a href="/?aksiyon=teste_don" target="_self" class="mini-link-btn btn-mini-gray">Test Ekranına Dön</a>
        <a href="/?aksiyon=cikis" target="_self" class="mini-link-btn btn-mini-blue">Oturumu Kapat</a>
    """, unsafe_allow_html=True)

    parametreler = st.query_params
    if "aksiyon" in parametreler:
        secilen_aksiyon = parametreler["aksiyon"]
        st.query_params.clear()
        
        if secilen_aksiyon == "teste_don":
            st.session_state.sayfa = "Test"
            st.rerun()
        elif secilen_aksiyon == "cikis":
            st.session_state.sayfa = "Giris"
            st.rerun()

    # --- SİNEMA PLATFORMU ANA İÇERİK ALANI ---
    st.markdown(f"""
    <div class="custom-navbar">
        <h2 style="margin:0; color:#0F0F1A; font-size:22px;">🍿 Kişiliğine Göre Süzülen Sinema Evreni</h2>
        <span style="background:#F3F4F6; color:#374151; padding:6px 16px; border-radius:10px; font-size:13px; border: 1px solid #E5E7EB; font-weight:600;">
            IMDb Sıralı Katalog
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    if "aktif_film" not in st.session_state:
        st.session_state.aktif_film = None
    if "aktif_poster" not in st.session_state:
        st.session_state.aktif_poster = None

    # --- POPUP (EKRAN KARTI) İÇİ TASARIMI YENİDEN YAZIYORUZ ---
    @st.dialog("🎬 Film Detayları", width="large") # width="large" ile popup'ı büyüttük
    def film_detay_popup():
        f_data = st.session_state.aktif_film
        poster_url = st.session_state.aktif_poster # Tıklanan filmin görselini aldık
        
        if f_data:
            odul_badge = ""
            if "Evet" in str(f_data.get('is_awarded', '')) or "🏆" in str(f_data.get('is_awarded', '')):
                odul_badge = "<span class='pop-badge pop-badge-awarded-gold'>🏆 Ödüllü Sürüm</span>"
            
            ingilizce_ozet = f_data.get('overview', '')
            if ingilizce_ozet and str(ingilizce_ozet).strip() != "":
                try:
                    turkce_ozet = GoogleTranslator(source='auto', target='tr').translate(ingilizce_ozet)
                except Exception:
                    turkce_ozet = f"(Çeviri yapılamadı) {ingilizce_ozet}"
            else:
                turkce_ozet = "Bu film için özet metni veri tabanında bulunmamaktadır."

            # Görsel ve Yazıları yan yana koymak için Streamlit Columns kullanıyoruz
            col_img, col_info = st.columns([1, 2]) # 1 birim genişlik görsele, 2 birim yazılara
            
            with col_img:
                # EKRAN KARTINDAKİ (POPUP) GÖRSEL
                st.image(poster_url, use_container_width=True)
                
            with col_info:
                st.markdown(f"""
                <h2 style='margin-top:0;'>{f_data.get('title', 'Bilinmeyen')}</h2>
                <div class="pop-meta-row">
                    <span class="pop-badge">📅 Yıl: {f_data.get('year', 'Belirtilmemiş')}</span>
                    <span class="pop-badge">⏳ Süre: {f_data.get('runtime', '100')} dk</span>
                    <span class="pop-badge">⭐ Puan: {f_data.get('vote_average', 'N/A')}</span>
                    {odul_badge}
                </div>
                <p style="color: #FF3366; font-size: 15px; font-weight: 600;">🎭 {f_data.get('genres_clean', 'Belirtilmemiş')}</p>
                
                <div class="pop-overview">
                    <h5 style="margin-top:0; margin-bottom:8px; color:#0F0F1A; font-weight:700; border-bottom:2px solid #E5E7EB; padding-bottom:6px;">📝 ÖZET</h5>
                    <p style="margin:0; text-align:justify; color:#4B5563; font-size:14px; line-height:1.6;">
                        {turkce_ozet}
                    </p>
                </div>
                """, unsafe_allow_html=True)
# --- 🚀 YENİ EKLENEN AKILLI VE OTOMATİK OYNATILAN YOUTUBE BUTONU ---
              
                st.markdown("<br>", unsafe_allow_html=True) # Araya şık bir boşluk
                
                film_adi = f_data.get('title', 'Bilinmeyen')
                film_id = f_data.get('id', None)
                
                # Arka plandaki zeki fonksiyonumuz sırayla (Altyazı > Dublaj > Orijinal) arayacak
                fragman_key = fragman_getir(film_adi, film_id)
                
                if fragman_key:
                    # Direkt izleme linki
                    youtube_linki = f"https://www.youtube.com/watch?v={fragman_key}&autoplay=1"
                else:
                    # Çok ekstrem bir durumda video hiç yoksa yedek plan: Arama Sayfası
                    arama_metni = f"{film_adi} Türkçe fragman".replace(" ", "+")
                    youtube_linki = f"https://www.youtube.com/results?search_query={arama_metni}"
                
                # Sahnede tek yıldız: Kırmızı, tam genişlikte buton (Sadece "Fragman İzle" yazıyor)
                st.link_button("▶️ Fragman İzle", youtube_linki, type="primary", use_container_width=True)

    # --- ANA SAYFADAKİ KARTLARIN OLUŞTURULDUĞU DÖNGÜ ---
    kategoriler = u.get("kategoriler", {})
    
    if "HATA" in kategoriler:
        st.error(kategoriler["HATA"][0]["title"])
    elif not kategoriler:
        st.warning("Filtre matrisine uygun film grubu oluşturulamadı.")
    else:
        for kat_adi, film_listesi in kategoriler.items():
            st.markdown(f"<h3 class='category-header'>🎬 {kat_adi} (En Yüksek IMDb Sıralaması)</h3>", unsafe_allow_html=True)
            
            cols = st.columns(4) # Yan yana 4 film
            for idx, film in enumerate(film_listesi):
                with cols[idx % 4]:
                    # 1. ADIMDA YAZDIĞIMIZ FONKSİYON İLE AFİŞİ ÇEKİYORUZ
                    poster = afis_getir(film['title'], film.get('id'))
                    
                    # ANA SAYFA FİLM GÖRSELİ GÖSTERİMİ
                    st.image(poster, use_container_width=True)
                    
                    tur_kisaltma = film['genres_clean'][:30] + "..." if len(film['genres_clean']) > 30 else film['genres_clean']
                    
                    # GÖRSELİN ALTINDA YAZACAK BİLGİLER
                    st.markdown(f"""
                    <div style='padding: 5px 0 10px 0;'>
                        <strong style='font-size: 16px; color:#0F0F1A;'>{film['title']}</strong><br>
                        <span style='font-size: 13px; color:#6B7280;'>🎭 {tur_kisaltma}</span><br>
                        <span style='font-size: 13px; font-weight:bold; color:#FF9900;'>⭐ {film['vote_average']} | #{idx+1}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # BUTON TASARIMI ARTIK SADECE "DETAYLARI GÖR" BUTONU OLDU
                    # BUTON TASARIMI YAZI KADAR GENİŞ OLACAK
                    # BUTON TASARIMINDA use_container_width=True KISMINI EKLİYORUZ
                    if st.button("Detayları Gör", key=f"btn_{kat_adi}_{idx}", use_container_width=True):
                        st.session_state.aktif_film = film
                        st.session_state.aktif_poster = poster
                        film_detay_popup()
                    
                    st.markdown("<br>", unsafe_allow_html=True) # Kartlar arası boşluk