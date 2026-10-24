import sys, wave, numpy as np, sherpa_onnx
D = "/root/.cache/edicao-video/asr"; WAV = sys.argv[1]; wins = [tuple(map(float, w.split(":"))) for w in sys.argv[2:]]
w = wave.open(WAV); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{D}/sherpa-onnx-whisper-small/small-encoder.int8.onnx", decoder=f"{D}/sherpa-onnx-whisper-small/small-decoder.int8.onnx",
    tokens=f"{D}/sherpa-onnx-whisper-small/small-tokens.txt", language="pt", task="transcribe", num_threads=4)
for s, e in wins:
    st = rec.create_stream(); st.accept_waveform(16000, a[int(s * 16000):int(e * 16000)]); rec.decode_stream(st); print(f"{s:5.2f}-{e:5.2f} {st.result.text.strip()}")
