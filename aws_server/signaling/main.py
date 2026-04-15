"""
AWS Signaling Server (Sinyalizasyon Sunucusu)
=============================================
AWS t2.micro üzerinde çalışır. Tek görevi:
1. React frontend'den WebSocket üzerinden gelen WebRTC "offer" (SDP + ICE) paketlerini almak.
2. Bu teklifi HTTP POST ile GPU worker'ın Ngrok URL'ine iletmek.
3. GPU'dan dönen "answer" paketini tekrar WebSocket üzerinden React'a göndermek.

Kurulum:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000

Ortam Değişkenleri (.env):
    GPU_WORKER_URL=https://<ngrok-id>.ngrok-free.app
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, Set

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# GPU Worker'ın Ngrok adresi — .env içinden okunur, runtime'da da değiştirilebilir
GPU_WORKER_URL: str = os.getenv("GPU_WORKER_URL", "http://localhost:8001")

# Bağlı istemcilerin WebSocket bağlantılarını tutan sözlük {client_id: websocket}
connected_clients: Dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Signaling Server başlatılıyor ===")
    logger.info(f"GPU Worker URL: {GPU_WORKER_URL}")
    yield
    logger.info("=== Signaling Server kapatılıyor ===")


app = FastAPI(
    title="DeepFake Signaling Server",
    description="WebRTC P2P bağlantısı için SDP/ICE sinyalizasyon sunucusu.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Production'da React uygulamanızın domain'i ile kısıtlayın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """AWS Load Balancer / health check endpoint."""
    return {"status": "ok", "gpu_worker_url": GPU_WORKER_URL}


@app.post("/api/set-worker-url")
async def set_worker_url(payload: dict):
    """
    Runtime'da GPU Worker URL'ini günceller (ör. Ngrok URL her başlatmada değişir).
    Payload: { "url": "https://xxxx.ngrok-free.app" }
    """
    global GPU_WORKER_URL
    new_url = payload.get("url", "").strip().rstrip("/")
    if not new_url:
        return {"error": "URL boş olamaz."}
    GPU_WORKER_URL = new_url
    logger.info(f"GPU Worker URL güncellendi: {GPU_WORKER_URL}")
    return {"status": "updated", "gpu_worker_url": GPU_WORKER_URL}


# ---------------------------------------------------------------------------
# WebSocket — Ana Sinyalizasyon Kanalı
# ---------------------------------------------------------------------------

@app.websocket("/ws/signal/{client_id}")
async def signaling_endpoint(websocket: WebSocket, client_id: str):
    """
    React frontend buraya bağlanır.
    Desteklenen mesaj tipleri:
      - { "type": "offer",   "sdp": "...", "face_model": "face1" }  → GPU worker'a iletilir
      - { "type": "ice_candidate", "candidate": {...} }              → GPU worker'a iletilir
    
    GPU Worker'dan dönen mesajlar:
      - { "type": "answer",  "sdp": "..." }
      - { "type": "ice_candidate", "candidate": {...} }
    """
    await websocket.accept()
    connected_clients[client_id] = websocket
    logger.info(f"İstemci bağlandı: {client_id}  (Toplam: {len(connected_clients)})")

    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            while True:
                raw = await websocket.receive_text()
                message = json.loads(raw)
                msg_type = message.get("type")

                logger.info(f"[{client_id}] Mesaj alındı: type={msg_type}")

                if msg_type == "offer":
                    # SDP offer'ı GPU worker'a ilet ve answer'ı al
                    payload = {
                        "sdp":  message.get("sdp"),
                        "type": "offer",
                        "client_id":  client_id,
                        "face_model": message.get("face_model", "face1"),
                    }
                    try:
                        resp = await http.post(
                            f"{GPU_WORKER_URL}/webrtc/offer",
                            json=payload,
                        )
                        resp.raise_for_status()
                        answer_data = resp.json()

                        # Answer'ı React'a geri gönder
                        await websocket.send_text(json.dumps({
                            "type": "answer",
                            "sdp":  answer_data["sdp"],
                        }))
                        logger.info(f"[{client_id}] Answer gönderildi.")

                        # GPU'dan gelen ICE adayları varsa ilet
                        for candidate in answer_data.get("ice_candidates", []):
                            await websocket.send_text(json.dumps({
                                "type":      "ice_candidate",
                                "candidate": candidate,
                            }))

                    except httpx.HTTPError as e:
                        logger.error(f"[{client_id}] GPU Worker'a erişilemedi: {e}")
                        await websocket.send_text(json.dumps({
                            "type":    "error",
                            "message": f"GPU Worker'a erişilemedi: {str(e)}",
                        }))

                elif msg_type == "ice_candidate":
                    # ICE adayını GPU worker'a ilet (Trickle ICE)
                    try:
                        await http.post(
                            f"{GPU_WORKER_URL}/webrtc/ice",
                            json={
                                "client_id": client_id,
                                "candidate": message.get("candidate"),
                            },
                        )
                    except httpx.HTTPError as e:
                        logger.warning(f"[{client_id}] ICE iletilemedi: {e}")

                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                else:
                    logger.warning(f"[{client_id}] Bilinmeyen mesaj tipi: {msg_type}")

    except WebSocketDisconnect:
        logger.info(f"İstemci bağlantıyı kesti: {client_id}")
    except Exception as e:
        logger.error(f"[{client_id}] Beklenmeyen hata: {e}")
    finally:
        connected_clients.pop(client_id, None)
        logger.info(f"İstemci kaldırıldı: {client_id}  (Kalan: {len(connected_clients)})")
