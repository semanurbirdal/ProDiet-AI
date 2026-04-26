import streamlit as st
import random
from supabase import create_client

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="ProDiet AI | Energetic Dashboard", layout="wide")

# --- 2. SUPABASE BAĞLANTISI ---
# Bilgilerini doğrudan kodun içine gömdüm, secrets ile uğraşma
URL = "https://iboenhtkltwldqgelrup.supabase.co"
KEY = "sb_publishable_0gbooXme-MWLY0toyU5Z9g_S_X6V1Bz"

try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")

# --- 3. CANLI VE MODERN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    .stApp { 
        background-color: #f0f2f6;
        background-image: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); }
    .main-title {
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 3rem; font-weight: 800; margin-bottom: 2rem;
    }
    .vki-header-box {
        background: #ffffff; padding: 1.5rem; text-align: center;
        border-radius: 24px; margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.5);
    }
    .vki-val { font-size: 95px; font-weight: 800; color: #4f46e5; text-align: center; margin: 5px 0; line-height: 1; }
    .status-btn { text-align: center; padding: 1.2rem; border-radius: 18px; color: white; font-weight: 700; font-size: 1.1rem; }
    .info-card { background: white; padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #f1f5f9; }
    .info-card h4 { margin: 0 0 12px 0; font-weight: 800; color: #1e293b; font-size: 1.1rem; text-transform: uppercase; }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white; border: none; padding: 15px; border-radius: 15px; font-weight: 700; width: 100%; height: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DİYET VERİ HAVUZU ---
meals_db = {
    "Kahvaltı": ["60g Yulaf + 1 Meyve + 10 Badem", "2 Yumurta (Omlet) + 1 Dilim Ekmek + 5 Zeytin", "1 Poşe Yumurta + 1/2 Avokado + 1 Dilim Ekmek"],
    "Öğle": ["180g Tavuk + 5 Kaşık Kinoa + Salata", "6 Mercimek Köftesi + Bol Yeşillik + 1 Ayran", "160g Somon + 8 Kuşkonmaz + Salata"],
    "Ara": ["1 Meyve + 2 Tam Ceviz", "150g Yoğurt + 1 Kaşık Bal", "1 Kare Bitter + Filtre Kahve"],
    "Akşam": ["150g Köfte + 200g Fırın Sebze", "1 Porsiyon Zeytinyağlı Fasulye + 4 Kaşık Bulgur", "180g Balık + Roka Salatası"]
}

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2737/2737035.png", width=60)
    st.title("ProDiet Profil")
    u_name = st.text_input("Ad Soyad", "Değerli Kullanıcı")
    c1, c2 = st.columns(2)
    u_age = c1.number_input("Yaş", 1, 100, 20)
    u_gen = c2.selectbox("Cinsiyet", ["Kadın", "Erkek"])
    u_w = c1.number_input("Kilo (kg)", 30.0, 200.0, 66.0)
    u_h = c2.number_input("Boy (cm)", 100, 250, 170)
    u_act = st.selectbox("Hareketlilik", ["Sedanter", "Hafif Aktif", "Orta Aktif", "Çok Aktif"])
    u_diet = st.selectbox("Beslenme", ["Hepçil", "Vegan", "Vejetaryen", "Ketojenik"])
    u_all = st.multiselect("Alerji", ["Gluten", "Laktoz", "Yok"])
    u_goal = st.selectbox("Ana Hedef", ["Kilo Ver", "Koru", "Kas Kazan"])
    st.markdown("<br>", unsafe_allow_html=True)
    start_btn = st.button("🚀 ANALİZİ BAŞLAT")

# --- 6. MAKRO HESAPLAYICI ---
def calc_macros(w, h, a, g, act, goal):
    bmr = (10*w) + (6.25*h) - (5*a) + (5 if g=="Erkek" else -161)
    m = {"Sedanter": 1.2, "Hafif Aktif": 1.375, "Orta Aktif": 1.55, "Çok Aktif": 1.725}
    tdee = bmr * m[act]
    if goal == "Kilo Ver": cal = tdee - 500
    elif goal == "Kas Kazan": cal = tdee + 300
    else: cal = tdee
    p, f = w * (1.8 if goal=="Kas Kazan" else 1.4), w * 0.8
    c = (cal - (p*4 + f*9)) / 4
    return int(cal), int(p), int(c), int(f)

# --- 7. ANA EKRAN AKIŞI ---
if start_btn:
    # --- VERİTABANI KAYDI ---
    payload = {
        "full_name": u_name, "age": int(u_age), "gender": u_gen,
        "weight": float(u_w), "height": int(u_h), "activity_level": u_act,
        "diet_type": u_diet, "allergies": ", ".join(u_all) if u_all else "Yok",
        "main_goal": u_goal
    }
    try:
        supabase.table("user_profiles").insert(payload).execute()
        st.toast("Verileriniz kaydedildi! ✅")
    except Exception as e:
        st.error(f"Veritabanı Kayıt Hatası: {e}")

    # --- PLAN EKRANI ---
    cal, p, c, f = calc_macros(u_w, u_h, u_age, u_gen, u_act, u_goal)
    st.markdown(f"<h1 class='main-title'>✨ {u_name} Kişisel Planı</h1>", unsafe_allow_html=True)
    
    m_cols = st.columns(4)
    for col, lab, val, clr in zip(m_cols, ["KALORİ", "PROTEİN", "KARB", "YAĞ"], [f"{cal} kcal", f"{p}g", f"{c}g", f"{f}g"], ["#4f46e5", "#ef4444", "#10b981", "#f59e0b"]):
        col.markdown(f'<div style="background:white; padding:20px; border-radius:15px; text-align:center; border-bottom:5px solid {clr};"><b>{lab}</b><br><span style="font-size:1.5rem;">{val}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    ca, cb = st.columns(2)
    for i, day in enumerate(days):
        with (ca if i%2==0 else cb):
            with st.expander(f"📅 {day} Menüsü", expanded=True):
                st.write(f"☀️ **Kahvaltı:** {random.choice(meals_db['Kahvaltı'])}")
                st.write(f"⚖️ **Öğle:** {random.choice(meals_db['Öğle'])}")
                st.write(f"🍎 **Ara:** {random.choice(meals_db['Ara'])}")
                st.write(f"🌙 **Akşam:** {random.choice(meals_db['Akşam'])}")
    st.balloons()
else:
    # --- DASHBOARD (ANA SAYFA) ---
    st.markdown("<h1 class='main-title'>ProDiet AI Dashboard</h1>", unsafe_allow_html=True)
    lc, rc = st.columns([1.5, 1])
    
    with lc:
        st.markdown('<div class="vki-header-box"><h2>Hızlı VKİ Hesaplama</h2></div>', unsafe_allow_html=True)
        bmi = u_w / ((u_h/100)**2)
        st.markdown(f'<div class="vki-val">{bmi:.1f}</div>', unsafe_allow_html=True)
        
        st_t, st_c = ("Normal Kilolu", "#10b981")
        if bmi < 18.5: st_t, st_c = ("Zayıf", "#f59e0b")
        elif 25 <= bmi < 30: st_t, st_c = ("Fazla Kilolu", "#f97316")
        elif bmi >= 30: st_t, st_c = ("Obez", "#ef4444")
        st.markdown(f'<div class="status-btn" style="background-color:{st_c};">Durum: {st_t}</div>', unsafe_allow_html=True)
        
    with rc:
        st.markdown('<div class="info-card" style="border-top: 6px solid #6366f1"><h4>💡 Uzman Görüşü</h4><p>Haftada 30 farklı bitki tüketmek bağırsak sağlığı için altın kuraldır.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-card" style="border-top: 6px solid #4ECDC4"><h4>🥑 Biliyor muydunuz?</h4><p>Brokoli pişirildikten sonra sülforafan aktivitesi artar.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-card" style="border-top: 6px solid #FF6B6B"><h4>✨ Motivasyon</h4><p>Vücudun, zihninin yapabileceğine inandığı her şeyi gerçekleştirir.</p></div>', unsafe_allow_html=True)
