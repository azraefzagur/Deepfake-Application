# Deepfake Application

Eğlence Amaçlı Yapay Zekâ Tabanlı Deepfake Etkileşim Sistemi 
Proje Genel Bakış 

Eğlence Amaçlı Yapay Zekâ Tabanlı Deepfake Etkileşim Sistemi, ses klonlama, yüz 
değiştirme (face swap) ve yapay zekâ tabanlı konuşma simülasyonunu bir araya getiren 
etkileşimli bir multimedya projesidir. Sistem, eğlence ve parodi odaklı sanal toplantı deneyimleri 
oluşturmak amacıyla tasarlanmıştır. 

Bu sistem yalnızca akademik ve eğlence amaçlı kullanılmak üzere geliştirilmiştir ve üretilen 
içeriklerde ses ve görsel watermark (filigran) gibi güvenlik mekanizmaları içermektedir. 

Ana Özellikler 
1. Ses Klonlama Modülü 
• Önceden eğitilmiş ünlü tarzı ses modelleri  
• Kullanıcı girdisinden metinden konuşmaya (Text-to-Speech) üretim  
• Konuşma hızının, tonunun ve duygusal ifadenin ayarlanabilmesi  
• Opsiyonel gerçek zamanlı ses dönüşümü (voice conversion)  
• Üretilen sesin WAV veya MP3 formatında indirilebilmesi  
• Oluşturulan seslere duyulamaz watermark eklenmesi  

2. Yapay Zekâ Video Yüz Değiştirme Modülü 
• Önceden tanımlanmış kamuya açık kişi yüz modelleri  
• Yüz tespiti ve yüz landmark hizalama  
• Yüz ifadeleri, kafa pozisyonu ve ışık koşulları korunarak face swap işlemi  
• Gerçek zamanlı veya gerçeğe yakın video toplantı simülasyonu  
• Ekranda sürekli görünen etiketler:  
o “AI Generated”  
o “Parody Mode”  

3. Yapay Zekâ Konuşma Modülü 
• Kişilik tabanlı konuşma üretimi  
• Gerçek zamanlı iki yönlü etkileşim  
• Hem metin tabanlı sohbet hem de ses tabanlı iletişim desteği  
• Akademik değerlendirme için güvenli konuşma kayıtları  

4. Toplantı Simülasyonu Özelliği 
• Sanal video konferans ortamı  
• Yapay zekâ tarafından oluşturulan karakterin toplantı katılımcısı olarak görünmesi  
• Önceden tanımlanmış senaryolar:  
o Komedi röportajı  
o İş görüşmesi parodisi  
o Dostça tartışma  
o Motivasyon konuşması  
• Opsiyonel çok karakterli mod  

5. Nicel Değerlendirme 
Proje aynı zamanda akademik performans değerlendirmesi içerir. 
Ses Benzerliği Metrikleri 
• MCD (Mel Cepstral Distortion)  
• SNR (Signal-to-Noise Ratio)  
Video Kalite Metrikleri 
• SSIM (Structural Similarity Index)  
• PSNR (Peak Signal-to-Noise Ratio)  
Gecikme Ölçümü 
• Gerçek zamanlı simülasyon için uçtan uca sistem gecikmesi  

6. Kullanıcı Arayüzü 
• Ses, yüz ve konuşma stili için ünlü seçim paneli  
• Son çıktı üretilmeden önce gerçek zamanlı önizleme  
• Üretilen sonuçların indirilebilmesi  
• İçeriğin doğrudan kamuya otomatik paylaşılmasını kısıtlama  

Amaç 
Bu projenin amacı, yapay zekâ tabanlı medya üretim teknolojilerinin etkileşimli eğlence 
ortamlarında nasıl kullanılabileceğini araştırmak ve aynı zamanda görsel ve duyulamaz 
watermark kullanarak etik şeffaflığı sağlamaktır. 

Etik Not 
Bu proje yalnızca eğlence, parodi ve akademik değerlendirme amacıyla geliştirilmiştir. 
Üretilen tüm içerikler AI tarafından oluşturulduğunu açıkça belirtmelidir. 

Sistem: 
• Aldatma  
• Kimlik taklidi  
• Zararlı kullanım  
amacıyla kullanılmak üzere tasarlanmamıştır. 
Kullanılan Teknolojiler 

Sistem aşağıdaki teknolojileri içerebilir: 
• Yapay Zekâ (Artificial Intelligence)  
• Derin Öğrenme (Deep Learning)  
• Metinden Konuşmaya (Text-to-Speech - TTS)  
• Ses Dönüşümü (Voice Conversion)  
• Yüz Tespiti ve Yüz Değiştirme (Face Detection & Face Swapping)  
• Doğal Dil İşleme (Natural Language Processing - NLP)  
• Gerçek Zamanlı Medya İşleme  

Çıktılar 
Sistem aşağıdaki çıktıları üretir: 
• Yapay zekâ tarafından üretilmiş ses dosyaları  
• Yapay zekâ tarafından üretilmiş deepfake video çıktıları  
• Simüle edilmiş etkileşimli toplantı oturumları  
• Akademik analiz için değerlendirme sonuçları

## Kurulum Adımları

 Bu projeyi kendi bilgisayarınızda çalıştırabilmeniz için şu adımların izlenmesi gerekmektedir:

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
