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
                final_image = process_image(img_bytes, target_width, target_height)
            
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
