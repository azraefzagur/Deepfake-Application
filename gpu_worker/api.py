"""
GPU Worker - FastAPI API Sunucusu
==================================
Ngrok tüneli aracılığıyla dışarıya açılır.
AWS Signaling Server'dan gelen WebRTC Offer'ları karşılar,
aiortc ile Answer üretir ve WebRTC bağlantısını kurar.

Kurulum:
    pip install -r requirements.txt
    python api.py

Dışarıya açma (ayrı terminalde):
    ngrok http 8001
    -- veya --
    cloudflared tunnel --url http://localhost:8001
"""

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# aiortc
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

from rtc_worker import DeepFakeVideoTrack

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Aktif RTCPeerConnection nesnelerini tutan sözlük {client_id: pc}
peer_connections: Dict[str, RTCPeerConnection] = {}
relay = MediaRelay()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== GPU Worker başlatılıyor ===")
    logger.info(f"GPU: CUDA desteği kontrol ediliyor...")
    yield
    # Sunucu kapanırken tüm peer bağlantılarını kapat
    logger.info("Tüm WebRTC bağlantıları kapatılıyor...")
    coros = [pc.close() for pc in peer_connections.values()]
    await asyncio.gather(*coros)
    peer_connections.clear()
    logger.info("=== GPU Worker kapatıldı ===")


app = FastAPI(
    title="DeepFake GPU Worker",
    description="WebRTC tabanlı gerçek zamanlı DeepFake servisi (aiortc + InsightFace + CUDA).",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Modeller
# ---------------------------------------------------------------------------

class RTCOfferRequest(BaseModel):
    """AWS Signaling Server'ın /webrtc/offer endpoint'ine gönderdiği payload."""
    sdp:        str
    type:       str = "offer"
    client_id:  str = ""
    face_model: str = "face1"


class RTCIceRequest(BaseModel):
    """Trickle ICE adayı için."""
    client_id: str
    candidate: dict


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Ngrok tüneli doğrulama ve sağlık kontrolü."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda_available else "N/A"
    except ImportError:
        cuda_available = False
        gpu_name = "torch yüklü değil"
    return {
        "status": "ok",
        "cuda": cuda_available,
        "gpu": gpu_name,
        "active_connections": len(peer_connections),
    }


@app.post("/webrtc/offer")
async def webrtc_offer(req: RTCOfferRequest):
    """
    AWS Signaling Server buraya SDP offer gönderir.
    1. RTCPeerConnection oluşturulur.
    2. Gelen video track'e DeepFakeVideoTrack wrap'lenir.
    3. SDP answer üretilip döndürülür (Signaling Server → React'a iletecek).
    """
    client_id = req.client_id or str(uuid.uuid4())
    logger.info(f"Yeni offer alındı. client_id={client_id}, face_model={req.face_model}")

    # Eski bağlantı varsa kapat
    if client_id in peer_connections:
        await peer_connections[client_id].close()

    pc = RTCPeerConnection()
    peer_connections[client_id] = pc

    # Toplanan ICE adaylarını sakla (basit non-trickle ICE)
    ice_candidates = []

    @pc.on("icecandidate")
    def on_ice_candidate(candidate):
        if candidate:
            ice_candidates.append({
                "candidate":     candidate.candidate,
                "sdpMid":        candidate.sdpMid,
                "sdpMLineIndex": candidate.sdpMLineIndex,
            })

    @pc.on("connectionstatechange")
    async def on_connection_state_change():
        logger.info(f"[{client_id}] Bağlantı durumu: {pc.connectionState}")
        if pc.connectionState in ("failed", "closed"):
            await pc.close()
            peer_connections.pop(client_id, None)
            logger.info(f"[{client_id}] Bağlantı kaldırıldı.")

    @pc.on("track")
    def on_track(track):
        """
        Tarayıcıdan gelen video track yakalandı.
        DeepFakeVideoTrack ile wrap'le ve geri gönder.
        """
        logger.info(f"[{client_id}] Track alındı: kind={track.kind}")
        if track.kind == "video":
            deep_fake_track = DeepFakeVideoTrack(
                relay.subscribe(track),
                face_model=req.face_model,
            )
            pc.addTrack(deep_fake_track)
            logger.info(f"[{client_id}] DeepFakeVideoTrack eklendi.")

    # Offer'ı ayarla
    offer = RTCSessionDescription(sdp=req.sdp, type=req.type)
    await pc.setRemoteDescription(offer)

    # Answer üret
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # ICE gathering tamamlanana kadar kısa bir süre bekle
    await asyncio.sleep(1.0)

    logger.info(f"[{client_id}] Answer gönderiliyor. ICE adayı sayısı: {len(ice_candidates)}")

    return {
        "sdp":            pc.localDescription.sdp,
        "type":           pc.localDescription.type,
        "client_id":      client_id,
        "ice_candidates": ice_candidates,
    }


@app.post("/webrtc/ice")
async def webrtc_ice(req: RTCIceRequest):
    """
    Trickle ICE: AWS Signaling Server'dan gelen ek ICE adaylarını ekler.
    """
    client_id = req.client_id
    if client_id not in peer_connections:
        raise HTTPException(status_code=404, detail=f"Bağlantı bulunamadı: {client_id}")

    pc = peer_connections[client_id]
    try:
        from aiortc import RTCIceCandidate
        candidate_data = req.candidate
        candidate = RTCIceCandidate(
            component   = candidate_data.get("component", 1),
            foundation  = candidate_data.get("foundation", ""),
            ip          = candidate_data.get("ip", ""),
            port        = int(candidate_data.get("port", 0)),
            priority    = int(candidate_data.get("priority", 0)),
            protocol    = candidate_data.get("protocol", "udp"),
            type        = candidate_data.get("type", "host"),
            sdpMid       = candidate_data.get("sdpMid"),
            sdpMLineIndex= candidate_data.get("sdpMLineIndex"),
        )
        await pc.addIceCandidate(candidate)
        return {"status": "added"}
    except Exception as e:
        logger.error(f"[{client_id}] ICE aday ekleme hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/set-face-model/{client_id}")
async def set_face_model(client_id: str, payload: dict):
    """
    Aktif bağlantının yüz modelini değiştirir (canlı olarak).
    Payload: { "face_model": "face2" }
    """
    if client_id not in peer_connections:
        raise HTTPException(status_code=404, detail="Bağlantı bulunamadı.")
    # Not: Track referansına erişmek için DeepFakeVideoTrack'i ayrıca kaydetmek gerekir;
    # bu endpoint forward-compatibility için şimdilik stub'dur.
    model = payload.get("face_model", "face1")
    logger.info(f"[{client_id}] Face model değiştirme isteği: {model}")
    return {"status": "ok", "face_model": model}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GPU_WORKER_PORT", 8001))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
