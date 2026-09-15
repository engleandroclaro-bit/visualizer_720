# -*- coding: utf-8 -*-
"""
Vizzy-Style Audio Visualizer
Python 3.11 • pygame • pygame_gui • numpy • ffmpeg • tkinter
"""

from __future__ import annotations

import json, math, os, subprocess, tempfile, wave, shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pygame, pygame_gui
from pygame import Rect, Surface
from pygame_gui.elements import (
    UIButton, UIHorizontalSlider, UILabel, UIDropDownMenu, UIPanel
)
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.windows import UIColourPickerDialog, UIMessageWindow

import tkinter as tk
from tkinter import filedialog

# --------------------------- Config --------------------------- #
class AppConfig:
    BASE_HEADER_HEIGHT = 56
    BASE_SIDEBAR_WIDTH = 360
    BASE_PREVIEW_W, BASE_PREVIEW_H = 1280, 720

    HEADER_HEIGHT = BASE_HEADER_HEIGHT
    SIDEBAR_WIDTH = BASE_SIDEBAR_WIDTH
    PREVIEW_W = BASE_PREVIEW_W
    PREVIEW_H = BASE_PREVIEW_H

    PADDING = 8
    BG_COLOR = (18, 18, 18)
    PREVIEW_BG_FALLBACK = (22, 22, 22)

    WINDOW_W = SIDEBAR_WIDTH + PADDING * 3 + PREVIEW_W
    WINDOW_H = HEADER_HEIGHT + PADDING * 3 + PREVIEW_H

    FPS = 60
    SCALE = 1.0

    SR = 44100
    FFT_SIZE = 2048

    BARS = 48
    CIRCLE_BANDS = 64

    # Detecta automaticamente o ffmpeg no sistema ou na pasta local
    FFMPEG_BIN = shutil.which('ffmpeg') or os.path.join(os.path.dirname(__file__), 'ffmpeg.exe') if os.path.exists(os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')) else 'ffmpeg'

# --------------------------- I18N --------------------------- #
I18N: Dict[str, Dict[str, Any]] = {
    'pt': {
        'app_title': 'Visualizador de Áudio',
        'new_project': 'Novo Projeto',
        'open_project': 'Abrir Projeto',
        'save': 'Salvar',
        'save_as': 'Salvar Como',
        'exit': 'Sair',
        'open_mp3': 'Abrir MP3',
        'open_lrc': 'Abrir LRC',
        'open_bg': 'Abrir BG',
        'open_logo': 'Abrir Logo',
        'sidebar_visualizer': 'Visualizador',
        'viz_bars': 'Barras',
        'viz_wave': 'Waveform',
        'viz_circle': 'Círculo',
        'appearance': 'Aparência',
        'viz_size': 'Tamanho do visualizador',
        'viz_pos_y': 'Posição do visualizador (Y)',
        'sidebar_files': 'Arquivos',
        'sidebar_lyrics': 'Letras',
        'lyrics_pos': 'Posição da letra',
        'pos_bottom': 'Inferior',
        'pos_center': 'Centro',
        'pos_top': 'Superior',
        'opacity_box': 'Opacidade da caixa',
        'show_prev_line': 'Mostrar linha anterior',
        'on': 'ON',
        'off': 'OFF',
        'bg_mode': 'Modo',
        'bg_scale': 'Escala',
        'bg_offx': 'Offset X (%)',
        'bg_offy': 'Offset Y (%)',
        'bg_reset': 'Reset BG',
        'bg_modes': ['Ajustar', 'Cobrir', 'Esticar', 'Original'],
        'lyrics_lines': 'Linhas da letra',
        'lyrics_lines_opts': ['Uma', 'Três'],
        'bars_palette': 'Paleta das barras',
        'bars_palette_opts': ['Sólido', 'Verde-Amarelo-Vermelho'],
        'circle_palette': 'Paleta do círculo',
        'circle_palette_opts': ['Magenta→Azul', 'Azul→Amarelo', 'Usar cor da barra'],
        'sidebar_logo': 'Logo',
        'logo_scale': 'Escala do logo (%)',
        'logo_offx': 'Logo Offset X (%)',
        'logo_offy': 'Logo Offset Y (%)',
        'noise_title': 'Particles / Noise',
        'noise_intensity': 'Intensidade',
        'noise_speed': 'Velocidade',
        'noise_toggle': 'Noise',
        'export': 'Exportar MP4',
        'bg_choice': 'Fundo (export)',
        'bg_choice_opts': ['Preto', 'Verde Chroma'],
        'info_done': 'Exportação concluída!',
        'err_audio': 'Nenhum áudio carregado.',
        'err_export': 'Falha na exportação; veja o log:\n',
        'choose_file': 'Escolher arquivo'
    },
    'en': {
        'app_title': 'Audio Visualizer',
        'new_project': 'New Project',
        'open_project': 'Open Project',
        'save': 'Save',
        'save_as': 'Save As',
        'exit': 'Exit',
        'open_mp3': 'Open MP3',
        'open_lrc': 'Open LRC',
        'open_bg': 'Open BG',
        'open_logo': 'Open Logo',
        'sidebar_visualizer': 'Visualizer',
        'viz_bars': 'Bars',
        'viz_wave': 'Waveform',
        'viz_circle': 'Circle',
        'appearance': 'Appearance',
        'viz_size': 'Visualizer Size',
        'viz_pos_y': 'Visualizer Position (Y)',
        'sidebar_files': 'Files',
        'sidebar_lyrics': 'Lyrics',
        'lyrics_pos': 'Lyrics Position',
        'pos_bottom': 'Bottom',
        'pos_center': 'Center',
        'pos_top': 'Top',
        'opacity_box': 'Box Opacity',
        'show_prev_line': 'Show Prev Line',
        'on': 'ON',
        'off': 'OFF',
        'bg_mode': 'Mode',
        'bg_scale': 'Scale',
        'bg_offx': 'Offset X (%)',
        'bg_offy': 'Offset Y (%)',
        'bg_reset': 'Reset BG',
        'bg_modes': ['Contain', 'Cover', 'Stretch', 'Original'],
        'lyrics_lines': 'Lyrics Lines',
        'lyrics_lines_opts': ['One', 'Three'],
        'bars_palette': 'Bars Palette',
        'bars_palette_opts': ['Solid', 'Green-Yellow-Red'],
        'circle_palette': 'Circle Palette',
        'circle_palette_opts': ['Magenta→Blue', 'Blue→Yellow', 'Use Bar Color'],
        'sidebar_logo': 'Logo',
        'logo_scale': 'Logo Scale (%)',
        'logo_offx': 'Logo Offset X (%)',
        'logo_offy': 'Logo Offset Y (%)',
        'noise_title': 'Particles / Noise',
        'noise_intensity': 'Intensity',
        'noise_speed': 'Speed',
        'noise_toggle': 'Noise',
        'export': 'Export MP4',
        'bg_choice': 'Background (export)',
        'bg_choice_opts': ['Black', 'Chroma Green'],
        'info_done': 'Export complete!',
        'err_audio': 'No audio loaded.',
        'err_export': 'Export failed; check log:\n',
        'choose_file': 'Choose file'
    }
}

VIZ_IDS = ['bars', 'waveform', 'circle']
LYR_POS_IDS = ['bottom', 'center', 'top']
BG_MODE_IDS = ['contain', 'cover', 'stretch', 'original']
LYR_LINES_IDS = ['one', 'three']
BARS_PALETTE_IDS = ['solid', 'gyr']
CIRCLE_PALETTE_IDS = ['magenta_blue', 'blue_yellow', 'use_bar']
EXPORT_BG_IDS = ['black', 'green']

def lerp(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t

def lerp_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))

