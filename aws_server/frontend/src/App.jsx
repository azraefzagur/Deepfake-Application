/**
 * DeepFace Live — Ana Uygulama Bileşeni (App.jsx) — v2 Optimized
 * ================================================================
 * WebRTC P2P videosu: Tarayıcı kamerası → AWS Signaling → GPU Worker → P2P DeepFake
 *
 * v2 eklemeleri:
 *   - Performans kontrol paneli (çözünürlük/FPS profili seçimi)
 *   - Genişletilmiş istatistikler (RTT, jitter, paket kaybı, kare düşüşü)
 *   - Asenkron modül paneli (ses klonlama / toplantı kaydı / ekran paylaşımı)
 */

import { useState, useCallback } from 'react';
import { useWebRTC } from './hooks/useWebRTC';
import { useMediaConstraints, QUALITY_PRESETS } from './hooks/useMediaConstraints';
import { useAsyncModules } from './hooks/useAsyncModules';
import VideoTile from './components/VideoTile';

// Mevcut yüz modelleri
const FACE_MODELS = [
  { id: 'face1', label: 'Yüz 1', emoji: '🧑' },
  { id: 'face2', label: 'Yüz 2', emoji: '👩' },
  { id: 'face3', label: 'Yüz 3', emoji: '🧔' },
  { id: 'face4', label: 'Yüz 4', emoji: '👱' },
  { id: 'face5', label: 'Yüz 5', emoji: '🧓' },
  { id: 'face6', label: 'Yüz 6', emoji: '👨‍🦰' },
];

// Bağlantı durumu -> Türkçe metin + dot class
const STATE_MAP = {
  idle:        { text: 'Bağlantı bekleniyor',    dotClass: 'status-dot--idle' },
  connecting:  { text: 'Bağlanıyor…',            dotClass: 'status-dot--connecting' },
  connected:   { text: 'P2P Bağlandı — WebRTC',  dotClass: 'status-dot--connected' },
  failed:      { text: 'Bağlantı başarısız',      dotClass: 'status-dot--error' },
  closed:      { text: 'Bağlantı kapatıldı',      dotClass: 'status-dot--idle' },
};

// Benzersiz istemci ID'si (her sayfa yüklemesinde yeni)
const CLIENT_ID = crypto.randomUUID?.() ?? `client-${Date.now()}`;

// AWS Signaling Server URL'si (env'den okunur, default localhost dev için)
const SIGNALING_URL = import.meta.env.VITE_SIGNALING_WS_URL ?? 'ws://localhost:8000';

