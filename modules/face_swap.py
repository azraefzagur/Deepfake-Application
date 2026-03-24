import cv2
import base64
import numpy as np
import os
import insightface
from insightface.app import FaceAnalysis

class FaceSwapper:
    def __init__(self):
        print("FaceSwapper başlatılıyor (InsightFace True Deepfake)...")
        # Define the static image paths to swap onto the user's face
        self.available_models = {
            "face1": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face1.png'), 
            "face2": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face2.png'),
            "face3": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face3.jpeg'),
            "face4": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face4.jpeg'),
            "face5": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face5.jpeg'),
            "face6": os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'source_faces', 'face6.jpeg')
        }
        self.active_model_path = None
        self.source_face = None
        
        self.app = None
        self.swapper = None
        
        try:
            # 1. Initialize FaceAnalysis for detecting faces
            # This will download the buffalo_l model (~330MB) to ~/.insightface/models on first run!
            print("FaceAnalysis modelleri yükleniyor (İlk açılışta sürebilir)...")
            self.app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(320, 320))
            
            # 2. Load Inswapper Model
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'models', 'inswapper_128.onnx')
            if os.path.exists(model_path):
                self.swapper = insightface.model_zoo.get_model(model_path, download=False, download_zip=False, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
                print("FaceSwapper modülü BAŞARIYLA başlatıldı! (Inswapper ONNX hazır)")
            else:
                print(f"KRİTİK HATA - ONNX Modeli bulunamadı: {model_path}")
                
        except Exception as e:
            print(f"KRİTİK HATA - InsightFace Yüklenemedi: {e}")

    def _load_source_face(self, image_path):
        """ Extract the 512D face embeddings from the target image. """
        if not os.path.exists(image_path):
            return None
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        faces = self.app.get(img)
        if len(faces) > 0:
            return faces[0]
        return None

    def select_model(self, model_id):
        """ Cache the embeddings of the selected persona face """
        if model_id in self.available_models:
            self.active_model_path = self.available_models[model_id]
            self.source_face = self._load_source_face(self.active_model_path)
            print(f"Face model selected and cached: {model_id}")
            return True
        return False

    def process_frame(self, base64_image, target_model_id):
        """
        Takes the user's webcam frame, finds their face, and completely replaces it with the configured source face.
        """
        try:
            if not base64_image or "," not in base64_image:
                return base64_image
                
            # Dinamik model değiştirme
            if target_model_id in self.available_models and self.available_models[target_model_id] != self.active_model_path:
                self.select_model(target_model_id)
                
            # 1. Decode base64
            encoded_data = base64_image.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return base64_image
            
            # 2. True Deepfake Swap
            if self.app is not None and self.swapper is not None and self.source_face is not None:
                faces = self.app.get(img)
                # Sadece bir yüzü (kullanıcıyı) analiz et ve değiştir
                if len(faces) > 0:
                    img = self.swapper.get(img, faces[0], self.source_face, paste_back=True)
            
            # 3. FR-2.11 Kalıcı filigran (Watermark)
            cv2.putText(img, "AI GENERATED - DEEPFAKE", (15, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 4. Encodlama
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            return "data:image/jpeg;base64," + encoded_img
            
        except Exception as e:
            print("Video Processing Error:", e)
            return base64_image