def gradient3(c_low, c_mid, c_high, t):
    if t <= 0.5:
        return lerp_color(c_low, c_mid, t * 2.0)
    return lerp_color(c_mid, c_high, (t - 0.5) * 2.0)

# --------------------------- Estado --------------------------- #
@dataclass
class ProjectState:
    language: str = 'pt'
    visualizer_mode: str = 'bars'
    lyrics_position: str = 'bottom'
    lyrics_box_opacity: float = 0.6
    show_prev_line: bool = True
    noise_on: bool = False
    noise_intensity: float = 0.0
    noise_speed: float = 1.0
    bar_color: Tuple[int, int, int] = (220, 220, 220)

    mp3_path: str = ''
    lrc_path: str = ''
    bg_path: str = ''
    logo_path: str = ''

    viz_scale: float = 1.0
    viz_offset_y: float = 0.0

    bg_mode: str = 'contain'
    bg_scale: float = 1.0
    bg_offx: float = 0.0
    bg_offy: float = 0.0

    lyrics_lines_mode: str = 'three'
    bars_palette: str = 'solid'
    circle_palette: str = 'magenta_blue'

    logo_scale: float = 100.0
    logo_offx: float = 0.0
    logo_offy: float = 0.0

    export_bg: str = 'black'

@dataclass
class AudioState:
    playing: bool = False
    offset_sec: float = 0.0
    duration_sec: float = 0.0
    samples: Optional[np.ndarray] = None

    def tsec(self) -> float:
        if self.playing:
            pos_ms = pygame.mixer.music.get_pos()
            return self.offset_sec if pos_ms < 0 else pos_ms / 1000.0
        return self.offset_sec

class LRCManager:
    def __init__(self):
        self.lines: List[Tuple[float, str]] = []

    def load_from_file(self, path: str):
        self.lines.clear()
        if not path or not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                if raw.startswith('[') and ':' in raw[:5] and raw[1:3] in ('ar', 'ti', 'al', 'by'):
                    continue
                parts = raw.split(']')
                text = parts[-1].strip()
                for p in parts[:-1]:
                    p = p.lstrip('[')
                    if not p:
                        continue
                    mm_ss = p.split(':')
                    if len(mm_ss) < 2:
                        continue
                    try:
                        m = int(mm_ss[0]); s = float(mm_ss[1])
                        t = m * 60 + s
                        self.lines.append((t, text))
                    except ValueError:
                        pass
        self.lines.sort(key=lambda x: x[0])

    def trio_indices(self, tsec: float) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        if not self.lines:
            return (None, None, None)
        idx = 0
        for i, (ts, _) in enumerate(self.lines):
            if ts <= tsec:
                idx = i
            else:
                break
        prev_i = idx - 1 if idx - 1 >= 0 else None
        curr_i = idx if self.lines[idx][0] <= tsec else None
        next_i = idx + 1 if idx + 1 < len(self.lines) else None
        return (prev_i, curr_i, next_i)

