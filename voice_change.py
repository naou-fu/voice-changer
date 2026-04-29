import pyaudio
import numpy as np
import time
import sys
from pedalboard import Pedalboard, PitchShift, Gain, Clipping

# ============================================
# USER CONFIGURATION
# ============================================
CHUNK = 60000                # Samples per callback (23 ms @ 44100 Hz) – low latency
RATE = 44100                # Sample rate
PITCH_SEMITONES = -3         # Pitch shift (positive = higher, negative = lower, 0 = off)
VOLUME_DB = 9            # Volume in dB (0 = no change, e.g., +6 = louder, -6 = quieter)

# ============================================
# BUILD EFFECT CHAIN (done once)
# ============================================
board = Pedalboard([
    PitchShift(semitones=PITCH_SEMITONES),
    Gain(gain_db=VOLUME_DB),
    # Soft clipping to prevent digital distortion
    Clipping(threshold_db=0.0),
])

# ============================================
# PYAUDIO CALLBACK
# ============================================
def callback(in_data, frame_count, time_info, status):
    """Process each audio chunk seamlessly."""
    if status:
        print(f"Status: {status}", file=sys.stderr)
    if in_data:
        # Convert raw bytes → float32 audio array (pedalboard expects float32)
        audio = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        # Apply the pedalboard effect (keeps length identical)
        processed = board(audio, RATE)
        # Convert back to int16
        out_data = (processed * 32768.0).astype(np.int16).tobytes()
        return (out_data, pyaudio.paContinue)
    return (None, pyaudio.paContinue)

# ============================================
# MAIN (unchanged, same device selection)
# ============================================
def list_devices(p):
    """Print available audio devices."""
    print("\n=== Available Audio Devices ===")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']} (in:{dev['maxInputChannels']}, out:{dev['maxOutputChannels']})")

def main():
    p = pyaudio.PyAudio()
    list_devices(p)

    device_input = input("\nEnter input device number (or press Enter for default): ").strip()
    device_index = int(device_input) if device_input else None

    print(f"\n=== Voice Changer Settings ===")
    print(f"CHUNK size: {CHUNK} samples ({CHUNK/RATE*1000:.1f} ms latency)")
    print(f"Sample rate: {RATE} Hz")
    print(f"Pitch shift: {PITCH_SEMITONES} semitones")
    print(f"Volume gain: {VOLUME_DB} dB")
    print("\nPress Ctrl+C to stop.\n")

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        output=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
        stream_callback=callback,
    )
    stream.start_stream()

    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Voice changer stopped.")

if __name__ == "__main__":
    main()