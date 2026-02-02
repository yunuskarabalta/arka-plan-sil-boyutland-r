import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# Sayfa Ayarları
st.set_page_config(page_title="Pro Arka Plan Silici", layout="wide")

st.title("📸 Profesyonel Arka Plan Temizleyici v1.2")

# --- Ayarlar Bölümü (Sidebar) ---
st.sidebar.header("⚙️ Ayarlar")

# Çıktı Modu Seçimi
st.sidebar.subheader("🎨 Çıktı Modu")
output_mode = st.sidebar.radio("Format Seçini:", ["Beyaz Şablon (JPG)", "Şeffaf / Orijinal (PNG)"])

# Boyut Ayarları (Sadece Şablon modunda aktif)
target_width = 600
target_height = 800

if output_mode == "Beyaz Şablon (JPG)":
    st.sidebar.subheader("📐 Boyutlandırma")
    st.sidebar.info("Varsayılan: 600x800. Büyük değer girerseniz resim ona göre genişletilir.")
    target_width = st.sidebar.number_input("Genişlik (px)", min_value=100, max_value=8000, value=600, step=50)
    target_height = st.sidebar.number_input("Yükseklik (px)", min_value=100, max_value=8000, value=800, step=50)
    st.write(f"Resminizi yükleyin, arka planı silinsin ve **{target_width}x{target_height}** beyaz şablona oturtulsun.")
else:
    st.sidebar.info("Resim **orijinal boyutunda** ve **arka planı şeffaf** olarak indirilecektir.")
    st.write("Resminizi yükleyin, arka planı silinsin ve orijinal boyutunda indirilsin.")

# Önbellekleme (Cache) - Parametre değiştikçe yeniden çalışır
@st.cache_data
def process_image(image_bytes, width, height, mode):
    # Byte -> PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Arka planı kaldır (rembg)
    output_image = remove(image)
    
    # Eğer Şeffaf Mod seçiliyse direkt ham halini döndür
    if mode == "Şeffaf / Orijinal (PNG)":
        return output_image
        
    # --- BEYAZ ŞABLON MODU ---
    # 2. Yeni beyaz bir tuval oluştur
    target_size = (width, height)
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    
    # 3. Resmi boyutlandır (Hem küçültme hem BÜYÜTME yapar)
    img_w, img_h = output_image.size
    
    # Sıfıra bölme hatası önlemi
    if img_w == 0 or img_h == 0:
        return canvas
    
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
    
    return canvas

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Resmi Sürükleyip Bırakın", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=False)

if uploaded_file:
    try:
        # Dosyayı byte olarak oku
        img_bytes = uploaded_file.getvalue()
        
        # İşle
        with st.spinner(f'{uploaded_file.name} işleniyor...'):
            final_image = process_image(img_bytes, target_width, target_height, output_mode)
        
        st.success(f"{uploaded_file.name} hazır! İndirmek için sol menüye bakınız. 👈")
        
        # Sonuç Resim Başlığı
        if output_mode == "Beyaz Şablon (JPG)":
            caption_text = f'Sonuç ({target_width}x{target_height})'
        else:
            caption_text = f'Sonuç (Orijinal - Şeffaf)'

        # Sadece Sonuç Resmini Göster
        st.image(final_image, caption=caption_text, width=500)
        
        # İndirme Paneli (Sidebar) - Tek dosya olduğu için direkt gösteriyoruz
        with st.sidebar:
            st.divider()
            st.header("💾 İndirme Paneli")
            
            # İndirme için hazırla
            buf = io.BytesIO()
            
            # Format Belirleme
            if output_mode == "Beyaz Şablon (JPG)":
                save_format = "JPEG"
                mime_type = "image/jpeg"
                ext = ".jpg"
            else:
                save_format = "PNG"
                mime_type = "image/png"
                ext = ".png"

            final_image.save(buf, format=save_format, quality=95)
            byte_im = buf.getvalue()
            
            # Varsayılan dosya adı
            default_name = os.path.splitext(uploaded_file.name)[0] + "_temiz"
            
            st.info("İsmi değiştirdikten sonra **ENTER** tuşuna basınız.")
            
            # İsim Değiştirme
            custom_name = st.text_input(
                "Dosya Adı:", 
                value=default_name
            )
            
            # Uzantı temizliği (kullanıcı yanlışlıkla extension yazdıysa)
            base_name = os.path.splitext(custom_name)[0]
            save_name = base_name + ext
            
            # İndirme Butonu
            st.download_button(
                label=f"💾 İndir ({save_name})",
                data=byte_im,
                file_name=save_name,
                mime=mime_type,
                use_container_width=True
            )
            
        
    except Exception as e:
        st.error(f"Hata oluştu: {e}")

