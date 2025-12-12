# 🎵 Python Music Visualizer

An interactive, real-time music visualizer built with Python. It captures system audio and creates a dynamic, colorful circular visualization that reacts to the beat and frequency of the music.

## ✨ Features

- **Real-time Audio Capture**: Listens to your system's output audio (Loopback).
- **Auto-Gain Control**: Automatically adjusts sensitivity so the visualization looks good at any volume.
- **Dynamic Bass Pulse**: The center circle pulses with the bass.
- **Symmetric Frequency Bars**: Colorful bars radiate from the center, representing different audio frequencies.
- **RGB Color Cycle**: Smooth color transitions for a vibrant visual experience.
- **Performance Optimized**: Uses NumPy for fast FFT calculations and Pygame for rendering.

## 🛠️ Prerequisites

You need Python 3 installed. This project relies on the following libraries:

- `pygame` (for the window and rendering)
- `soundcard` (for capturing system audio)
- `numpy` (for math and FFT calculations)

## 📦 Installation

1.  **Clone the repository** (or download the files):
    ```bash
    git clone https://github.com/YOUR_USERNAME/visualizer.git
    cd visualizer
    ```

2.  **Install dependencies**:
    ```bash
    pip install pygame soundcard numpy
    ```

## 🚀 Usage

1.  Play some music on your computer (Spotify, YouTube, etc.).
2.  Run the visualizer script:
    ```bash
    python visualizer.py
    ```
3.  The window will open and react to the music!

## ⚙️ How it Works

1.  **Audio Capture**: Uses `soundcard` to record "what you hear" from the default speaker.
2.  **FFT Analysis**: Converts the audio waveform into frequency data using Fast Fourier Transform.
3.  **Visualization**:
    - **Bass**: Low frequencies drive the pulsing size of the central circle.
    - **Mids/Highs**: Higher frequencies determine the length of the radiating bars.
    - **Smoothing**: Applies smoothing algorithms to prevent jittery movement.

## 📝 License

This project is open source and available for free. Feel free to modify and share!
