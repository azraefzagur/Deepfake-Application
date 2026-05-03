import os
import httpx
from datetime import datetime

class VoiceCloner:
    def __init__(self):
        """
        Microservice client for XTTSv2 Voice Cloning.
        Relies on the tts_service running on localhost:8002.
        """
        self.tts_service_url = "http://127.0.0.1:8002/generate-audio/"
        
        # Referans ses dosyalarının bulunacağı dizin
        self.reference_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_service", "references")
        os.makedirs(self.reference_dir, exist_ok=True)
        print("VoiceCloner (Microservice Client) initialized with dynamic voices.")

    async def clone_voice(self, target_text, persona="kayit_1", rate=1.0, pitch=0, emotion='neutral'):
        """
        Sends an async HTTP POST request to the local TTS microservice.
        """
        print(f"Requesting voice clone from Microservice: '{target_text}' | Persona: {persona}")
        
        # Dinamik olarak persona adına göre (.wav) dosyasını bul (Örn: kayit_1.wav)
        reference_path = os.path.join(self.reference_dir, f"{persona}.wav")
        
        if not os.path.exists(reference_path):
            print(f"Uyarı: {reference_path} bulunamadı! İşlem iptal ediliyor.")
            return None

        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_wav = f"voice_{timestamp}.wav"
        final_path = os.path.join(output_dir, final_wav)
        
        payload = {
            "text": target_text,
            "reference_audio_path": reference_path,
            "output_path": final_path,
            "language": "tr" # Desteklenen dil
        }
        
        try:
            # XTTSv2 GPU'da saniyeler sürebilir
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.tts_service_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Microservice Success: Audio saved at {data['output_path']}")
                    return final_wav
                else:
                    print(f"Microservice Error: {response.text}")
                    return None
        except Exception as e:
            print(f"Microservice Connection Error (Is it running on 8002?): {e}")
            return None
