import sys, wave, numpy as np, sherpa_onnx, subprocess
D = sys.argv[1]; WAV = sys.argv[2]; wins = [tuple(map(float, x.split("-"))) for x in sys.argv[3:]]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{D}/sherpa-onnx-whisper-small/small-encoder.int8.onnx", decoder=f"{D}/sherpa-onnx-whisper-small/small-decoder.int8.onnx",
                                                 tokens=f"{D}/sherpa-onnx-whisper-small/small-tokens.txt", language="pt", task="transcribe", num_threads=4)
w = wave.open(WAV); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
for s0, s1 in wins:
    seg = np.concatenate([a[int(s0 * 16000):int(s1 * 16000)], np.zeros(6400, np.float32)])
    st = rec.create_stream(); st.accept_waveform(16000, seg); rec.decode_stream(st); print(f"{s0:5.1f}-{s1:5.1f}: {st.result.text}", flush=True)
