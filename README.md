# Deepfake Application

Bu proje, bir video üzerinde yüz değiştirme (face swap) işlemi gerçekleştiren web tabanlı bir simülatördür.

## 🚀 Kurulum Adımları

Arkadaşlarınızın bu projeyi kendi bilgisayarlarında çalıştırabilmesi için şu adımları izlemesi gerekmektedir:

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/azraefzagur/Deepfake-Application.git
cd Deepfake-Application
```

### 2. Büyük Model Dosyalarını Temin Edin
GitHub'ın dosya boyutu sınırları nedeniyle bazı büyük modeller (.onnx ve .pth) bu depoya dahil edilmemiştir. Lütfen bu dosyaları proje sahibinden (Drive üzerinden) temin edin:
* `inswapper_128.onnx` -> `data/` klasörüne yerleştirilmelidir.
* `insightface-0.7.3-cp39-cp39-win_amd64.whl` -> Ana dizine yerleştirilmelidir (Windows kullanıcıları için kurulumu kolaylaştırır).

### 3. API Anahtarını Yapılandırın
Proje ana dizininde `.env` adlı bir dosya oluşturun ve içine geçerli bir Gemini API anahtarı ekleyin:
```env
GEMINI_API_KEY=KENDI_API_ANAHTARINIZ_BURAYA
```

### 4. Sanal Ortamı Hazırlayın (Python 3.9 Tavsiye Edilir)
Aşağıdaki komutları sırasıyla terminalde çalıştırarak gerekli kütüphaneleri kurun:
```cmd
python -m venv .venv_deepfake
call .venv_deepfake\Scripts\activate
pip install ./insightface-0.7.3-cp39-cp39-win_amd64.whl
pip install -r requirements.txt
```

### 5. Uygulamayı Başlatın
Kurulum bittikten sonra proje klasöründeki `start.bat` dosyasına çift tıklayarak uygulamayı başlatabilirsiniz.

---
> [!IMPORTANT]
> Uygulamanın sorunsuz çalışması için Python 3.9 sürümü önerilmektedir.
