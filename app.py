import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="centered")

st.title("📸 Profesyonel Arka Plan Temizleyici")

# --- Ayarlar Bölümü (Sidebar) ---
st.sidebar.header("⚙️ Ayarlar")
st.sidebar.write("Çıktı görüntüsünün boyutlarını buradan ayarlayabilirsiniz.")

target_width = st.sidebar.number_input("Genişlik (px)", min_value=100, max_value=4000, value=600, step=50)
target_height = st.sidebar.number_input("Yükseklik (px)", min_value=100, max_value=4000, value=800, step=50)

st.write(f"Resminizi yükleyin, arka planı silinsin ve **{target_width}x{target_height}** beyaz şablona oturtulsun.")


# Önbellekleme (Cache) ile her değişiklikte tekrar işlemesini engelliyoruz

# Önbellekleme (Cache) ile her değişiklikte tekrar işlemesini engelliyoruz
@st.cache_data
def process_image(image_bytes, width, height):
    # Byte verisini görsele çevir
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Arka planı kaldır
    output_image = remove(image)
    
    # 2. Yeni beyaz bir tuval oluştur (Kullanıcının seçtiği boyutlarda)
    target_size = (width, height)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 3. Resmi boyutlandır (Orantılı olarak sığdır)
    # Thumbnail metodu orantıyı bozmadan sığdırır
    # Kopyasını alıyoruz ki orijinal nesne bozulmasın (döngüsel problemlere karşı)
    img_copy = output_image.copy()
    img_copy.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # 4. Resmi merkeze yerleştir
    # Resmin yeni boyutlarını al
    img_w, img_h = img_copy.size
    
    # Ortalamak için başlangıç koordinatlarını hesapla
    offset_x = (target_size[0] - img_w) // 2
    offset_y = (target_size[1] - img_h) // 2
    
    # Yapıştır (Maske kullanarak şeffaflığı koru)
    canvas.paste(img_copy, (offset_x, offset_y), img_copy)
    
    return canvas

# Dosya Yükleme Alanı
uploaded_files = st.file_uploader("Resimleri Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # Dosyayı byte olarak oku (Cache için bu gerekli)
            img_bytes = uploaded_file.getvalue()
            
            # Görüntüleme için görseli aç
            input_image = Image.open(io.BytesIO(img_bytes))
            
            # İşle (Cache sayesinde sadece boyut değişince çalışır, isim değişince çalışmaz)
            with st.spinner(f'{uploaded_file.name} işleniyor...'):
                final_image = process_image(img_bytes, target_width, target_height)
            
            # Yan yana göster
            col1, col2 = st.columns(2)
            with col1:
                st.image(input_image, caption='Orijinal', use_container_width=True)
            with col2:
                st.image(final_image, caption=f'Sonuç ({target_width}x{target_height})', use_container_width=True)
            
            # İndirme Butonu için belleğe kaydet
            buf = io.BytesIO()
            final_image.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            # Varsayılan dosya adı (Uzantısız)
            default_name = os.path.splitext(uploaded_file.name)[0] + "_temiz"
            
            # Sidebar'a taşıma işlemi
            with st.sidebar:
                st.divider()
                st.subheader(f"⬇️ {uploaded_file.name}")
                
                # Benzersiz KEY kullanarak her dosya için ayrı input oluşturuyoruz
                st.info("İsmi değiştirdikten sonra **ENTER** tuşuna basınız.")
                custom_name = st.text_input(
                    "Yeni Dosya Adı:", 
                    value=default_name, 
                    key=f"filename_{i}_{uploaded_file.name}"
                )
                
                # Kullanıcı uzantı yazdıysa onu koru, yazmadıysa .jpg ekle
                if not custom_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    save_name = custom_name + ".jpg"
                else:
                    save_name = custom_name

                st.download_button(
                    label=f"💾 İndir ({save_name})",
                    data=byte_im,
                    file_name=save_name,
                    mime="image/jpeg",
                    key=f"download_{i}_{uploaded_file.name}",
                    use_container_width=True
                )
            
            st.success(f"{uploaded_file.name} hazır! İndirmek için sol menüye bakınız. 👈")
            st.divider()
            
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
