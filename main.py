import os
from rembg import remove
from PIL import Image

def process_images():
    # Klasör yollarını tanımla
    input_folder = 'input'
    output_folder = 'output'

    # Klasörlerin varlığını kontrol et, yoksa oluştur
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"'{input_folder}' klasörü oluşturuldu. Lütfen resimlerinizi bu klasöre koyun.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Input klasöründeki dosyaları listele
    files = os.listdir(input_folder)
    
    # Resim dosyalarını filtrele (jpg, jpeg, png)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if not image_files:
        print(f"'{input_folder}' klasöründe hiç resim bulunamadı.")
        return

    print(f"Toplam {len(image_files)} resim işlenecek...")

    for filename in image_files:
        try:
            input_path = os.path.join(input_folder, filename)
            
            # Çıktı dosya adını oluştur (.png olarak kaydetmek en iyisidir çünkü şeffaflık destekler)
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_no_bg.png"
            output_path = os.path.join(output_folder, output_filename)

            print(f"İşleniyor: {filename} -> {output_filename}")

            # Resmi aç
            input_image = Image.open(input_path)

            # Arka planı kaldır
            output_image = remove(input_image)

            # Kaydet
            output_image.save(output_path)
            
        except Exception as e:
            print(f"Hata oluştu ({filename}): {e}")

    print("\nİşlem tamamlandı! Resimlerinizi 'output' klasöründe bulabilirsiniz.")

if __name__ == "__main__":
    process_images()
