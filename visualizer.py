import pygame
import soundcard as sc
import numpy as np
import colorsys
import sys
import random
import warnings

warnings.filterwarnings("ignore", category=UserWarning) 
warnings.filterwarnings("ignore", message=".*data discontinuity.*")


WIDTH, HEIGHT = 1080, 500
FPS = 60
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024  
FFT_SIZE = BUFFER_SIZE // 2
BAR_COUNT = 140 
HALF_BARS = BAR_COUNT // 2
BASE_RADIUS = 90
MAX_BAR_LENGTH = 300 
MIN_FREQ_INDEX = 2
MAX_FREQ_INDEX = 80 
TRAIL_ALPHA = 60

class Particle:
    def __init__(self, x, y, color, speed_mult):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(4, 10) * speed_mult
        self.vx = np.cos(angle) * speed
        self.vy = np.sin(angle) * speed
        self.life = 255
        self.decay = random.uniform(8, 15)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        if self.life > 0:
            col = list(self.color)
            fade_factor = max(0, self.life / 255.0)
            r = int(col[0] * fade_factor)
            g = int(col[1] * fade_factor)
            b = int(col[2] * fade_factor)
            try:
                pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), self.size)
            except ValueError:
                pass

def get_rainbow_color(hue):
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Music Visualizer")
    clock = pygame.time.Clock()

    trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    trail_surface.fill((0, 0, 0, TRAIL_ALPHA))

    try:
        default_speaker = sc.default_speaker()
        mics = sc.all_microphones(include_loopback=True)
        loopback_mic = sc.default_microphone() 
        for mic in mics:
            if default_speaker.name in mic.name or "Loopback" in mic.name:
                 loopback_mic = mic
                 break
        print(f"Recording from: {loopback_mic.name}")
    except Exception as e:
        print(f"Audio init failed: {e}")
        return

    hue_offset = 0
    bar_heights = np.zeros(BAR_COUNT)
    particles = []
    
    angles = np.linspace(-np.pi/2, 1.5*np.pi, BAR_COUNT, endpoint=False)

    rolling_peak = 0.01

    try:
        with loopback_mic.recorder(samplerate=SAMPLE_RATE) as mic:
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        pass
                        trail_surface = pygame.Surface(event.size, pygame.SRCALPHA)
                        trail_surface.fill((0, 0, 0, TRAIL_ALPHA))

                w, h = screen.get_size()
                cx, cy = w // 2, h // 2

                try:
                    raw_data = mic.record(numframes=BUFFER_SIZE)
                    mono = np.mean(raw_data, axis=1)
                except Exception:
                    mono = np.zeros(BUFFER_SIZE)

                if len(mono) == BUFFER_SIZE:
                    windowed = mono * np.hanning(len(mono))
                    spectrum = np.abs(np.fft.rfft(windowed))[:MAX_FREQ_INDEX]
                else:
                    spectrum = np.zeros(MAX_FREQ_INDEX)

                curr_peak = np.max(spectrum) if len(spectrum) > 0 else 0
                
                if curr_peak > rolling_peak:
                     rolling_peak = rolling_peak * 0.9 + curr_peak * 0.1
                else:
                     rolling_peak = rolling_peak * 0.995 + curr_peak * 0.005
                
                if rolling_peak < 0.2: rolling_peak = 0.2
                
                scale_factor = 40.0 / rolling_peak
                spectrum = spectrum * scale_factor

                bass_energy = np.mean(spectrum[1:5]) 
                if np.isnan(bass_energy): bass_energy = 0
                
                pulse_add = min(bass_energy * 2, 150)
                radius = BASE_RADIUS + pulse_add
                
                if pulse_add > 50:
                    pass

                chunk_size = len(spectrum) // HALF_BARS
                if chunk_size < 1: chunk_size = 1
                
                half_bars = []
                for i in range(HALF_BARS):
                    s = i * chunk_size
                    e = s + chunk_size
                    val = np.max(spectrum[s:e]) if s < len(spectrum) else 0
                    
                    gain = 0.5 + (i / HALF_BARS) * 3.0
                    
                    half_bars.append(val * 3 * gain) 

                full_bars = half_bars + half_bars[::-1]
                
                for i in range(BAR_COUNT):
                    if i < len(full_bars):
                        bar_heights[i] = full_bars[i]

                screen.fill((0, 0, 0))

                hue_offset = (hue_offset + 0.02) % 1.0 
                main_color = get_rainbow_color(hue_offset)

                try:
                    pygame.draw.circle(screen, main_color, (cx, cy), int(radius), 4)
                except: pass

                for i, height in enumerate(bar_heights):
                    if height < 5: continue
                    height = min(height, MAX_BAR_LENGTH)
                    
                    ang = angles[i]
                    cos_a, sin_a = np.cos(ang), np.sin(ang)
                    
                    sx = cx + cos_a * radius
                    sy = cy + sin_a * radius
                    ex = cx + cos_a * (radius + height)
                    ey = cy + sin_a * (radius + height)
                    
                    bar_hue = (hue_offset + abs(i - HALF_BARS)/HALF_BARS) % 1.0
                    col = get_rainbow_color(bar_hue)
                    
                    pygame.draw.line(screen, col, (sx, sy), (ex, ey), 4)

                pygame.display.flip()
                clock.tick(FPS)

    except Exception as outer_e:
        print(f"Critical Loop Error: {outer_e}")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