# --------------------------- Projeto IO --------------------------- #
class ProjectIO:
    FIELDS = [
        'language', 'visualizer_mode', 'lyrics_position', 'lyrics_box_opacity', 'show_prev_line',
        'noise_on', 'noise_intensity', 'noise_speed', 'bar_color', 'mp3_path', 'lrc_path', 'bg_path', 'logo_path',
        'viz_scale', 'viz_offset_y', 'bg_mode', 'bg_scale', 'bg_offx', 'bg_offy', 'lyrics_lines_mode',
        'bars_palette', 'circle_palette', 'logo_scale', 'logo_offx', 'logo_offy', 'export_bg'
    ]

    @staticmethod
    def to_json(state: ProjectState) -> str:
        return json.dumps({k: getattr(state, k) for k in ProjectIO.FIELDS}, ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(txt: str) -> ProjectState:
        data = json.loads(txt)
        st = ProjectState()
        for k in ProjectIO.FIELDS:
            if k in data:
                setattr(st, k, data[k])
        if isinstance(st.bar_color, list):
            st.bar_color = tuple(int(x) for x in st.bar_color)
        return st

# --------------------------- Áudio --------------------------- #
def ffmpeg_decode_to_wav(mp3_path: str, out_wav: str, sr: int = AppConfig.SR) -> bool:
    try:
        cmd = [AppConfig.FFMPEG_BIN, '-y', '-i', mp3_path, '-vn', '-ac', '1', '-ar', str(sr), out_wav]
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
    except (FileNotFoundError, Exception):
        return False

def load_wav_mono_float(path: str) -> Tuple[Optional[np.ndarray], float]:
    try:
        with wave.open(path, 'rb') as w:
            sr = w.getframerate()
            nframes = w.getnframes()
            sw = w.getsampwidth()
            nch = w.getnchannels()
            frames = w.readframes(nframes)
            if sw != 2:
                return (None, 0.0)
            data = np.frombuffer(frames, dtype=np.int16)
            if nch > 1:
                data = data.reshape(-1, nch).mean(axis=1)
            data = (data.astype(np.float32)) / 32768.0
            return (data, len(data) / sr)
    except Exception:
        return (None, 0.0)

# --------------------------- Visualizers --------------------------- #
class VisualizerBase:
    def render(self, surf: Surface, tsec: float, app: 'App'):
        raise NotImplementedError

class VizWaveform(VisualizerBase):
    def render(self, surf: Surface, tsec: float, app: 'App'):
        w, h = surf.get_size()
        s = max(0.5, min(2.0, float(app.state.viz_scale)))
        offy = app.viz_offy_px()
        mid = h // 2 + offy
        color = app.state.bar_color
        pygame.draw.line(surf, color, (0, mid), (w, mid), 1)
        samples = app.audio.samples
        if samples is None or samples.size == 0:
            return
        sr = AppConfig.SR
        win_secs = 0.10
        half = int(win_secs * sr / 2)
        center = int(tsec * sr)
        a = max(0, center - half)
        b = min(samples.size, center + half)
        window = samples[a:b]
        if window.size < 4:
            return
        idx = np.linspace(0, window.size - 1, w).astype(np.int32)
        ys = window[idx]
        peak = float(np.max(np.abs(ys))) + 1e-6
        base = (h * 0.45) / (peak * 1.2)
        scale = base * s
        pts = [(x, mid + int(np.clip(ys[x] * scale, -h * 0.49, h * 0.49))) for x in range(w)]
        if len(pts) >= 2:
            pygame.draw.lines(surf, color, False, pts, 3)

class VizBars(VisualizerBase):
    def __init__(self):
        self.smooth = np.zeros(AppConfig.BARS, dtype=np.float32)
        self.gain = 1.0

    def render(self, surf: Surface, tsec: float, app: 'App'):
        w, h = surf.get_size()
        samples = app.audio.samples
        s = max(0.5, min(2.0, float(app.state.viz_scale)))
        offy = app.viz_offy_px()
        if samples is None or samples.size == 0:
            return
        sr = AppConfig.SR
        N = AppConfig.FFT_SIZE
        center = int(tsec * sr)
        a = max(0, center - N // 2)
        b = min(samples.size, a + N)
        window = samples[a:b]
        if window.size < N:
            pad = np.zeros(N, dtype=np.float32)
            pad[:window.size] = window
            window = pad
        win = np.hanning(N).astype(np.float32)
        spec = np.fft.rfft(window * win)
        mag = np.abs(spec).astype(np.float32)
        bands = self._bands_from_mag(mag, sr, AppConfig.BARS)
        peak = float(bands.max()) + 1e-6
        target = min(3.0, 0.95 / peak)
        self.gain = 0.02 * target + 0.98 * self.gain
        bands = np.clip(bands * self.gain, 0.0, 1.0)
        self.smooth = 0.6 * bands + 0.4 * self.smooth

        cx = w // 2
        base_bar_w = max(2, w // (AppConfig.BARS * 2))
        base_spacing = 4
        bar_w = max(1, int(base_bar_w * s))
        spacing = max(2, int(base_spacing * s))
        max_half_h = int(min(h * 0.49, h * 0.45 * s))

        low = (20, 220, 60); mid = (255, 240, 40); high = (250, 50, 30)
        solid_color = app.state.bar_color

        for i, val in enumerate(self.smooth):
            bh = int(np.clip(val * max_half_h, 2, max_half_h))
            col = gradient3(low, mid, high, float(val)) if app.state.bars_palette == 'gyr' else solid_color
            x_left = cx - (i + 1) * (bar_w + spacing)
            x_right = cx + spacing + i * (bar_w + spacing)
            pygame.draw.rect(surf, col, (x_left, h // 2 + offy - bh, bar_w, bh * 2))
            pygame.draw.rect(surf, col, (x_right, h // 2 + offy - bh, bar_w, bh * 2))

    def _bands_from_mag(self, mag: np.ndarray, sr: int, n: int) -> np.ndarray:
        freqs = np.fft.rfftfreq(AppConfig.FFT_SIZE, d=1.0 / sr)
        edges = np.geomspace(60.0, 16000.0, n + 1)
        out = np.zeros(n, dtype=np.float32)
        for i in range(n):
            idx = np.where((freqs >= edges[i]) & (freqs < edges[i + 1]))[0]
            val = 0.0 if idx.size == 0 else np.log1p(float(np.sqrt(np.mean((mag[idx]) ** 2))))
            out[i] = np.clip(val / 8.0, 0.0, 1.0)
        return out

class VizCircle(VisualizerBase):
    def __init__(self):
        self.smooth = np.zeros(AppConfig.CIRCLE_BANDS, dtype=np.float32)

    def _bands_from_mag(self, mag: np.ndarray, sr: int, n: int) -> np.ndarray:
        freqs = np.fft.rfftfreq(AppConfig.FFT_SIZE, d=1.0 / sr)
        edges = np.geomspace(60.0, 16000.0, n + 1)
        out = np.zeros(n, dtype=np.float32)
        for i in range(n):
            idx = np.where((freqs >= edges[i]) & (freqs < edges[i + 1]))[0]
            rms = 0.0 if idx.size == 0 else float(np.sqrt(np.mean((mag[idx]) ** 2)))
            out[i] = np.clip(np.log1p(rms) / 6.0, 0.0, 1.0)
        return out

    def _palette(self, app: 'App') -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        if app.state.circle_palette == 'magenta_blue':
            return (200, 40, 255), (30, 200, 255)
        if app.state.circle_palette == 'blue_yellow':
            return (60, 120, 255), (255, 210, 40)
        bc = app.state.bar_color
        return bc, (min(255, bc[0] + 40), min(255, bc[1] + 120), min(255, bc[2] + 160))

    def render(self, surf: Surface, tsec: float, app: 'App'):
        w, h = surf.get_size()
        s = max(0.5, min(2.0, float(app.state.viz_scale)))
        offy = app.viz_offy_px()
        cx, cy = w // 2, h // 2 + offy
        max_r = int(min(w, h) * 0.49)
        base_r = int(min(w, h) // 4 * s)
        base_r = max(10, min(base_r, max_r))

        samples = app.audio.samples
        if samples is None or samples.size == 0:
            pygame.draw.circle(surf, app.state.bar_color, (cx, cy), base_r, 2)
            return

        sr = AppConfig.SR
        N = AppConfig.FFT_SIZE
        center = int(tsec * sr)
        a = max(0, center - N // 2)
        b = min(samples.size, a + N)
        window = samples[a:b]
        if window.size < N:
            pad = np.zeros(N, dtype=np.float32)
            pad[:window.size] = window
            window = pad

        win = np.hanning(N).astype(np.float32)
        mag = np.abs(np.fft.rfft(window * win)).astype(np.float32)
        bands = self._bands_from_mag(mag, sr, AppConfig.CIRCLE_BANDS)
        self.smooth = 0.65 * bands + 0.35 * self.smooth

        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        inner, outer = self._palette(app)

        steps = 220
        arr = np.interp(np.linspace(0, self.smooth.size, steps, endpoint=False),
                        np.arange(self.smooth.size), self.smooth).astype(np.float32)
        arr = 0.25 * np.roll(arr, -1) + 0.5 * arr + 0.25 * np.roll(arr, 1)

        layers = 6
        for k in range(layers):
            t = k / (layers - 1) if layers > 1 else 0.0
            col = lerp_color(inner, outer, t)
            alpha = int(200 * (1.0 - t) ** 1.5)
            rg = 1.0 + 0.60 * s * (1.0 - t * 0.7)
            pts = []
            for i in range(steps):
                ang = (i / steps) * math.tau
                r = base_r * (1.0 + rg * 0.5 * float(arr[i]))
                r = min(r, max_r)
                x = cx + int(math.cos(ang) * r)
                y = cy + int(math.sin(ang) * r)
                pts.append((x, y))
            if len(pts) >= 3:
                pygame.draw.aalines(glow, (*col, alpha), True, pts)

        pygame.draw.circle(glow, (*inner, 220), (cx, cy), base_r, 2)
        surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        if app.state.visualizer_mode == 'circle' and app.state.logo_path and os.path.exists(app.state.logo_path):
            try:
                logo = pygame.image.load(app.state.logo_path).convert_alpha()
                lw, lh = logo.get_size()
                scale = max(10, int(max(lw, lh) * app.state.logo_scale / 100.0))
                if max(lw, lh) != scale:
                    if lw >= lh:
                        logo = pygame.transform.smoothscale(logo, (scale, int(lh * scale / lw)))
                    else:
                        logo = pygame.transform.smoothscale(logo, (int(lw * scale / lh), scale))
                ox = int((app.state.logo_offx / 100.0) * w * 0.5)
                oy = int((app.state.logo_offy / 100.0) * h * 0.5)
                surf.blit(logo, logo.get_rect(center=(cx + ox, cy + oy)))
            except Exception:
                pass

# --------------------------- UI --------------------------- #
class AppUI:
    def __init__(self, manager: pygame_gui.UIManager, root_rect: Rect, state: ProjectState):
        self.manager = manager
        self.root_rect = root_rect
        self.state = state

        self.header_panel: UIPanel
        self.sidebar_container: UIScrollingContainer
        self.sidebar_content: UIPanel
        self.preview_rect: Rect
        self.preview_top_panel: UIPanel

        self.controls: Dict[str, object] = {}
        self.open_section: Optional[str] = None

        self._build_layout()

    def _clear_container(self, container: UIPanel):
        for elem in list(container.get_container().elements):
            try:
                if elem is not container and hasattr(elem, 'kill'):
                    elem.kill()
            except Exception:
                pass

    def _build_layout(self):
        for attr in ('header_panel', 'sidebar_container', 'sidebar_content', 'preview_top_panel'):
            el = getattr(self, attr, None)
            if hasattr(el, 'kill'):
                try:
                    el.kill()
                except Exception:
                    pass

        try:
            self.root_rect = pygame.display.get_surface().get_rect()
        except Exception:
            pass
        r = self.root_rect

        self.header_panel = UIPanel(Rect(r.x + AppConfig.PADDING, r.y + AppConfig.PADDING,
                                         r.w - AppConfig.PADDING * 2, AppConfig.HEADER_HEIGHT),
                                    manager=self.manager)
        self._build_header()

        sb_y = self.header_panel.relative_rect.bottom + AppConfig.PADDING

        self.sidebar_container = UIScrollingContainer(
            Rect(r.x + AppConfig.PADDING, sb_y,
                 AppConfig.SIDEBAR_WIDTH, r.h - AppConfig.PADDING - sb_y),
            manager=self.manager
        )
        self.sidebar_content = UIPanel(
            Rect(0, 0, self.sidebar_container.relative_rect.w - 10, 1200),
            manager=self.manager, container=self.sidebar_container
        )
        self._build_sidebar(self.sidebar_content)

        pv_x = self.sidebar_container.relative_rect.right + AppConfig.PADDING
        pv_top = sb_y
        self.preview_top_panel = UIPanel(Rect(pv_x, pv_top, r.w - pv_x - AppConfig.PADDING, 40),
                                         manager=self.manager)
        self._build_preview_top()

        pv_y = self.preview_top_panel.relative_rect.bottom + AppConfig.PADDING // 2
        self.preview_rect = Rect(pv_x, pv_y, AppConfig.PREVIEW_W, AppConfig.PREVIEW_H)

    def _build_header(self):
        self._clear_container(self.header_panel)
        t = I18N[self.state.language]
        x = 8; y = 8; h = AppConfig.HEADER_HEIGHT - 16
        gap = 8; bw = 140

        def btn(key, label, w=bw):
            nonlocal x
            b = UIButton(Rect(x, y, w, h), label, manager=self.manager, container=self.header_panel)
            self.controls[key] = b
            x += w + gap

        btn('btn_new', t['new_project'])
        btn('btn_open', t['open_project'])
        btn('btn_save', t['save'])
        btn('btn_save_as', t['save_as'])

        w = self.header_panel.relative_rect.w
        bx = w - 340
        self.controls['btn_export'] = UIButton(Rect(bx, y, 130, h), t['export'],
                                               manager=self.manager, container=self.header_panel)
        self.controls['btn_exit'] = UIButton(Rect(bx + 140, y, 80, h), t['exit'],
                                             manager=self.manager, container=self.header_panel)

        bx2 = w - 90
        opts = I18N[self.state.language]['bg_choice_opts']
        cur = 0 if self.state.export_bg == 'black' else 1
        dd = UIDropDownMenu(options_list=opts, starting_option=opts[cur],
                            relative_rect=Rect(bx2 - 140, y, 130, h),
                            manager=self.manager, container=self.header_panel)
        self.controls['dd_export_bg'] = dd

        pt = UIButton(Rect(w - 52 - 52, y, 50, h), 'PT', manager=self.manager, container=self.header_panel)
        en = UIButton(Rect(w - 52, y, 50, h), 'EN', manager=self.manager, container=self.header_panel)
        self.controls['btn_pt'] = pt; self.controls['btn_en'] = en
        if self.state.language == 'pt':
            pt.disable(); en.enable()
        else:
            en.disable(); pt.enable()

    def _build_preview_top(self):
        self._clear_container(self.preview_top_panel)
        self.controls['lbl_time'] = UILabel(Rect(8, 8, 160, 24), '00:00 / 00:00',
                                            manager=self.manager, container=self.preview_top_panel)
        w = self.preview_top_panel.relative_rect.w
        btn_w = 90; gap = 8; x = w - (btn_w * 3 + gap * 2) - 8
        self.controls['btn_play_top']  = UIButton(Rect(x, 6, btn_w, 28), 'Play',
                                                  manager=self.manager, container=self.preview_top_panel)
        x += btn_w + gap
        self.controls['btn_pause_top'] = UIButton(Rect(x, 6, btn_w, 28), 'Pause',
                                                  manager=self.manager, container=self.preview_top_panel)
        x += btn_w + gap
        self.controls['btn_stop_top']  = UIButton(Rect(x, 6, btn_w, 28), 'Stop',
                                                  manager=self.manager, container=self.preview_top_panel)

    def _build_sidebar(self, container_panel: UIPanel):
        self._clear_container(container_panel)
        t = I18N[self.state.language]
        x, y = 8, 8
        full_w = container_panel.relative_rect.w - 16

        def section_button(key: str, title: str):
            nonlocal y
            b = UIButton(Rect(x, y, full_w, 28), f'▸ {title}', manager=self.manager, container=container_panel)
            self.controls[f'sec_{key}'] = b
            y += 32
            return b

        def label(text: str):
            nonlocal y
            UILabel(Rect(x, y, full_w, 20), text, manager=self.manager, container=container_panel)
            y += 24

        b_v = section_button('viz', t['sidebar_visualizer'])
        if self.open_section == 'viz':
            dd_labels = [t['viz_bars'], t['viz_wave'], t['viz_circle']]
            curr_idx = VIZ_IDS.index(self.state.visualizer_mode)
            dd = UIDropDownMenu(dd_labels, dd_labels[curr_idx],
                                Rect(x, y, full_w, 28), manager=self.manager, container=container_panel)
            self.controls['dd_viz'] = dd; y += 36

            label(t['viz_size'])
            self.controls['slider_viz_scale'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                   int(self.state.viz_scale * 100), (50, 200),
                                                                   manager=self.manager, container=container_panel)
            y += 32

            label(t['viz_pos_y'])
            self.controls['slider_viz_offy'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                  int(self.state.viz_offset_y), (-40, 40),
                                                                  manager=self.manager, container=container_panel)
            y += 32

            label(t['appearance'])
            bars_labels = I18N[self.state.language]['bars_palette_opts']
            curr_bars_idx = BARS_PALETTE_IDS.index(self.state.bars_palette)
            dd_bars = UIDropDownMenu(bars_labels, bars_labels[curr_bars_idx],
                                     Rect(x, y, full_w, 28), manager=self.manager, container=container_panel)
            self.controls['dd_bars_palette'] = dd_bars; y += 36

            circle_labels = I18N[self.state.language]['circle_palette_opts']
            curr_circle_idx = CIRCLE_PALETTE_IDS.index(self.state.circle_palette)
            dd_circle = UIDropDownMenu(circle_labels, circle_labels[curr_circle_idx],
                                       Rect(x, y, full_w, 28), manager=self.manager, container=container_panel)
            self.controls['dd_circle_palette'] = dd_circle; y += 36

            r, g, b = self.state.bar_color
            UILabel(Rect(x, y, 24, 20), 'R', manager=self.manager, container=container_panel)
            self.controls['slider_r'] = UIHorizontalSlider(Rect(x + 28, y, full_w - 28, 24), r, (0, 255),
                                                           manager=self.manager, container=container_panel)
            y += 28
            UILabel(Rect(x, y, 24, 20), 'G', manager=self.manager, container=container_panel)
            self.controls['slider_g'] = UIHorizontalSlider(Rect(x + 28, y, full_w - 28, 24), g, (0, 255),
                                                           manager=self.manager, container=container_panel)
            y += 28
            UILabel(Rect(x, y, 24, 20), 'B', manager=self.manager, container=container_panel)
            self.controls['slider_b'] = UIHorizontalSlider(Rect(x + 28, y, full_w - 28, 24), b, (0, 255),
                                                           manager=self.manager, container=container_panel)
            y += 32
            preview = UIButton(Rect(x, y, full_w, 24), f"RGB: {r},{g},{b}",
                               manager=self.manager, container=container_panel)
            preview.disable()
            self.controls['color_preview'] = preview
            y += 32

            if self.state.visualizer_mode == 'circle':
                b_logo = section_button('logo', I18N[self.state.language]['sidebar_logo'])
                if self.open_section == 'logo':
                    self.controls['btn_logo'] = UIButton(Rect(x, y, full_w, 28), t['open_logo'],
                                                         manager=self.manager, container=container_panel)
                    y += 32
                    UILabel(Rect(x, y, full_w, 20), t['logo_scale'], manager=self.manager, container=container_panel)
                    y += 24
                    self.controls['slider_logo_scale'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                            int(self.state.logo_scale), (10, 300),
                                                                            manager=self.manager, container=container_panel)
                    y += 32
                    UILabel(Rect(x, y, full_w, 20), t['logo_offx'], manager=self.manager, container=container_panel)
                    y += 24
                    self.controls['slider_logo_offx'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                           int(self.state.logo_offx), (-100, 100),
                                                                           manager=self.manager, container=container_panel)
                    y += 32
                    UILabel(Rect(x, y, full_w, 20), t['logo_offy'], manager=self.manager, container=container_panel)
                    y += 24
                    self.controls['slider_logo_offy'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                           int(self.state.logo_offy), (-100, 100),
                                                                           manager=self.manager, container=container_panel)
                    y += 36

        b_mp3 = section_button('files', t['open_mp3'])
        if self.open_section == 'files':
            self.controls['btn_mp3'] = UIButton(Rect(x, y, full_w, 28), t['open_mp3'],
                                                manager=self.manager, container=container_panel)
            y += 32

        b_lrc = section_button('lrc', t['sidebar_lyrics'])
        if self.open_section == 'lrc':
            self.controls['btn_lrc'] = UIButton(Rect(x, y, full_w, 28), t['open_lrc'],
                                                manager=self.manager, container=container_panel)
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['lyrics_lines'], manager=self.manager, container=container_panel)
            y += 24
            lyr_lines_labels = I18N[self.state.language]['lyrics_lines_opts']
            curr_lines_idx = LYR_LINES_IDS.index(self.state.lyrics_lines_mode)
            dd_lyr_lines = UIDropDownMenu(lyr_lines_labels, lyr_lines_labels[curr_lines_idx],
                                          Rect(x, y, full_w, 28), manager=self.manager, container=container_panel)
            self.controls['dd_lyr_lines'] = dd_lyr_lines; y += 36

            UILabel(Rect(x, y, full_w, 20), t['lyrics_pos'], manager=self.manager, container=container_panel)
            y += 24
            lyr_labels = [t['pos_bottom'], t['pos_center'], t['pos_top']]
            curr_idx = LYR_POS_IDS.index(self.state.lyrics_position)
            dd_lyr = UIDropDownMenu(lyr_labels, lyr_labels[curr_idx], Rect(x, y, full_w, 28),
                                    manager=self.manager, container=container_panel)
            self.controls['dd_lyrpos'] = dd_lyr; y += 36

            UILabel(Rect(x, y, full_w, 20),
                    f"{t['opacity_box']} ({int(self.state.lyrics_box_opacity * 100)}%)",
                    manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_opacity'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                 int(self.state.lyrics_box_opacity * 100), (0, 100),
                                                                 manager=self.manager, container=container_panel)
            y += 32
            self.controls['btn_toggle_prev'] = UIButton(
                Rect(x, y, full_w, 28),
                f"{t['show_prev_line']}: {t['on'] if self.state.show_prev_line else t['off']}",
                manager=self.manager, container=container_panel)
            y += 36

        b_bg = section_button('bg', t['open_bg'])
        if self.open_section == 'bg':
            self.controls['btn_bg'] = UIButton(Rect(x, y, full_w, 28), t['open_bg'],
                                               manager=self.manager, container=container_panel)
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['bg_mode'], manager=self.manager, container=container_panel)
            y += 24
            bg_labels = I18N[self.state.language]['bg_modes']
            curr_bg_idx = BG_MODE_IDS.index(self.state.bg_mode)
            dd_bg = UIDropDownMenu(bg_labels, bg_labels[curr_bg_idx],
                                   Rect(x, y, full_w, 28), manager=self.manager, container=container_panel)
            self.controls['dd_bg_mode'] = dd_bg; y += 36
            UILabel(Rect(x, y, full_w, 20), t['bg_scale'], manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_bg_scale'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                  int(self.state.bg_scale * 100), (10, 200),
                                                                  manager=self.manager, container=container_panel)
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['bg_offx'], manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_bg_offx'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                 int(self.state.bg_offx), (-100, 100),
                                                                 manager=self.manager, container=container_panel)
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['bg_offy'], manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_bg_offy'] = UIHorizontalSlider(Rect(x, y, full_w, 24),
                                                                 int(self.state.bg_offy), (-100, 100),
                                                                 manager=self.manager, container=container_panel)
            y += 32
            self.controls['btn_bg_reset'] = UIButton(Rect(x, y, full_w, 28), t['bg_reset'],
                                                     manager=self.manager, container=container_panel)
            y += 36

        b_noise = section_button('noise', t['noise_title'])
        if self.open_section == 'noise':
            self.controls['btn_noise_toggle'] = UIButton(
                Rect(x, y, full_w, 28),
                f"{t['noise_toggle']}: {t['on'] if self.state.noise_on else t['off']}",
                manager=self.manager, container=container_panel
            )
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['noise_intensity'], manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_noise'] = UIHorizontalSlider(
                Rect(x, y, full_w, 24), int(self.state.noise_intensity * 100), (0, 100),
                manager=self.manager, container=container_panel
            )
            y += 32
            UILabel(Rect(x, y, full_w, 20), t['noise_speed'], manager=self.manager, container=container_panel)
            y += 24
            self.controls['slider_noise_speed'] = UIHorizontalSlider(
                Rect(x, y, full_w, 24), int(self.state.noise_speed * 100), (20, 200),
                manager=self.manager, container=container_panel
            )
            y += 36

        container_panel.set_dimensions((container_panel.relative_rect.w, max(y + 8, container_panel.relative_rect.h)))

# --------------------------- App --------------------------- #
class App:
    def _fit_rect(self, max_w: int, max_h: int, aspect_w: int = 16, aspect_h: int = 9) -> Tuple[int, int]:
        target = aspect_w / aspect_h
        box = max_w / max_h
        if box > target:
            h = max_h; w = int(h * target)
        else:
            w = max_w; h = int(w / target)
        return max(320, w), max(180, h)

    def viz_offy_px(self) -> int:
        return int((self.state.viz_offset_y / 100.0) * AppConfig.PREVIEW_H * 0.4)

    def _apply_window_size(self, win_w: int, win_h: int):
        AppConfig.WINDOW_W, AppConfig.WINDOW_H = win_w, win_h
        base_h = AppConfig.BASE_HEADER_HEIGHT + AppConfig.BASE_PREVIEW_H + AppConfig.PADDING * 3
        AppConfig.SCALE = float(min(max(win_h / base_h, 0.85), 1.25))
        AppConfig.HEADER_HEIGHT = max(48, int(AppConfig.BASE_HEADER_HEIGHT * AppConfig.SCALE))
        AppConfig.SIDEBAR_WIDTH = int(min(max(win_w * 0.24, 300), 520))

        top_bar_h = 40
        inner_w = win_w - (AppConfig.PADDING * 3 + AppConfig.SIDEBAR_WIDTH)
        inner_h = win_h - (AppConfig.PADDING * 3 + AppConfig.HEADER_HEIGHT + top_bar_h + AppConfig.PADDING // 2)
        inner_w = max(320, inner_w); inner_h = max(220, inner_h)
        AppConfig.PREVIEW_W, AppConfig.PREVIEW_H = self._fit_rect(inner_w, inner_h, 16, 9)
        AppConfig.PREVIEW_W = (AppConfig.PREVIEW_W // 2) * 2
        AppConfig.PREVIEW_H = (AppConfig.PREVIEW_H // 2) * 2

        self.window = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
        self.manager.set_window_resolution((win_w, win_h))
        self.ui.root_rect = self.window.get_rect()
        self.ui._build_layout()

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Visualizador de Áudio')

        pygame.mixer.pre_init(AppConfig.SR, size=-16, channels=1)
        pygame.mixer.init()

        try:
            desk_w, desk_h = pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            desk_w, desk_h = getattr(info, 'current_w', 1600), getattr(info, 'current_h', 900)

        init_w = int(desk_w * 0.9); init_h = int(desk_h * 0.9)
        self.window = pygame.display.set_mode((init_w, init_h), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        theme_path = os.path.join(os.path.dirname(__file__), 'theme.json')
        self.manager = pygame_gui.UIManager((init_w, init_h),
                                            theme_path=theme_path if os.path.exists(theme_path) else None)

        self.state = ProjectState()
        self.audio = AudioState()
        self.lrc = LRCManager()

        self.ui = AppUI(self.manager, self.window.get_rect(), self.state)
        self._apply_window_size(init_w, init_h)

        self.viz_map = {'bars': VizBars(), 'waveform': VizWaveform(), 'circle': VizCircle()}
        self.preview_surface = Surface((AppConfig.PREVIEW_W, AppConfig.PREVIEW_H))

        self._noise_small = np.random.randint(0, 255, (180, 320), dtype=np.uint8)
        self._noise_t = 0.0

        self.project_path: Optional[str] = None
        self.tmp_wav: Optional[str] = None

    def _format_time(self, secs: float) -> str:
        m = int(max(0, secs) // 60); s = int(max(0, secs) % 60)
        return f'{m:02d}:{s:02d}'

    def _blit_bg(self):
        if not self.state.bg_path or not os.path.exists(self.state.bg_path):
            return
        try:
            img = pygame.image.load(self.state.bg_path).convert()
            iw, ih = img.get_size()
            W, H = AppConfig.PREVIEW_W, AppConfig.PREVIEW_H
            mode = self.state.bg_mode if self.state.bg_mode in BG_MODE_IDS else 'contain'
            scale_mult = max(0.1, min(2.0, float(self.state.bg_scale)))
            if mode == 'contain':
                s = min(W / iw, H / ih) * scale_mult
                dst_w, dst_h = int(iw * s), int(ih * s)
            elif mode == 'cover':
                s = max(W / iw, H / ih) * scale_mult
                dst_w, dst_h = int(iw * s), int(ih * s)
            elif mode == 'stretch':
                dst_w, dst_h = int(W * scale_mult), int(H * scale_mult)
            else:
                s = scale_mult; dst_w, dst_h = int(iw * s), int(ih * s)
            dst_w = max(1, dst_w); dst_h = max(1, dst_h)
            img2 = pygame.transform.smoothscale(img, (dst_w, dst_h)) if (dst_w, dst_h) != (iw, ih) else img
            dx = (W - dst_w) // 2; dy = (H - dst_h) // 2
            pan_base_x = max(W, dst_w) * 0.5; pan_base_y = max(H, dst_h) * 0.5
            dx += int((self.state.bg_offx / 100.0) * pan_base_x)
            dy += int((self.state.bg_offy / 100.0) * pan_base_y)
            self.preview_surface.blit(img2, (dx, dy))
        except Exception:
            pass

    def _wrap_text(self, text: str, font: pygame.font.Font, max_w: int) -> List[str]:
        words = text.split()
        lines = []; cur = ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if font.size(test)[0] <= max_w or not cur:
                cur = test
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines

    def _render_lyrics(self, tsec: float) -> None:
        if not self.lrc.lines:
            return
        pygame.font.init()
        font_curr = pygame.font.SysFont(None, 44)
        font_aux  = pygame.font.SysFont(None, 28)

        pi, ci, ni = self.lrc.trio_indices(tsec)
        prev_txt = self.lrc.lines[pi][1] if pi is not None else ''
        curr_txt = self.lrc.lines[ci][1] if ci is not None else ''
        next_txt = self.lrc.lines[ni][1] if ni is not None else ''

        pad = 20
        max_w = AppConfig.PREVIEW_W - pad * 2

        if self.state.lyrics_position == 'top':
            base_y, anchor = pad, 'top'
        elif self.state.lyrics_position == 'center':
            base_y, anchor = AppConfig.PREVIEW_H // 2, 'center'
        else:
            base_y, anchor = AppConfig.PREVIEW_H - pad, 'bottom'

        one_line = (self.state.lyrics_lines_mode == 'one')
        curr_lines = self._wrap_text(curr_txt, font_curr, max_w)
        prev_lines = self._wrap_text(prev_txt, font_aux, max_w) if not one_line else []
        next_lines = self._wrap_text(next_txt, font_aux, max_w) if not one_line else []

        gap = 6
        heights = (
            sum(font_aux.size(l)[1] for l in prev_lines) +
            (gap if prev_lines and curr_lines else 0) +
            sum(font_curr.size(l)[1] for l in curr_lines) +
            (gap if curr_lines and next_lines else 0) +
            sum(font_aux.size(l)[1] for l in next_lines)
        )
        y0 = base_y if anchor == 'top' else (base_y - heights if anchor == 'bottom' else base_y - heights // 2)

        box_opacity = int(255 * float(self.state.lyrics_box_opacity))
        if box_opacity > 0:
            box = pygame.Surface((max_w, min(AppConfig.PREVIEW_H, heights + 20)), pygame.SRCALPHA)
            box.fill((0, 0, 0, min(255, max(0, box_opacity))))
            self.preview_surface.blit(box, (pad, max(0, y0 - 10)))

        x = pad; y = y0

        def blit(lines, font, color, y):
            for line in lines:
                srf = font.render(line, True, color)
                self.preview_surface.blit(srf, (x + (max_w - srf.get_width()) // 2, y))
                y += srf.get_height()
            return y

        if (not one_line) and self.state.show_prev_line and prev_lines:
            y = blit(prev_lines, font_aux, (220, 220, 220), y); y += gap
        if curr_lines:
            y = blit(curr_lines, font_curr, (255, 255, 255), y)
        if (not one_line) and next_lines:
            y += gap; blit(next_lines, font_aux, (230, 230, 230), y)

    def _render_noise_overlay(self, dt: float) -> None:
        if not self.state.noise_on:
            return
        strength = max(0.0, min(1.0, float(self.state.noise_intensity)))
        speed_factor = max(0.2, min(2.0, float(self.state.noise_speed)))
        self._noise_t += dt * speed_factor

        base_speed = 120 + 280 * strength
        shift = int((self._noise_t * base_speed) % self._noise_small.shape[0])

        sc = 1.0 + 0.08 * math.sin(self._noise_t * 1.3)
        rolled = np.roll(self._noise_small, shift=shift, axis=0)
        noise_rgb = np.stack([rolled, rolled, rolled], axis=2)
        noise = pygame.surfarray.make_surface(noise_rgb)

        zw, zh = int(self._noise_small.shape[1] * sc), int(self._noise_small.shape[0] * sc)
        noise = pygame.transform.smoothscale(noise, (zw, zh))
        noise = pygame.transform.smoothscale(noise, (AppConfig.PREVIEW_W, AppConfig.PREVIEW_H))
        noise.set_alpha(int(255 * 0.35 * strength))
        self.preview_surface.blit(noise, (0, 0))

    def _cleanup_tmp(self) -> None:
        try:
            if self.tmp_wav and os.path.exists(self.tmp_wav):
                os.remove(self.tmp_wav)
        except Exception:
            pass

    def _render_preview(self, dt: float):
        if self.preview_surface.get_size() != (AppConfig.PREVIEW_W, AppConfig.PREVIEW_H):
            self.preview_surface = Surface((AppConfig.PREVIEW_W, AppConfig.PREVIEW_H))
        self.preview_surface.fill(AppConfig.PREVIEW_BG_FALLBACK)
        self._blit_bg()

        tsec = self.audio.tsec()
        viz = self.viz_map.get(self.state.visualizer_mode)
        if viz: viz.render(self.preview_surface, tsec, self)
        self._render_noise_overlay(dt)
        self._render_lyrics(tsec)

        self.window.fill(AppConfig.BG_COLOR)
        self.window.blit(self.preview_surface, self.ui.preview_rect)

    def _sync_dropdowns(self):
        dd = self.ui.controls.get('dd_viz')
        if isinstance(dd, UIDropDownMenu):
            options = list(dd.options_list)
            try:
                self.state.visualizer_mode = VIZ_IDS[options.index(dd.selected_option)]
            except Exception: pass
        dd = self.ui.controls.get('dd_lyrpos')
        if isinstance(dd, UIDropDownMenu):
            options = list(dd.options_list)
            try:
                self.state.lyrics_position = LYR_POS_IDS[options.index(dd.selected_option)]
            except Exception: pass
        dd = self.ui.controls.get('dd_lyr_lines')
        if isinstance(dd, UIDropDownMenu):
            options = list(dd.options_list)
            try:
                self.state.lyrics_lines_mode = LYR_LINES_IDS[options.index(dd.selected_option)]
            except Exception: pass
        dd = self.ui.controls.get('dd_bars_palette')
        if isinstance(dd, UIDropDownMenu):
            options = list(dd.options_list)
            try:
                self.state.bars_palette = BARS_PALETTE_IDS[options.index(dd.selected_option)]
            except Exception: pass
        dd = self.ui.controls.get('dd_circle_palette')
        if isinstance(dd, UIDropDownMenu):
            options = list(dd.options_list)
            try:
                self.state.circle_palette = CIRCLE_PALETTE_IDS[options.index(dd.selected_option)]
            except Exception: pass

    def _handle_header_click(self, key: str):
        t = I18N[self.state.language]
        if key == 'btn_new':
            self.state = ProjectState(language=self.state.language)
            self.audio = AudioState()
            self.lrc = LRCManager()
            self.ui.state = self.state
            self.ui.open_section = None
            self.ui._build_layout()
            self.project_path = None
        elif key == 'btn_open':
            path = self._ask_file([('Projeto JSON', '*.json'), ('All', '*.*')])
            if not path: return
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    st = ProjectIO.from_json(f.read())
                self.state = st; self.ui.state = self.state; self.ui._build_layout()
                if self.state.lrc_path and os.path.exists(self.state.lrc_path):
                    self.lrc.load_from_file(self.state.lrc_path)
                if self.state.mp3_path and os.path.exists(self.state.mp3_path):
                    self._load_mp3(self.state.mp3_path)
                self.project_path = path
                self._info('Projeto carregado.')
            except Exception as e:
                self._error(str(e))
        elif key == 'btn_save':
            if not self.project_path:
                self._handle_header_click('btn_save_as'); return
            try:
                with open(self.project_path, 'w', encoding='utf-8') as f:
                    f.write(ProjectIO.to_json(self.state))
                self._info('Projeto salvo.')
            except Exception as e:
                self._error(str(e))
        elif key == 'btn_save_as':
            path = self._ask_save([('Projeto JSON', '*.json')], default_name='projeto.json')
            if not path: return
            self.project_path = path
            self._handle_header_click('btn_save')
        elif key == 'btn_exit':
            self._should_quit = True
        elif key == 'btn_pt':
            self.state.language = 'pt'; self.ui._build_layout()
        elif key == 'btn_en':
            self.state.language = 'en'; self.ui._build_layout()
        elif key == 'btn_export':
            self._export_mp4()

    def _handle_sidebar_click(self, key: str):
        def open_only(section: Optional[str]):
            self.ui.open_section = section
            self.ui._build_sidebar(self.ui.sidebar_content)

        if key.startswith('sec_'):
            sec = key[4:]
            open_only(None if self.ui.open_section == sec else sec)
            return

        t = I18N[self.state.language]
        if key == 'btn_mp3':
            path = self._ask_file([('MP3/Audio', '*.mp3;*.m4a;*.aac;*.wav'), ('All', '*.*')])
            if path: self._load_mp3(path)

        elif key == 'btn_lrc':
            path = self._ask_file([('LRC', '*.lrc'), ('All', '*.*')])
            if path:
                self.state.lrc_path = path
                self.lrc.load_from_file(path)
                self.ui._build_sidebar(self.ui.sidebar_content)

        elif key == 'btn_bg':
            path = self._ask_file([('Image', '*.jpg;*.jpeg;*.png;*.bmp'), ('All', '*.*')])
            if path:
                self.state.bg_path = path
                self.ui._build_sidebar(self.ui.sidebar_content)

        elif key == 'btn_logo':
            path = self._ask_file([('Image', '*.png;*.jpg;*.jpeg;*.bmp'), ('All', '*.*')])
            if path:
                self.state.logo_path = path
                self.ui._build_sidebar(self.ui.sidebar_content)

        elif key == 'btn_bg_reset':
            self.state.bg_mode = 'contain'; self.state.bg_scale = 1.0
            self.state.bg_offx = 0.0; self.state.bg_offy = 0.0
            self.ui._build_sidebar(self.ui.sidebar_content)

        elif key == 'btn_toggle_prev':
            self.state.show_prev_line = not self.state.show_prev_line
            btn = self.ui.controls.get('btn_toggle_prev')
            if isinstance(btn, UIButton):
                btn.set_text(f"{t['show_prev_line']}: {t['on'] if self.state.show_prev_line else t['off']}")

    def _handle_top_audio_click(self, key: str):
        if key == 'btn_play_top':
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.audio.playing = True
            elif self.tmp_wav and os.path.exists(self.tmp_wav):
                pygame.mixer.music.load(self.tmp_wav)
                pygame.mixer.music.play()
                self.audio.playing = True
                self.audio.offset_sec = 0.0
        elif key == 'btn_pause_top':
            if self.audio.playing:
                self.audio.offset_sec = max(0.0, pygame.mixer.music.get_pos() / 1000.0)
                pygame.mixer.music.pause()
                self.audio.playing = False
        elif key == 'btn_stop_top':
            pygame.mixer.music.stop(); self.audio.playing = False; self.audio.offset_sec = 0.0

    def _handle_dropdown_change(self, ui_element):
        if isinstance(ui_element, UIDropDownMenu):
            if ui_element is self.ui.controls.get('dd_export_bg'):
                opts = list(ui_element.options_list)
                sel = opts.index(ui_element.selected_option)
                self.state.export_bg = EXPORT_BG_IDS[sel]
                return
        self._sync_dropdowns()
        self.ui._build_sidebar(self.ui.sidebar_content)

    def _handle_slider_change(self, ui_element):
        if ui_element is self.ui.controls.get('slider_opacity'):
            self.state.lyrics_box_opacity = float(ui_element.get_current_value()) / 100.0
            self.ui._build_sidebar(self.ui.sidebar_content)
        elif ui_element is self.ui.controls.get('slider_noise'):
            self.state.noise_intensity = float(ui_element.get_current_value()) / 100.0
        elif ui_element is self.ui.controls.get('slider_noise_speed'):
            self.state.noise_speed = float(ui_element.get_current_value()) / 100.0
        elif ui_element is self.ui.controls.get('slider_viz_scale'):
            self.state.viz_scale = float(ui_element.get_current_value()) / 100.0
        elif ui_element is self.ui.controls.get('slider_viz_offy'):
            self.state.viz_offset_y = float(ui_element.get_current_value())
        elif ui_element is self.ui.controls.get('slider_bg_scale'):
            self.state.bg_scale = float(ui_element.get_current_value()) / 100.0
        elif ui_element is self.ui.controls.get('slider_bg_offx'):
            self.state.bg_offx = float(ui_element.get_current_value())
        elif ui_element is self.ui.controls.get('slider_bg_offy'):
            self.state.bg_offy = float(ui_element.get_current_value())
        elif ui_element is self.ui.controls.get('slider_logo_scale'):
            self.state.logo_scale = float(ui_element.get_current_value())
        elif ui_element is self.ui.controls.get('slider_logo_offx'):
            self.state.logo_offx = float(ui_element.get_current_value())
        elif ui_element is self.ui.controls.get('slider_logo_offy'):
            self.state.logo_offy = float(ui_element.get_current_value())
        elif ui_element in (self.ui.controls.get('slider_r'),
                            self.ui.controls.get('slider_g'),
                            self.ui.controls.get('slider_b')):
            r = int(self.ui.controls['slider_r'].get_current_value())
            g = int(self.ui.controls['slider_g'].get_current_value())
            b = int(self.ui.controls['slider_b'].get_current_value())
            self.state.bar_color = (r, g, b)
            prev = self.ui.controls.get('color_preview')
            if isinstance(prev, UIButton):
                prev.set_text(f"RGB: {r},{g},{b}")

    def _ask_file(self, patterns):
        try:
            root = tk.Tk(); root.withdraw()
            path = filedialog.askopenfilename(title=I18N[self.state.language]['choose_file'], filetypes=patterns)
            root.destroy()
            return path
        except Exception:
            return ''

    def _ask_save(self, patterns, default_name='project.json'):
        try:
            root = tk.Tk(); root.withdraw()
            path = filedialog.asksaveasfilename(defaultextension='.json', initialfile=default_name, filetypes=patterns)
            root.destroy()
            return path
        except Exception:
            return ''

    def _load_mp3(self, path: str):
        self._cleanup_tmp()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav'); tmp.close()
        if not ffmpeg_decode_to_wav(path, tmp.name, AppConfig.SR):
            self._error('FFmpeg não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH do sistema.')
            try: os.remove(tmp.name)
            except Exception: pass
            return
        data, dur = load_wav_mono_float(tmp.name)
        if data is None:
            self._error('Falha ao ler WAV'); os.remove(tmp.name); return
        self.state.mp3_path = path; self.audio.samples = data
        self.audio.duration_sec = dur; self.tmp_wav = tmp.name
        try:
            pygame.mixer.music.load(self.tmp_wav)
            pygame.mixer.music.play()
            self.audio.playing = True; self.audio.offset_sec = 0.0
        except Exception as e:
            self._error(str(e))

    def _info(self, msg: str):
        try:
            UIMessageWindow(Rect(0, 0, 420, 220), html_message=msg, manager=self.manager, window_title='Info')
        except Exception:
            pass

    def _error(self, msg: str):
        try:
            UIMessageWindow(Rect(0, 0, 520, 260), html_message=msg, manager=self.manager, window_title='Erro')
        except Exception:
            pass

    def _export_mp4(self):
        t = I18N[self.state.language]
        if self.audio.samples is None or self.audio.duration_sec <= 0:
            self._error(t['err_audio']); return

        out_path = self._ask_save([('MP4', '*.mp4')], default_name='video.mp4')
        if not out_path: return

        bg_color = (0, 0, 0) if self.state.export_bg == 'black' else (0, 255, 0)
        frames_dir = tempfile.mkdtemp(prefix='viz_frames_')

        def even(n: int) -> int: return n if n % 2 == 0 else n + 1
        W = even(AppConfig.PREVIEW_W); H = even(AppConfig.PREVIEW_H)

        total_frames = int(self.audio.duration_sec * 30.0)

        old_preview = self.preview_surface
        old_rect = self.ui.preview_rect
        self.preview_surface = pygame.Surface((W, H)).convert()
        self.ui.preview_rect = Rect(self.ui.preview_rect.x, self.ui.preview_rect.y, W, H)

        try:
            for i in range(total_frames):
                tsec = i / 30.0
                self.preview_surface.fill(bg_color)
                self._blit_bg()
                viz = self.viz_map.get(self.state.visualizer_mode)
                if viz: viz.render(self.preview_surface, tsec, self)
                self._render_noise_overlay(1.0 / 30.0)
                self._render_lyrics(tsec)
                frame_path = os.path.join(frames_dir, f'frame_{i:06d}.png')
                pygame.image.save(self.preview_surface, frame_path)

                # Mantém a janela respondendo ao sistema durante o export
                pygame.event.pump()
                self.manager.update(0)
                self.manager.draw_ui(self.window)
                pygame.display.flip()

            tmp_wav = self.tmp_wav
            if not (tmp_wav and os.path.exists(tmp_wav)):
                self._error('Áudio temporário não encontrado.'); return

            log_path = os.path.join(frames_dir, 'ffmpeg_error.log')
            cmd = [
                AppConfig.FFMPEG_BIN, '-y',
                '-r', '30',
                '-f', 'image2', '-i', os.path.join(frames_dir, 'frame_%06d.png'),
                '-i', tmp_wav,
                '-shortest',
                '-vf', "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k',
                out_path
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode != 0 or (not os.path.exists(out_path) or os.path.getsize(out_path) == 0):
                with open(log_path, 'wb') as f: f.write(proc.stderr or b'')
                self._error(t['err_export'] + log_path); return

            self._info(t['info_done'])

        except Exception as e:
            self._error(f'Erro ao exportar: {e}')

        finally:
            self.preview_surface = old_preview
            self.ui.preview_rect = old_rect
            try:
                shutil.rmtree(frames_dir, ignore_errors=True)
            except Exception:
                pass

    def run(self):
        self._should_quit = False
        while not self._should_quit:
            dt = self.clock.tick(AppConfig.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._should_quit = True
                elif event.type == pygame.VIDEORESIZE:
                    self._apply_window_size(event.w, event.h)
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    for key in ['btn_new','btn_open','btn_save','btn_save_as','btn_exit','btn_pt','btn_en','btn_export']:
                        if event.ui_element is self.ui.controls.get(key):
                            self._handle_header_click(key); break
                    for key in list(self.ui.controls.keys()):
                        if key.startswith('sec_') and event.ui_element is self.ui.controls.get(key):
                            self._handle_sidebar_click(key); break
                    for key in ['btn_mp3','btn_lrc','btn_bg','btn_logo','btn_bg_reset','btn_toggle_prev','btn_noise_toggle']:
                        if event.ui_element is self.ui.controls.get(key):
                            if key == 'btn_noise_toggle':
                                self.state.noise_on = not self.state.noise_on
                                t = I18N[self.state.language]
                                event.ui_element.set_text(f"{t['noise_toggle']}: {t['on'] if self.state.noise_on else t['off']}")
                            else:
                                self._handle_sidebar_click(key)
                            break
                    for key in ['btn_play_top','btn_pause_top','btn_stop_top']:
                        if event.ui_element is self.ui.controls.get(key):
                            if self.audio.samples is None and key == 'btn_play_top':
                                self._error(I18N[self.state.language]['err_audio'])
                            else:
                                self._handle_top_audio_click(key)
                            break

                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    self._handle_dropdown_change(event.ui_element)

                elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self._handle_slider_change(event.ui_element)

                self.manager.process_events(event)

            lbl = self.ui.controls.get('lbl_time')
            if isinstance(lbl, UILabel):
                try:
                    cur = self._format_time(self.audio.tsec())
                    total = self._format_time(self.audio.duration_sec)
                    lbl.set_text(f'{cur} / {total}')
                except Exception:
                    pass

            self.manager.update(dt)
            self._render_preview(dt)
            self.manager.draw_ui(self.window)
            pygame.display.flip()

        self._cleanup_tmp()
        pygame.quit()

if __name__ == '__main__':
    App().run()