import pyaudio
import numpy as np
import time
import sys

# ============================================
# USER CONFIGURATION - CHANGE THESE VALUES
# ============================================
CHUNK = 60000             # Buffer size: higher = smoother, more latency (try 1024, 2048, 4096)
RATE = 44100                # Sample rate: 44100 (CD quality) or 22050 (less CPU)
PITCH_SEMITONES = 6       # Pitch shift in semitones (positive = higher, negative = lower, 0 = off)
VOLUME = 3                # Volume multiplier (>1 louder, <1 quieter)

# ============================================
# PRE-COMPUTATION FOR FAST RESAMPLING
# ============================================
if PITCH_SEMITONES != 0:
    factor = 2.0 ** (PITCH_SEMITONES / 12.0)
    new_len = int(CHUNK / factor)
    # Pre-calculate interpolation indices (only done once)
    idx = np.linspace(0, CHUNK - 1, new_len, dtype=np.float32)
    idx_floor = np.floor(idx).astype(np.int32)
    idx_frac = idx - idx_floor
    idx_ceil = np.clip(idx_floor + 1, 0, CHUNK - 1)
    # Pre-allocate output buffer
    resampled_buffer = np.zeros(CHUNK, dtype=np.float32)
else:
    factor = 1.0
    new_len = CHUNK

# ============================================
# FAST AUDIO PROCESSING FUNCTION
# ============================================
def apply_effect(in_data):
    """
    Apply pitch shift and volume boost to a chunk of audio.
    Uses pre-computed indices and minimal allocations for speed.
    """
    # Convert raw bytes to int16 numpy array
    samples = np.frombuffer(in_data, dtype=np.int16)
    
    if PITCH_SEMITONES != 0:
        # Convert to float32 for interpolation
        samples_f = samples.astype(np.float32)
        
        # Linear interpolation using pre-computed indices (very fast)
        resampled_buffer[:new_len] = (
            samples_f[idx_floor] * (1.0 - idx_frac) +
            samples_f[idx_ceil] * idx_frac
        )
        
        # Apply volume
        resampled_buffer[:new_len] *= VOLUME
        
        # Clip to int16 range to prevent distortion
        np.clip(resampled_buffer[:new_len], -32768.0, 32767.0, out=resampled_buffer[:new_len])
        
        # Zero out the rest of the buffer (padding)
        if new_len < CHUNK:
            resampled_buffer[new_len:] = 0.0
        
        # Convert back to int16 bytes
        return resampled_buffer.astype(np.int16).tobytes()
    else:
        # No pitch shift: just apply volume (faster path)
        samples_f = samples.astype(np.float32) * VOLUME
        np.clip(samples_f, -32768.0, 32767.0, out=samples_f)
        return samples_f.astype(np.int16).tobytes()

# ============================================
# PYAUDIO CALLBACK
# ============================================
def callback(in_data, frame_count, time_info, status):
    """Called by PyAudio for each audio chunk."""
    if status:
        print(f"Status: {status}", file=sys.stderr)
    if in_data:
        processed = apply_effect(in_data)
        return (processed, pyaudio.paContinue)
    return (None, pyaudio.paContinue)

# ============================================
# MAIN SETUP
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
    
    # Select input device
    device_input = input("\nEnter input device number (or press Enter for default): ").strip()
    device_index = int(device_input) if device_input else None
    
    print(f"\n=== Voice Changer Settings ===")
    print(f"CHUNK size: {CHUNK} samples ({CHUNK/RATE*1000:.1f} ms latency)")
    print(f"Sample rate: {RATE} Hz")
    print(f"Pitch shift: {PITCH_SEMITONES} semitones")
    print(f"Volume: {VOLUME}x")
    print("\nPress Ctrl+C to stop.\n")
    
    # Open audio stream
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        output=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
        stream_callback=callback
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