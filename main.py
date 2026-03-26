import os
import argparse
import mimetypes

# Fix Windows registry MIME type issues for CSS and JS
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

from flask import Flask, send_from_directory, make_response, request, jsonify
from flask_socketio import SocketIO, emit
from modules.voice_cloning import VoiceCloner
from modules.face_swap import FaceSwapper
from modules.conversation import ConversationManager
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__, static_folder='web')
app.config['SECRET_KEY'] = 'secure_offline_mode!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# Initialize Core Modules globally to keep them in memory
print("Initializing Core Intelligence Modules...")
voice_cloner = VoiceCloner()
face_swapper = FaceSwapper()
conv_manager = ConversationManager()

# Global state for asynchronous frame processing
processing_lock = False

@app.route('/')
def index():
    response = make_response(send_from_directory('web', 'index.html'))
    # FR-6.6: Block direct integration with public auto-sharing platforms.
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none';"
    return response

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

@app.route('/outputs/<path:filename>')
def serve_outputs(filename):
    """ Serve generated audio/video files """
    return send_from_directory('outputs', filename)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Endpoint mapping frontend chat to backend conversation module.
    """
    data = request.json
    user_input = data.get('message', '')
    persona = data.get('persona', 'formal')
    rate = float(data.get('rate', 1.0))
    pitch = int(data.get('pitch', 0))
    emotion = data.get('emotion', 'neutral')
    
    # 1. Update active persona
    conv_manager.set_persona(persona)
    
    # 2. Get AI response and securely log it
    ai_response = conv_manager.get_response(user_input)
    
    # 3. Generate Audio using TTS with requested controls
    audio_file = voice_cloner.clone_voice(
        target_text=ai_response, 
        rate=rate, 
        pitch=pitch, 
        emotion=emotion
    )
    audio_url = f"/outputs/{audio_file}" if audio_file else None
    
    return jsonify({"response": ai_response, "audio_url": audio_url})

@socketio.on('video_frame')
def handle_video_frame(data):
    """
    FR-2.10: Handle real-time video frames from frontend, run Face Swap, and return swapped frame.
    Uses an asynchronous-like approach by skipping frames if previous processing is still ongoing.
    """
    global processing_lock
    
    if processing_lock:
        # Önceki kare hala işleniyor, bu kareyi atla (gecikmeyi önlemek için)
        return

    image_data = data.get('image')
    face_model = data.get('face_model', 'face1')
    
    if not image_data:
        return

    # Request nesnesinden sid bilgisini iş parçacığı dışına taşıyoruz
    from flask import request as flask_request
    target_sid = flask_request.sid

    def process_and_emit(img, model, sid):
        global processing_lock
        processing_lock = True
        try:
            # Face Swap işlemini yap
            processed_image = face_swapper.process_frame(img, model)
            # SocketIO üzerinden sadece ilgili kullanıcıya (sid) geri gönder
            socketio.emit('processed_frame', {'image': processed_image}, room=sid)
        except Exception as e:
            print(f"Frame Processing Error: {e}")
        finally:
            processing_lock = False

    # Arka planda çalıştır
    socketio.start_background_task(process_and_emit, image_data, face_model, target_sid)

def main():
    print("AI-Based Deepfake Interaction System Intialized")
    print("Modules loaded successfully. Starting Local Server on http://127.0.0.1:5000")
    
    # Run server locally (prevents public auto-sharing by default)
    # Note: debug=True will autoreload when this file saves
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    main()
