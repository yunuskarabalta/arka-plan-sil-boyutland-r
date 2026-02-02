# Python Arka Plan Kaldırma Botu

Bu basit araç, `input` klasörüne koyduğunuz resimlerin arka planını otomatik olarak temizler ve `output` klasörüne kaydeder.

## Kurulum

1. Bilgisayarınızda Python'un yüklü olduğundan emin olun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

1. Bu scripti ilk kez çalıştırdığınızda otomatik olarak `input` ve `output` klasörlerini oluşturacaktır:
   ```bash
   python main.py
   ```
2. Arka planını silmek istediğiniz resimleri oluşan `input` klasörünün içine atın.
3. Tekrar `python main.py` komutunu çalıştırın.
4. Temizlenmiş resimlerinizi `output` klasöründe bulabilirsiniz.

## Not
İlk çalıştırmada yapay zeka modeli indirileceği için işlem biraz uzun sürebilir. Sonraki işlemlerde çok daha hızlı olacaktır.
