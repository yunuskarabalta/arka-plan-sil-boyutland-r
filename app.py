import streamlit as st
from rembg import remove
from PIL import Image
import io

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="centered")

st.title("📸 Profesyonel Arka Plan Temizleyici")
st.write("Resminizi yükleyin, arka planı silinsin ve 600x800 beyaz şablona oturtulsun.")

def process_image(image):
    # 1. Arka planı kaldır
    output_image = remove(image)
    
    # 2. Yeni beyaz bir tuval oluştur (600x800)
    target_size = (600, 800)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 3. Resmi boyutlandır (Orantılı olarak sığdır)
    # Thumbnail metodu orantıyı bozmadan sığdırır
    output_image.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # 4. Resmi merkeze yerleştir
    # Resmin yeni boyutlarını al
    img_w, img_h = output_image.size
    
    # Ortalamak için başlangıç koordinatlarını hesapla
    offset_x = (target_size[0] - img_w) // 2
    offset_y = (target_size[1] - img_h) // 2
    
    # Yapıştır (Maske kullanarak şeffaflığı koru)
    canvas.paste(output_image, (offset_x, offset_y), output_image)
    
    return canvas

# Dosya Yükleme Alanı
uploaded_files = st.file_uploader("Resimleri Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # Resmi oku
            input_image = Image.open(uploaded_file)
            
            # İşle
            with st.spinner(f'{uploaded_file.name} işleniyor...'):
                final_image = process_image(input_image)
            
            # Yan yana göster
            col1, col2 = st.columns(2)
            with col1:
                st.image(input_image, caption='Orijinal', use_container_width=True)
            with col2:
                st.image(final_image, caption='Sonuç (600x800 Beyaz)', use_container_width=True)
            
            # İndirme Butonu için belleğe kaydet
            buf = io.BytesIO()
            final_image.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            file_name = uploaded_file.name.split('.')[0] + "_processed.jpg"
            
            st.download_button(
                label=f"⬇️ İndir: {file_name}",
                data=byte_im,
                file_name=file_name,
                mime="image/jpeg"
            )
            
            st.success(f"{uploaded_file.name} tamamlandı!")
            st.divider()
            
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
