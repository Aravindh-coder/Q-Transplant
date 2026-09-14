'use client';

import React, { useRef, useState } from 'react';
import { Camera, RefreshCw, CheckCircle } from 'lucide-react';

interface WebcamCaptureProps {
  onCapture: (blob: Blob) => void;
}

export const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [captured, setCaptured] = useState<boolean>(false);
  const [status, setStatus] = useState<string>('Click "Start Camera" to capture live photo.');

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setStream(mediaStream);
      setCaptured(false);
      setStatus('Camera live — position face and click Capture Photo.');
    } catch (err: any) {
      setStatus('Camera access denied or unavailable on this device.');
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current || !stream) {
      setStatus('Please start the camera first.');
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          onCapture(blob);
          setCaptured(true);
          setStatus('Live photo captured successfully!');
          // Stop camera stream after capture
          stream.getTracks().forEach((track) => track.stop());
          setStream(null);
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const retakePhoto = () => {
    setCaptured(false);
    startCamera();
  };

  return (
    <div className="p-4 rounded-xl bg-slate-950/60 border border-indigo-500/30 space-y-3">
      <div className="flex justify-between items-center">
        <label className="text-xs font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
          <Camera className="w-4 h-4 text-indigo-400" /> Live Doctor Photo (Webcam Capture)
        </label>
        {captured && (
          <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
            <CheckCircle className="w-3.5 h-3.5" /> Photo Captured
          </span>
        )}
      </div>

      <div className="relative rounded-lg overflow-hidden bg-slate-900 border border-slate-800 min-h-[220px] flex items-center justify-center">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className={`w-full max-h-[260px] object-cover rounded-lg ${captured ? 'hidden' : 'block'}`}
        />
        <canvas
          ref={canvasRef}
          className={`w-full max-h-[260px] object-cover rounded-lg ${captured ? 'block' : 'hidden'}`}
        />
      </div>

      <div className="flex gap-2">
        {!stream && !captured && (
          <button
            type="button"
            onClick={startCamera}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow"
          >
            <Camera className="w-4 h-4" /> Start Camera
          </button>
        )}

        {stream && !captured && (
          <button
            type="button"
            onClick={capturePhoto}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow"
          >
            <Camera className="w-4 h-4" /> Capture Photo
          </button>
        )}

        {captured && (
          <button
            type="button"
            onClick={retakePhoto}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5"
          >
            <RefreshCw className="w-4 h-4" /> Retake Photo
          </button>
        )}
      </div>

      <p className="text-[11px] text-slate-400">{status}</p>
    </div>
  );
};
