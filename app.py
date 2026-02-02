import streamlit as st
from rembg import remove
from PIL import Image
import io
import os
import cv2
import numpy as np

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="wide")

st.title("📸 Profesyonel Arka Plan Temizleyici")

# --- Ayarlar Bölümü (Sidebar) ---
st.sidebar.header("⚙️ Ayarlar")

# Boyut Ayarları
st.sidebar.subheader("📐 Boyutlandırma")
target_width = st.sidebar.number_input("Genişlik (px)", min_value=100, max_value=4000, value=600, step=50)
target_height = st.sidebar.number_input("Yükseklik (px)", min_value=100, max_value=4000, value=800, step=50)

st.sidebar.divider()

# Gelişmiş Ayarlar
st.sidebar.subheader("🧠 Akıllı Temizlik")
use_smart_clean = st.sidebar.checkbox("Otomatik Parçacık Temizleyici", value=True, help="Ana nesne dışındaki küçük logoları ve lekeleri otomatik siler.")
smart_clean_threshold = 0.05 # %5'ten küçük parçaları sil

st.sidebar.divider()

st.sidebar.subheader("🧪 Detay Ayarları")
use_alpha_matting = st.sidebar.checkbox("Hassas Kenar (Alpha Matting)", value=False, help="Kenarları daha yumuşak siler.")
alpha_matting_erode = 10
if use_alpha_matting:
    alpha_matting_erode = st.sidebar.slider("Kenar Aşındırma", 0, 40, 10)

st.write(f"Resminizi yükleyin, arka planı silinsin ve **{target_width}x{target_height}** beyaz şablona oturtulsun.")

# Önbellekleme (Cache) - Parametre değiştikçe yeniden çalışır
@st.cache_data
def process_image(image_bytes, width, height, _use_smart, _smart_thresh, _use_alpha, _erode_size):
    # Byte -> PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Arka planı kaldır (rembg)
    if _use_alpha:
        output_image = remove(image, alpha_matting=True, alpha_matting_erode_size=_erode_size)
    else:
        output_image = remove(image)
        
    # 2. Akıllı Temizlik (OpenCV ile küçük parçaları silme)
    if _use_smart:
        # PIL -> Numpy (RGBA)
        img_np = np.array(output_image)
        
        # Sadece Alpha kanalını al (Şeffaflık maskesi)
        alpha_channel = img_np[:, :, 3]
        
        # Konturları bul (Dış hatlar)
        contours, _ = cv2.findContours(alpha_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # En büyük nesneyi bul (Ana ürün)
            # key=cv2.contourArea hatası almamak için lambda kullanıyoruz
            largest_contour = max(contours, key=cv2.contourArea)
            max_area = cv2.contourArea(largest_contour)
            
            # Yeni bir temiz maske oluştur (Simsiyah)
            clean_mask = np.zeros_like(alpha_channel)
            
            # Yeterince büyük olan tüm parçaları maskeye ekle
            for cnt in contours:
                if cv2.contourArea(cnt) > (max_area * _smart_thresh):
                    cv2.drawContours(clean_mask, [cnt], -1, 255, thickness=cv2.FILLED)
            
            # Orijinal alpha ile temiz maskeyi birleştir
            # Maskenin olmadığı yerleri sil (Alpha'yı 0 yap)
            img_np[:, :, 3] = cv2.bitwise_and(alpha_channel, clean_mask)
            
            # Tekrar PIL formatına çevir
            output_image = Image.fromarray(img_np)

    # 3. Yeni beyaz bir tuval oluştur
    target_size = (width, height)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 4. Resmi boyutlandır
    img_copy = output_image.copy()
    img_copy.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # 5. Resmi merkeze yerleştir
    img_w, img_h = img_copy.size
    offset_x = (target_size[0] - img_w) // 2
    offset_y = (target_size[1] - img_h) // 2
    
    canvas.paste(img_copy, (offset_x, offset_y), img_copy)
    
    return canvas

# Dosya Yükleme Alanı
uploaded_files = st.file_uploader("Resimleri Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    # Tüm sonuçları burada toplayacağız
    processed_results = []
    
    # 1. Döngü: Tüm resimleri işle ve ekranda göster
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # Dosyayı byte olarak oku
            img_bytes = uploaded_file.getvalue()
            
            # Görüntüleme için görseli aç
            input_image = Image.open(io.BytesIO(img_bytes))
            
            # İşle
            with st.spinner(f'{uploaded_file.name} işleniyor...'):
                final_image = process_image(img_bytes, target_width, target_height, use_smart_clean, smart_clean_threshold, use_alpha_matting, alpha_matting_erode)
            
            # Sonuçları listeye ekle (Daha sonra sidebar için kullanacağız)
            processed_results.append({
                "file": uploaded_file,
                "input_image": input_image,
                "final_image": final_image,
                "index": i
            })
            
            # Yan yana göster
            col1, col2 = st.columns(2)
            with col1:
                st.image(input_image, caption=f'Orijinal ({uploaded_file.name})', use_container_width=True)
            with col2:
                st.image(final_image, caption=f'Sonuç ({target_width}x{target_height})', use_container_width=True)
            
            st.divider()
            
        except Exception as e:
            st.error(f"{uploaded_file.name} dosyasında hata: {e}")

    # 2. Sidebar: Seçilen dosya için sabit kontrol paneli
    if processed_results:
        with st.sidebar:
            st.divider()
            st.header("💾 İndirme Paneli")
            
            # Seçim Kutusu (Hangi dosyayı indireceğiz?)
            # Dosya isimlerinden bir liste oluşturuyoruz
            file_options = {item["file"].name: item for item in processed_results}
            selected_filename = st.selectbox("İşlem Yapılacak Dosyayı Seçin:", list(file_options.keys()))
            
            # Seçilen dosyanın verilerini al
            selected_item = file_options[selected_filename]
            active_file = selected_item["file"]
            active_final_image = selected_item["final_image"]
            active_index = selected_item["index"]
            
            # İndirme için hazırla
            buf = io.BytesIO()
            active_final_image.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            # Varsayılan dosya adı
            default_name = os.path.splitext(active_file.name)[0] + "_temiz"
            
            st.info("İsmi değiştirdikten sonra **ENTER** tuşuna basınız.")
            
            # İsim Değiştirme
            custom_name = st.text_input(
                "Dosya Adı:", 
                value=default_name, 
                key=f"rename_{active_index}"
            )
            
            # Uzantı kontrolü
            if not custom_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                save_name = custom_name + ".jpg"
            else:
                save_name = custom_name
            
            # İndirme Butonu
            st.download_button(
                label=f"💾 İndir ({save_name})",
                data=byte_im,
                file_name=save_name,
                mime="image/jpeg",
                key=f"btn_download_{active_index}",
                use_container_width=True
            )
            
            st.success(f"{active_file.name} seçili.")
