import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="wide")

st.title("📸 Profesyonel Arka Plan Temizleyici v1.7 (GÜNCEL)")

# --- Ayarlar Bölümü (Sidebar) ---
st.sidebar.header("⚙️ Ayarlar")

# Önbellek Temizleme Butonu (Sorun Giderme İçin)
if st.sidebar.button("⚠️ Önbelleği Temizle (Reset)"):
    st.cache_data.clear()
    st.experimental_rerun()

# Boyut Ayarları
st.sidebar.subheader("📐 Boyutlandırma")
st.sidebar.info("Varsayılan: 600x800. Beyaz şablon bu boyutlarda oluşturulur.")
target_width = st.sidebar.number_input("Genişlik (px)", min_value=100, max_value=8000, value=600, step=50)
target_height = st.sidebar.number_input("Yükseklik (px)", min_value=100, max_value=8000, value=800, step=50)

# Sürüm Kontrolü ve Bilgilendirme
st.warning("⚠️ Eğer bu yazıyı görüyorsanız SÜRÜM v1.7 (Çift Çıktı Modu) AKTİFTİR.")
st.write(f"Resminizi yükleyin. Sistem size hem **Beyaz Şablon** hem de **Şeffaf PNG** halini sunacaktır.")

# Önbellekleme (Cache)
# FONKSİYON İSMİ KASTEN DEĞİŞTİRİLDİ (CACHE INVALIDATION İÇİN)
@st.cache_data
def process_both_images_final(image_bytes, width, height):
    # Byte -> PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Arka planı kaldır (rembg) -> Bu bize ŞEFFAF (PNG) verir
    output_image = remove(image)
        
    # --- BEYAZ ŞABLON OLUŞTURMA ---
    # 2. Yeni beyaz bir tuval oluştur
    target_size = (width, height)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 3. Resmi boyutlandır (Hem küçültme hem BÜYÜTME yapar)
    img_w, img_h = output_image.size
    
    # Sıfıra bölme hatası önlemi
    if img_w == 0 or img_h == 0:
        return canvas, output_image
    
    # Ölçekleme oranını hesapla (En boy oranını koru)
    scale = min(width / img_w, height / img_h)
    
    # En az 1 piksel olacak şekilde ayarla
    new_w = max(1, int(img_w * scale))
    new_h = max(1, int(img_h * scale))
    
    # Resmi yeniden boyutlandır (LANCZOS filtresi ile kaliteli)
    if new_w > 0 and new_h > 0:
        img_resized = output_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        img_resized = output_image
    
    # 4. Resmi merkeze yerleştir
    offset_x = (width - new_w) // 2
    offset_y = (height - new_h) // 2
    
    canvas.paste(img_resized, (offset_x, offset_y), img_resized)
    
    # Hem Şablonu (JPG) hem Şeffafı (PNG) döndür
    return canvas, output_image

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Resmi Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=False)

if uploaded_file:
    try:
        # Dosyayı byte olarak oku
        img_bytes = uploaded_file.getvalue()
        
        # İşle
        with st.spinner(f'{uploaded_file.name} işleniyor...'):
            final_white, final_transparent = process_both_images_final(img_bytes, target_width, target_height)
        
        st.success(f"{uploaded_file.name} hazır! İndirmek için sol menüye bakınız. 👈")
        
        # Resimleri Yan Yana Göster (KALDIRILDI - ALT ALTA GÖSTERİLİYOR GARANTİ İÇİN)
        st.divider()
        st.subheader("1. Beyaz Şablonlu Halı (JPG)")
        st.image(final_white, caption=f'Beyaz Şablon ({target_width}x{target_height})', width=500)
        
        st.divider()
        st.subheader("2. Arka Planı Silinmiş Şeffaf Halı (PNG)")
        st.image(final_transparent, caption='Şeffaf / Orijinal (PNG)', width=500)
        
        # İndirme Paneli (Sidebar)
        with st.sidebar:
            st.divider()
            st.header("💾 İndirme Paneli")
            
            st.info("İsmi değiştirdikten sonra **ENTER** tuşuna basınız.")
            
            # Varsayılan dosya adı
            default_name = os.path.splitext(uploaded_file.name)[0]
            
            # İsim Değiştirme
            custom_name = st.text_input(
                "Dosya Adı:", 
                value=default_name
            )
            
            # Uzantısız halini al (temiz isim)
            base_filename = os.path.splitext(custom_name)[0]
            
            st.divider()
            
            # --- BUTON 1: BEYAZ ŞABLON İNDİR ---
            buf_jpg = io.BytesIO()
            final_white.save(buf_jpg, format="JPEG", quality=95)
            byte_jpg = buf_jpg.getvalue()
            name_jpg = base_filename + "_sablon.jpg"
            
            st.download_button(
                label=f"💾 İndir: Beyaz Şablon (JPG)",
                data=byte_jpg,
                file_name=name_jpg,
                mime="image/jpeg",
                use_container_width=True
            )
            
            # --- BUTON 2: ŞEFFAF PNG İNDİR ---
            buf_png = io.BytesIO()
            final_transparent.save(buf_png, format="PNG")
            byte_png = buf_png.getvalue()
            name_png = base_filename + "_seffaf.png"
            
            st.download_button(
                label=f"💾 İndir: Şeffaf (PNG)",
                data=byte_png,
                file_name=name_png,
                mime="image/png",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