export default function App() {
  const [faceModel,    setFaceModel]    = useState('face1');
  const [signalingUrl, setSignalingUrl] = useState(SIGNALING_URL);
  const [urlInput,     setUrlInput]     = useState(SIGNALING_URL);

  // ── useMediaConstraints — Çözünürlük/FPS kısıtları ──
  const { preset, setPreset, constraints, applyToStream, profile } = useMediaConstraints();

  // ── useWebRTC — Ana WebRTC bağlantısı ──
  const {
    connectionState, localStream, remoteStream, stats,
    startConnection, stopConnection, peerConnection,
  } = useWebRTC(signalingUrl, CLIENT_ID, faceModel, constraints);

  // ── useAsyncModules — Yan modüller (ses klonlama, kayıt, ekran) ──
  const { modules, moduleRegistry, toggleModule, moduleEvent } = useAsyncModules();

  const stateInfo = STATE_MAP[connectionState] ?? STATE_MAP.idle;
  const isActive  = connectionState === 'connected' || connectionState === 'connecting';

  const handleConnect = () => {
    setSignalingUrl(urlInput.trim());
    startConnection();
  };

  // Kalite profili değiştiğinde, açık stream'e de hemen uygula
  const handlePresetChange = (newPreset) => {
    setPreset(newPreset);
    if (localStream) applyToStream(localStream);
  };

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header__logo">
          <div className="header__logo-icon">🎭</div>
          <span>DeepFace Live</span>
        </div>
        <span className="header__badge">WebRTC · P2P · Optimized</span>
      </header>

      {/* ── Main ── */}
      <main className="main">

        {/* ── Video Stage ── */}
        <section className="video-stage glass-card">
          <div className="video-stage__title">
            📡 Canlı Video Akışı
          </div>

          <div className="video-grid">
            <VideoTile
              stream={localStream}
              label={`Orijinal — ${profile.width}×${profile.height} @ ${profile.fps}fps`}
              placeholder="📷"
            />
            <VideoTile
              stream={remoteStream}
              label="DeepFake (GPU)"
              isDeepfake
              placeholder="🎭"
            />
          </div>

          {/* Status Bar */}
          <div className="status-bar" role="status" aria-live="polite">
            <span className={`status-dot ${stateInfo.dotClass}`} />
            <span>{stateInfo.text}</span>
            {connectionState === 'connected' && (
              <span style={{ marginLeft: 'auto', color: 'var(--clr-text-muted)', fontVariantNumeric: 'tabular-nums' }}>
                {stats.fps | 0} fps · {stats.bitrate} kbps · {stats.rtt}ms RTT
              </span>
            )}
          </div>
        </section>

        {/* ── Sidebar ── */}
        <aside className="sidebar">

          {/* Yüz Modeli Seçimi */}
          <div className="glass-card">
            <p className="sidebar__section-title">Yüz Modeli Seç</p>
            <div className="face-grid" role="radiogroup" aria-label="Yüz modeli seçimi">
              {FACE_MODELS.map(face => (
                <button
                  key={face.id}
                  id={`face-btn-${face.id}`}
                  className={`face-card${faceModel === face.id ? ' face-card--active' : ''}`}
                  onClick={() => setFaceModel(face.id)}
                  role="radio"
                  aria-checked={faceModel === face.id}
                  title={face.label}
                >
                  <span className="face-card__emoji">{face.emoji}</span>
                  <span>{face.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* ── Performans Ayarları ── */}
          <div className="glass-card">
            <p className="sidebar__section-title">⚡ Performans Ayarları</p>
            <div className="quality-grid" role="radiogroup" aria-label="Kalite profili seçimi">
              {Object.entries(QUALITY_PRESETS).map(([key, p]) => (
                <button
                  key={key}
                  id={`quality-btn-${key}`}
                  className={`quality-btn${preset === key ? ' quality-btn--active' : ''}`}
                  onClick={() => handlePresetChange(key)}
                  role="radio"
                  aria-checked={preset === key}
                >
                  <span className="quality-btn__label">{p.label}</span>
                  <span className="quality-btn__detail">{p.width}×{p.height}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Bağlantı Ayarları */}
          <div className="glass-card">
            <p className="sidebar__section-title">Bağlantı Ayarları</p>

            <div className="input-group" style={{ marginBottom: 14 }}>
              <label htmlFor="signaling-url-input">Signaling Server (AWS)</label>
              <input
                id="signaling-url-input"
                type="text"
                value={urlInput}
                onChange={e => setUrlInput(e.target.value)}
                placeholder="wss://your-aws-domain:8000"
                disabled={isActive}
              />
            </div>

            {!isActive ? (
              <button
                id="btn-connect"
                className="btn btn--primary"
                onClick={handleConnect}
              >
                🚀 Bağlantıyı Başlat
              </button>
            ) : (
              <button
                id="btn-disconnect"
                className={`btn ${connectionState === 'connecting' ? 'btn--secondary' : 'btn--danger'}`}
                onClick={stopConnection}
              >
                {connectionState === 'connecting' ? '⏳ Bağlanıyor…' : '⏹ Bağlantıyı Kes'}
              </button>
            )}
          </div>

          {/* ── Asenkron Modüller ── */}
          <div className="glass-card">
            <p className="sidebar__section-title">🧩 Ek Modüller</p>
            <div className="module-list">
              {Object.entries(moduleRegistry).map(([key, reg]) => {
                const state = modules[key];
                return (
                  <button
                    key={key}
                    id={`module-btn-${key}`}
                    className={`module-btn${state.active ? ' module-btn--active' : ''}`}
                    onClick={() => toggleModule(key)}
                    disabled={state.loading}
                    title={reg.description}
                  >
                    <span className="module-btn__icon">{reg.label.split(' ')[0]}</span>
                    <span className="module-btn__text">
                      {reg.label.split(' ').slice(1).join(' ')}
                      {state.loading && ' ⏳'}
                    </span>
                    <span className={`module-btn__indicator${state.active ? ' module-btn__indicator--on' : ''}`} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Geliştirilmiş İstatistikler */}
          <div className="glass-card">
            <p className="sidebar__section-title">📊 Detaylı İstatistikler</p>
            <div>
              <div className="stat-row">
                <span className="stat-row__label">Protokol</span>
                <span className="stat-row__value stat-row__value--accent">WebRTC P2P</span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Çözünürlük</span>
                <span className="stat-row__value">{stats.resolution}</span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">FPS</span>
                <span className={`stat-row__value ${connectionState === 'connected' ? 'stat-row__value--success' : ''}`}>
                  {connectionState === 'connected' ? `${stats.fps | 0}` : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Bit Hızı</span>
                <span className="stat-row__value">
                  {connectionState === 'connected' ? `${stats.bitrate} kbps` : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">RTT (Gecikme)</span>
                <span className="stat-row__value">
                  {connectionState === 'connected' ? `${stats.rtt} ms` : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Jitter</span>
                <span className="stat-row__value">
                  {connectionState === 'connected' ? `${stats.jitter} ms` : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Paket Kaybı</span>
                <span className={`stat-row__value ${stats.packetsLost > 50 ? 'stat-row__value--danger' : ''}`}>
                  {connectionState === 'connected' ? stats.packetsLost : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Kareler (alınan/düşen)</span>
                <span className="stat-row__value" style={{ fontSize: '0.75rem' }}>
                  {connectionState === 'connected'
                    ? `${stats.framesReceived} / ${stats.framesDropped}`
                    : '—'}
                </span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">Yüz Modeli</span>
                <span className="stat-row__value stat-row__value--accent">{faceModel}</span>
              </div>
              <div className="stat-row">
                <span className="stat-row__label">İstemci ID</span>
                <span className="stat-row__value" style={{ fontSize: '0.68rem', opacity: 0.6 }}>
                  {CLIENT_ID.slice(0, 12)}…
                </span>
              </div>
            </div>
          </div>

          {/* Mimari Bilgisi */}
          <div className="glass-card" style={{ fontSize: '0.75rem', color: 'var(--clr-text-muted)', lineHeight: 1.7 }}>
            <p className="sidebar__section-title">Mimari</p>
            <p>🌐 <strong style={{color:'var(--clr-text-primary)'}}>AWS t2.micro</strong><br/>
              React UI + FastAPI Signaling<br/>
              Video verisi geçmez.</p>
            <p style={{marginTop: 8}}>
              🖥️ <strong style={{color:'var(--clr-text-primary)'}}>Yerel GPU</strong><br/>
              FastAPI + aiortc + CUDA<br/>
              Face-Cache + Adaptif Skip<br/>
              Ngrok ile dışarıya açıktır.
            </p>
          </div>
        </aside>
      </main>

      <footer className="footer">
        AI GENERATED — Bu sistem akademik amaçlıdır. Gerçek kişilere uygulanması yasaktır.
      </footer>
    </div>
  );
}
