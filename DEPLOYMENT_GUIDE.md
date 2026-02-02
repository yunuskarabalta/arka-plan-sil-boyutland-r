# Streamlit Cloud Dağıtım Kılavuzu

Bu projeyi Streamlit Cloud üzerinde ücretsiz olarak yayınlamak için aşağıdaki adımları izleyebilirsin.

## 1. Hazırlık
Projen zaten GitHub'a yüklendi (`requirements.txt` ve `app.py` hazır).

## 2. Streamlit Cloud'a Git
1. Tarayıcında [share.streamlit.io](https://share.streamlit.io/) adresine git.
2. GitHub hesabınla giriş yap (eğer yapmadıysan).

## 3. Yeni Uygulama Oluştur
1. Sağ üst köşedeki **"New app"** (veya "Create app") butonuna tıkla.
2. **"Use existing repo"** seçeneğini seç.

## 4. Ayarları Doldur
Açılan formda şu bilgileri seç:

- **Repository:** `yunuskarabalta/arka-plan-sil-boyutland-r`
  *(Listede çıkmazsa "Paste GitHub URL" kısmına şu linki yapıştır: `https://github.com/yunuskarabalta/arka-plan-sil-boyutland-r`)*
- **Branch:** `main`
- **Main file path:** `app.py`

## 5. Başlat
- **"Deploy!"** butonuna tıkla.

## 6. Bekle ve Test Et
- Streamlit senin için sunucuyu kuracak ve gerekli kütüphaneleri (`rembg`, `pillow` vb.) `requirements.txt` dosyasından okuyup yükleyecek.
- Bu işlem ilk seferde 2-3 dakika sürebilir (özellikle yapay zeka modellerini indirirken).
- "Your app is in the oven" yazısını görünce bekle, bittiğinde uygulaman açılacak.

## İpuçları
- Eğer "Memory (RAM)" hatası alırsan, proje çok büyük resimlerde sunucuyu zorluyor olabilir ama `rembg[cpu]` kullandığımız için genelde sorun çıkmaz.
- Bir güncelleme yapmak istersen, bilgisayarında kodu değiştirip `git push` yapman yeterli, site otomatik güncellenir.
