# 🎭 Simple Voice Pitch Shifter

A lightweight Python tool to transform your voice in real-time. Shift your pitch up for a "chipmunk" effect or down for a "deep/villain" vibe.

---

## 🚀 Installation

To get started, you'll need to install the audio dependencies:

### 1. Audio Drivers
* **Windows**: Install [ASIO4ALL](https://asio4all.org) for the best performance.
* **Mac**: `brew install portaudio`
* **Linux**: `sudo apt-get install portaudio19-dev`

### 2. Python Packages
Run this command in your terminal:
```bash
pip install pyaudio numpy pedalboard
```

---

## 🛠️ How it Works

The script uses a simple processing chain:
1. **PyAudio**: Grabs your voice from the mic.
2. **Pedalboard**: Applies the `PitchShift` effect.
3. **NumPy**: Cleans up the audio data for the speakers.

---

## 🎛️ Usage
Simply run the script and speak!
```bash
python voice_changer.py
```

> **Tip:** Adjust the `PitchShift(semitones=...)` value in the code to change how high or low your voice goes.
