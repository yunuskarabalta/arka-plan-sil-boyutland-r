import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="wide")

st.title("📸 Profesyonel Arka Plan Temizleyici")

# --- Ayarlar Bölümü (Sidebar) ---
st.sidebar.header("⚙️ Ayarlar")

# Boyut Ayarları
st.sidebar.subheader("📐 Boyutlandırma")
st.sidebar.info("Varsayılan: 600x800. Büyük değer girerseniz resim ona göre genişletilir.")
target_width = st.sidebar.number_input("Genişlik (px)", min_value=100, max_value=8000, value=600, step=50)
target_height = st.sidebar.number_input("Yükseklik (px)", min_value=100, max_value=8000, value=800, step=50)

st.write(f"Resminizi yükleyin, arka planı silinsin ve **{target_width}x{target_height}** beyaz şablona oturtulsun.")

# Önbellekleme (Cache) - Parametre değiştikçe yeniden çalışır
@st.cache_data
def process_image(image_bytes, width, height):
    # Byte -> PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Arka planı kaldır (rembg)
    output_image = remove(image)
        
    # 2. Yeni beyaz bir tuval oluştur
    target_size = (width, height)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 3. Resmi boyutlandır (Hem küçültme hem BÜYÜTME yapar)
    # Thumbnail metodu resmi büyütmez, o yüzden resize kullanacağız.
    img_w, img_h = output_image.size
    
    # Ölçekleme oranını hesapla (En boy oranını koru)
    # Hedef kutunun içine sığacak en büyük boyutu bul
    scale = min(width / img_w, height / img_h)
    
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    
    # Resmi yeniden boyutlandır (LANCZOS filtresi ile kaliteli)
    img_resized = output_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 4. Resmi merkeze yerleştir
    offset_x = (width - new_w) // 2
    offset_y = (height - new_h) // 2
    
    canvas.paste(img_resized, (offset_x, offset_y), img_resized)
    
    return canvas

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Resmi Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=False)

if uploaded_file:
    try:
        # Dosyayı byte olarak oku
        img_bytes = uploaded_file.getvalue()
        
        # İşle
        with st.spinner(f'{uploaded_file.name} işleniyor...'):
            final_image = process_image(img_bytes, target_width, target_height)
        
        st.success(f"{uploaded_file.name} hazır! İndirmek için sol menüye bakınız. 👈")
        
        # Sadece Sonuç Resmini Göster
        st.image(final_image, caption=f'Sonuç ({target_width}x{target_height})', width=500)
        
        # İndirme Paneli (Sidebar) - Tek dosya olduğu için direkt gösteriyoruz
        with st.sidebar:
            st.divider()
            st.header("💾 İndirme Paneli")
            
            # İndirme için hazırla
            buf = io.BytesIO()
            final_image.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            # Varsayılan dosya adı
            default_name = os.path.splitext(uploaded_file.name)[0] + "_temiz"
            
            st.info("İsmi değiştirdikten sonra **ENTER** tuşuna basınız.")
            
            # İsim Değiştirme
            custom_name = st.text_input(
                "Dosya Adı:", 
                value=default_name
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
                use_container_width=True
            )
            
        
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
