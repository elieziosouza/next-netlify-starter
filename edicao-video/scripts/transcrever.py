import sys, wave, json, numpy as np, sherpa_onnx
D = sys.argv[1]; WAV = sys.argv[2]; OUT = sys.argv[3]
w = wave.open(WAV); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{D}/sherpa-onnx-whisper-small/small-encoder.int8.onnx",
    decoder=f"{D}/sherpa-onnx-whisper-small/small-decoder.int8.onnx",
    tokens=f"{D}/sherpa-onnx-whisper-small/small-tokens.txt",
    language="pt", task="transcribe", num_threads=4)
cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = f"{D}/silero_vad.onnx"
cfg.silero_vad.min_silence_duration = 0.25; cfg.silero_vad.min_speech_duration = 0.2
cfg.silero_vad.max_speech_duration = 8; cfg.sample_rate = 16000
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
segs = []; ws = cfg.silero_vad.window_size; i = 0
def drain():
    while not vad.empty():
        s = vad.front; st = s.start / 16000; samples = np.array(s.samples, np.float32)
        segs.append((st, st + len(samples) / 16000, samples)); vad.pop()
while i + ws <= len(a):
    vad.accept_waveform(a[i:i + ws]); i += ws; drain()
vad.flush(); drain()
out = []
for st, en, smp in segs:
    s = rec.create_stream(); s.accept_waveform(16000, smp); rec.decode_stream(s)
    txt = s.result.text.strip()
    out.append(dict(start=round(st, 2), end=round(en, 2), text=txt)); print(f"[{st:6.2f}-{en:6.2f}] {txt}", flush=True)
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
