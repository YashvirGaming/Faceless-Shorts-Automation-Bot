import asyncio
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEvent, QPropertyAnimation, QSize, Qt, QThread, QTimer, QUrl, Signal, qInstallMessageHandler
from PySide6.QtGui import QColor, QDesktopServices, QFontDatabase, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QDialog, QFileDialog, QFormLayout, QFrame,
    QGraphicsDropShadowEffect, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QSlider, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

try:
    import edge_tts
except Exception:
    edge_tts = None

APP_NAME = "SHORTS CREATOR APP"
APP_VERSION = "1.0.1"
AUTHOR = "YashvirGaming"
YOUTUBE_URL = "https://youtube.com/@YashvirGaming"
GITHUB_URL = "https://github.com/YashvirGaming"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
FONT_EXT = {".ttf", ".otf"}
NO_WINDOW = 0x08000000 if os.name == "nt" else 0

BG = "#050806"
PANEL = "#0a120e"
PANEL2 = "#0e1a14"
BORDER = "#0f5c3a"
NEON = "#00ff9c"
NEON_DIM = "#00b36b"
TEXT = "#c8ffe6"
MUTED = "#5f8f7a"
WARN = "#ff4d6d"

POP_TAG = "{\\fscx70\\fscy70\\t(0,100,\\fscx112\\fscy112)\\t(100,180,\\fscx100\\fscy100)}"
GLOW_TAG = "{\\blur14\\alpha&H50&}"

PROGRESS_KEYS = {
    "frame", "fps", "bitrate", "total_size", "out_time_us", "out_time_ms", "out_time",
    "dup_frames", "drop_frames", "speed", "progress", "stream_0_0_q", "stream_0_1_q",
}

DEFAULT_SCRIPT = (
    "A British MP wants to sell Diego Garcia to the United States. "
    "A Conservative lawmaker has proposed selling the military base directly to Washington "
    "for six billion pounds sterling, about 378 billion Mauritian rupees. "
    "The suggestion was made in the House of Commons on Monday, October 19, "
    "while London continues negotiations with Mauritius and Washington "
    "to secure the long-term future of military operations on this atoll in the Chagos Archipelago. "
    "Sir Edward Leigh, MP for Gainsborough, says the sale would meet both security needs and defence funding. "
    "His question to the government: why not create a virtuous circle, "
    "sell the base to President Trump for six billion pounds, "
    "then use that money to raise defence spending to three percent of GDP by 2030?"
)

DEFAULT_CUES = [
    ("A British MP", "chagos-sovereignty"),
    ("military base", "main-qimg"),
    ("six billion pounds sterling", "im-73073017"),
    ("negotiations with Mauritius", "map-of-chagos"),
    ("Chagos Archipelago", "75887790"),
    ("Sir Edward Leigh", "sir_edward_leigh"),
    ("defence funding", "images (1)"),
    ("President Trump", "1000w_q95"),
    ("three percent", "images (2)"),
]

VOICES = [
    "en-US-AndrewNeural", "en-US-BrianNeural", "en-US-GuyNeural", "en-US-ChristopherNeural",
    "en-US-EricNeural", "en-US-RogerNeural", "en-US-SteffanNeural", "en-US-AriaNeural",
    "en-US-JennyNeural", "en-US-MichelleNeural", "en-GB-RyanNeural", "en-GB-ThomasNeural",
    "en-GB-SoniaNeural", "en-GB-LibbyNeural", "en-AU-WilliamNeural", "en-AU-NatashaNeural",
    "en-IN-PrabhatNeural", "en-IN-NeerjaNeural",
]

STYLE = """
QWidget { background: @BG@; color: @TEXT@; font-family: "Consolas", "Cascadia Mono", "Segoe UI"; font-size: 13px; }
QMainWindow, QDialog { background: @BG@; }
QLabel { background: transparent; }
QLabel#muted { color: @MUTED@; }
QLabel#section { color: @NEON@; font-weight: bold; font-size: 12px; }
QFrame#panel { background: @PANEL@; border: 1px solid @BORDER@; border-radius: 10px; }
QTabWidget::pane { border: 1px solid @BORDER@; border-radius: 10px; background: @PANEL@; top: -1px; }
QTabBar::tab { background: @PANEL@; color: @MUTED@; padding: 10px 18px; border: 1px solid @BORDER@; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; font-weight: bold; }
QTabBar::tab:selected { color: @NEON@; background: @PANEL2@; border-color: @NEON@; }
QTabBar::tab:hover { color: @NEON@; }
QPlainTextEdit, QLineEdit { background: #040705; border: 1px solid @BORDER@; border-radius: 6px; padding: 6px; selection-background-color: @NEON_DIM@; selection-color: #001a0e; }
QPlainTextEdit:focus, QLineEdit:focus { border: 1px solid @NEON@; }
QPlainTextEdit#terminal { background: #020403; color: @NEON@; border: 1px solid @BORDER@; }
QComboBox, QSpinBox { background: #040705; border: 1px solid @BORDER@; border-radius: 6px; padding: 5px 8px; min-height: 22px; }
QComboBox:hover, QSpinBox:hover, QComboBox:focus, QSpinBox:focus { border-color: @NEON@; }
QComboBox QAbstractItemView { background: #040705; border: 1px solid @NEON@; selection-background-color: @NEON_DIM@; selection-color: #001a0e; }
QComboBox::drop-down { border: none; width: 22px; }
QCheckBox { spacing: 8px; background: transparent; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid @BORDER@; border-radius: 3px; background: #040705; }
QCheckBox::indicator:checked { background: @NEON@; border-color: @NEON@; }
QPushButton { background: #07150e; color: @NEON@; border: 1px solid @NEON_DIM@; border-radius: 8px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background: #0c2a1b; border-color: @NEON@; color: #eafff4; }
QPushButton:pressed { background: @NEON_DIM@; color: #001a0e; }
QPushButton:disabled { color: #2f5a47; border-color: #14382a; background: #060d09; }
QPushButton#create { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b36b, stop:1 #00ff9c); color: #00170d; border: none; font-size: 18px; padding: 14px 30px; border-radius: 10px; }
QPushButton#create:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d37f, stop:1 #5dffc0); color: #00170d; }
QPushButton#create:disabled { background: #123424; color: #3d7a5f; }
QPushButton#danger { color: @WARN@; border-color: #7a2036; }
QPushButton#danger:hover { border-color: @WARN@; background: #2a0c14; color: #ffd6de; }
QProgressBar { border: 1px solid @NEON_DIM@; border-radius: 8px; background: #030504; text-align: center; color: #eafff4; font-weight: bold; min-height: 28px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007a4a, stop:1 #00ff9c); border-radius: 7px; }
QListWidget, QTableWidget { background: #040705; border: 1px solid @BORDER@; border-radius: 6px; gridline-color: #0b2a1c; }
QListWidget::item { color: @TEXT@; border: 1px solid transparent; border-radius: 6px; padding: 4px; }
QListWidget::item:selected, QTableWidget::item:selected { background: #0c2a1b; color: @NEON@; border: 1px solid @NEON@; }
QHeaderView::section { background: @PANEL2@; color: @NEON@; border: none; border-bottom: 1px solid @BORDER@; padding: 6px; font-weight: bold; }
QScrollBar:vertical { background: #040705; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: @NEON_DIM@; border-radius: 5px; min-height: 28px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar:horizontal { background: #040705; height: 12px; }
QScrollBar::handle:horizontal { background: @NEON_DIM@; border-radius: 5px; min-width: 28px; }
QSlider::groove:horizontal { height: 6px; background: #0b2a1c; border-radius: 3px; }
QSlider::sub-page:horizontal { background: @NEON_DIM@; border-radius: 3px; }
QSlider::handle:horizontal { background: @NEON@; width: 16px; margin: -6px 0; border-radius: 8px; }
QToolTip { background: #040705; color: @NEON@; border: 1px solid @NEON@; padding: 4px; }
QMessageBox { background: @BG@; }
"""
for _k, _v in {
    "@BG@": BG, "@PANEL@": PANEL, "@PANEL2@": PANEL2, "@BORDER@": BORDER, "@NEON@": NEON,
    "@NEON_DIM@": NEON_DIM, "@TEXT@": TEXT, "@MUTED@": MUTED, "@WARN@": WARN,
}.items():
    STYLE = STYLE.replace(_k, _v)


def res_dir():
    return Path(__file__).resolve().parent


def user_dir():
    d = Path.home() / "ShortsCreator"
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_tool(name):
    for base in (res_dir() / "bin", res_dir(), Path(sys.argv[0]).resolve().parent / "bin"):
        for ext in (".exe", ""):
            p = base / (name + ext)
            if p.is_file():
                return str(p)
    return shutil.which(name)


def register_font(path):
    fid = QFontDatabase.addApplicationFont(str(path))
    if fid < 0:
        return None
    fams = QFontDatabase.applicationFontFamilies(fid)
    return fams[0] if fams else None


def scan_fonts():
    found, seen = [], set()
    for d in (res_dir() / "fonts", user_dir() / "fonts"):
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if p.suffix.lower() in FONT_EXT and str(p) not in seen:
                    fam = register_font(p)
                    if fam:
                        found.append((fam, str(p)))
                        seen.add(str(p))
    return found


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def fmt_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_color(hex_color):
    c = QColor(hex_color)
    return f"&H00{c.blue():02X}{c.green():02X}{c.red():02X}"


def estimate_words(text, duration):
    tokens = text.split()
    weights = [len(t) + 2 for t in tokens]
    total = sum(weights)
    words, t = [], 0.0
    for tok, w in zip(tokens, weights):
        d = duration * w / total
        words.append({"start": t, "end": t + d, "text": tok})
        t += d
    return words


def build_ass(cfg, words, total):
    fam = cfg["font_family"]
    size = cfg["font_size"]
    bold = -1 if cfg["bold"] else 0
    outline = max(4, round(size * 0.075))
    txt = ass_color(cfg["col_text"])
    hi = ass_color(cfg["col_hi"])
    out = ass_color(cfg["col_outline"])
    glow = ass_color(cfg["col_glow"])
    margin = cfg["margin"]
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Cap,{fam},{size},{hi},{txt},{out},&H80000000,{bold},0,0,0,100,100,1,0,1,{outline},3,2,80,80,{margin},1\n"
        f"Style: Glow,{fam},{size},{glow},{glow},{glow},&H00000000,{bold},0,0,0,100,100,1,0,1,{outline * 2},0,2,80,80,{margin},1\n"
        f"Style: Title,{fam},{cfg['title_size']},&H00FFFFFF,&H00FFFFFF,{out},&H80000000,{bold},0,0,0,100,100,1,0,1,5,2,8,60,60,200,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    lines = []
    title = cfg["title"].replace("{", "").replace("}", "").replace("\\", "").strip()
    if title:
        lines.append(f"Dialogue: 3,{fmt_time(0)},{fmt_time(total)},Title,,0,0,0,,{title}")
    pop = POP_TAG if cfg["pop"] else ""
    wpl = cfg["wpl"]
    groups = [words[i:i + wpl] for i in range(0, len(words), wpl)]
    for gi, group in enumerate(groups):
        start = group[0]["start"]
        last_end = group[-1]["end"]
        nxt = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else total
        end = min(nxt, last_end + 0.5)
        plain, karaoke = [], []
        for wi, w in enumerate(group):
            nstart = group[wi + 1]["start"] if wi + 1 < len(group) else end
            dur = max(1, round((nstart - w["start"]) * 100))
            clean = w["text"].replace("{", "").replace("}", "").replace("\\", "")
            if cfg["uppercase"]:
                clean = clean.upper()
            plain.append(clean)
            karaoke.append("{\\k" + str(dur) + "}" + clean)
        if cfg["glow"]:
            lines.append(f"Dialogue: 1,{fmt_time(start)},{fmt_time(end)},Glow,,0,0,0,,{pop}{GLOW_TAG}{' '.join(plain)}")
        lines.append(f"Dialogue: 2,{fmt_time(start)},{fmt_time(end)},Cap,,0,0,0,,{pop}{' '.join(karaoke)}")
    return header + "\n".join(lines) + "\n"


def plan_timeline(words, total, cues, images, even, log):
    items = []
    if not even:
        toks = [(norm(w["text"]), i) for i, w in enumerate(words)]
        toks = [t for t in toks if t[0]]
        cursor = 0
        points = []
        for phrase, img in cues:
            target = [x for x in (norm(p) for p in phrase.split()) if x]
            if not target or not img:
                continue
            n = len(target)
            hit = None
            for k in range(cursor, len(toks) - n + 1):
                if [t[0] for t in toks[k:k + n]] == target:
                    hit = k
                    break
            if hit is None:
                log(f"Cue not found in narration, skipped: {phrase!r}")
                continue
            points.append((words[toks[hit][1]]["start"], img))
            cursor = hit + n
        if points:
            points[0] = (0.0, points[0][1])
            for k, (t, img) in enumerate(points):
                end = points[k + 1][0] if k + 1 < len(points) else total
                items.append([img, max(0.4, end - t)])
    if not items:
        log("No usable cues, spreading images evenly")
        per = total / len(images)
        items = [[img, per] for img in images]
    s = sum(d for _, d in items)
    if s < total:
        items[-1][1] += total - s
    return items


class Cancelled(Exception):
    pass


class Worker(QThread):
    progress = Signal(int)
    status = Signal(str)
    log = Signal(str)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.proc = None
        self.stop_flag = False

    def cancel(self):
        self.stop_flag = True
        p = self.proc
        if p is not None and p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass

    def check(self):
        if self.stop_flag:
            raise Cancelled()

    def run(self):
        try:
            out = self.pipeline()
            self.done.emit(str(out))
        except Cancelled:
            self.failed.emit("CANCELLED")
        except Exception as e:
            self.log.emit(traceback.format_exc())
            self.failed.emit(str(e))

    def ffmpeg(self, args, cwd, duration=None, lo=0, hi=0):
        cmd = [self.cfg["ffmpeg"], "-y", "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1"] + args
        self.proc = subprocess.Popen(
            cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", creationflags=NO_WINDOW,
        )
        tail = []
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            key = line.split("=")[0]
            if key in ("out_time_us", "out_time_ms"):
                if duration:
                    try:
                        sec = int(line.split("=")[1]) / 1e6
                        frac = min(1.0, max(0.0, sec / duration))
                        self.progress.emit(int(lo + (hi - lo) * frac))
                    except ValueError:
                        pass
            elif key in PROGRESS_KEYS:
                continue
            else:
                tail.append(line)
                tail = tail[-12:]
        code = self.proc.wait()
        self.proc = None
        self.check()
        if code != 0:
            raise RuntimeError("FFmpeg failed:\n" + "\n".join(tail))

    def probe(self, path):
        r = subprocess.run(
            [self.cfg["ffmpeg"], "-hide_banner", "-i", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NO_WINDOW,
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", r.stderr)
        if not m:
            raise RuntimeError("Could not read audio duration")
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

    async def synth(self, text, path):
        cfg = self.cfg
        try:
            comm = edge_tts.Communicate(text, cfg["voice"], rate=cfg["rate"], boundary="WordBoundary")
        except TypeError:
            comm = edge_tts.Communicate(text, cfg["voice"], rate=cfg["rate"])
        words = []
        n_total = max(1, len(text.split()))
        with open(path, "wb") as f:
            async for chunk in comm.stream():
                if self.stop_flag:
                    raise Cancelled()
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    words.append({
                        "start": chunk["offset"] / 1e7,
                        "end": (chunk["offset"] + chunk["duration"]) / 1e7,
                        "text": chunk["text"],
                    })
                    self.progress.emit(2 + int(12 * min(1.0, len(words) / n_total)))
        return words

    def make_segment(self, i, img, dur, work, lo, hi):
        cfg = self.cfg
        W, H, FPS = cfg["w"], cfg["h"], cfg["fps"]
        CW, CH = int(W * 1.5), int(H * 1.5)
        frames = max(1, round(dur * FPS))
        if cfg["blur_fit"]:
            sw, sh = CW // 6, CH // 6
            graph = (
                "[0:v]split[a][b];"
                f"[a]scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},scale={sw}:{sh},boxblur=8:2,scale={CW}:{CH}[bg];"
                f"[b]scale={CW}:{CH}:force_original_aspect_ratio=decrease[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1"
            )
        else:
            graph = f"[0:v]scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},setsar=1"
        if cfg["zoom"]:
            z = f"1+0.15*on/{frames}" if i % 2 == 0 else f"1.15-0.15*on/{frames}"
            graph += (
                f",zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
                "format=yuv420p[v]"
            )
            pre = []
        else:
            graph += f",scale={W}:{H},format=yuv420p[v]"
            pre = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}"]
        out = work / "tmp" / f"seg{i:03d}.mp4"
        args = pre + [
            "-i", str(img), "-filter_complex", graph, "-map", "[v]", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(out),
        ]
        self.ffmpeg(args, work, duration=dur, lo=lo, hi=hi)
        return out

    def pipeline(self):
        cfg = self.cfg
        out_dir = Path(cfg["out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="shorts_"))
        try:
            (work / "tmp").mkdir()
            (work / "fonts").mkdir()
            for f in cfg["font_files"]:
                try:
                    shutil.copy2(f, work / "fonts" / Path(f).name)
                except Exception:
                    pass

            self.status.emit("[1/5] GENERATING AI VOICEOVER")
            self.progress.emit(2)
            text = " ".join(cfg["text"].split())
            audio = work / "voice.mp3"
            self.log.emit(f"Voice: {cfg['voice']}  rate: {cfg['rate']}")
            try:
                words = asyncio.run(self.synth(text, audio))
            except Cancelled:
                raise
            except Exception as e:
                raise RuntimeError(f"Voice generation failed. Check your internet connection and voice name.\n{e}")
            self.check()
            if not audio.exists() or audio.stat().st_size < 2000:
                raise RuntimeError("Voice engine returned no audio. Check your internet connection and voice name.")
            dur = self.probe(audio)
            if not words:
                self.log.emit("No word timing received, estimating caption timing")
                words = estimate_words(text, dur)
            total = dur + 0.6
            self.log.emit(f"Voiceover length: {dur:.1f}s  ({len(words)} words)")
            self.progress.emit(15)

            self.status.emit("[2/5] BUILDING CAPTIONS")
            (work / "captions.ass").write_text(build_ass(cfg, words, total), encoding="utf-8")
            self.progress.emit(17)
            self.check()

            self.status.emit("[3/5] PLANNING SCENES")
            images = [p for p in cfg["images"] if Path(p).is_file()]
            cues = [(ph, p) for ph, p in cfg["cues"] if p and Path(p).is_file()]
            if not images:
                images = [p for _, p in cues]
            if not images:
                raise RuntimeError("No valid images found")
            items = plan_timeline(words, total, cues, images, cfg["even"], self.log.emit)
            for img, d in items:
                self.log.emit(f"  {d:5.1f}s  {Path(img).name}")
            self.progress.emit(18)

            segs = []
            n = len(items)
            for i, (img, d) in enumerate(items):
                self.check()
                self.status.emit(f"[4/5] RENDERING SCENE {i + 1}/{n}")
                lo = 18 + 52 * i / n
                hi = 18 + 52 * (i + 1) / n
                segs.append(self.make_segment(i, img, d, work, lo, hi))
            self.progress.emit(70)

            (work / "list.txt").write_text("\n".join(f"file 'tmp/{s.name}'" for s in segs) + "\n", encoding="utf-8")

            self.status.emit("[5/5] ENCODING FINAL VIDEO")
            args = ["-f", "concat", "-safe", "0", "-i", "list.txt", "-i", "voice.mp3"]
            graph = "[0:v]ass=captions.ass:fontsdir=fonts[v];"
            music = cfg["music"]
            if music and Path(music).is_file():
                args += ["-stream_loop", "-1", "-i", music]
                vol = cfg["music_vol"] / 100
                graph += (
                    "[1:a]aresample=48000[va];"
                    f"[2:a]aresample=48000,volume={vol:.2f}[ma];"
                    "[va][ma]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]"
                )
                self.log.emit(f"Background music mixed at {cfg['music_vol']}%")
            else:
                graph += "[1:a]aresample=48000[a]"
            args += [
                "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", cfg["preset"], "-crf", str(cfg["crf"]), "-pix_fmt", "yuv420p",
                "-r", str(cfg["fps"]), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "-t", f"{total:.2f}", "short.mp4",
            ]
            self.ffmpeg(args, work, duration=total, lo=70, hi=99)

            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final = out_dir / f"short_{stamp}.mp4"
            shutil.move(str(work / "short.mp4"), str(final))
            if cfg["save_mp3"]:
                shutil.copy2(audio, out_dir / f"voice_{stamp}.mp3")
            self.progress.emit(100)
            self.status.emit("COMPLETE")
            return final
        finally:
            shutil.rmtree(work, ignore_errors=True)


class GlowButton(QPushButton):
    def __init__(self, text, color=NEON, base=10, peak=32, hover=True, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.base = base
        self.peak = peak
        self.hover = hover
        self.fx = QGraphicsDropShadowEffect(self)
        self.fx.setOffset(0, 0)
        self.fx.setColor(QColor(color))
        self.fx.setBlurRadius(base)
        self.setGraphicsEffect(self.fx)
        self.anim = QPropertyAnimation(self.fx, b"blurRadius", self)
        self.anim.setDuration(180)

    def go(self, value):
        self.anim.stop()
        self.anim.setStartValue(self.fx.blurRadius())
        self.anim.setEndValue(value)
        self.anim.start()

    def enterEvent(self, e):
        if self.hover:
            self.go(self.peak)
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self.hover:
            self.go(self.base)
        super().leaveEvent(e)

    def changeEvent(self, e):
        if e.type() == QEvent.EnabledChange:
            self.fx.setEnabled(self.isEnabled())
        super().changeEvent(e)


class ColorButton(QPushButton):
    changed = Signal()

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(130)
        self.color = "#ffffff"
        self.set_color(color)
        self.clicked.connect(self.pick)

    def set_color(self, color):
        self.color = QColor(color).name()
        fg = "#000000" if QColor(self.color).lightness() > 128 else "#ffffff"
        self.setText(self.color.upper())
        self.setStyleSheet(
            f"QPushButton {{ background: {self.color}; color: {fg}; border: 1px solid {NEON}; "
            f"border-radius: 6px; padding: 6px; }}"
        )

    def pick(self):
        c = QColorDialog.getColor(QColor(self.color), self, "Pick color")
        if c.isValid():
            self.set_color(c.name())
            self.changed.emit()


class CreditsDialog(QDialog):
    def __init__(self, parent, title_family):
        super().__init__(parent)
        self.setWindowTitle("Credits")
        self.setModal(True)
        self.setFixedSize(540, 440)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 26, 30, 24)
        lay.setSpacing(14)

        t = QLabel(APP_NAME)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet(f"color: {NEON}; font-family: '{title_family}'; font-size: 40px;")
        fx = QGraphicsDropShadowEffect(t)
        fx.setColor(QColor(NEON))
        fx.setBlurRadius(26)
        fx.setOffset(0, 0)
        t.setGraphicsEffect(fx)
        lay.addWidget(t)

        v = QLabel(f"VERSION {APP_VERSION}")
        v.setAlignment(Qt.AlignCenter)
        v.setObjectName("muted")
        lay.addWidget(v)

        by = QLabel(f"Designed & developed by  <b style='color:{NEON}'>{AUTHOR}</b>")
        by.setAlignment(Qt.AlignCenter)
        lay.addWidget(by)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        lay.addWidget(sep)

        yt = GlowButton("▶   YOUTUBE   //   youtube.com/@YashvirGaming", color="#ff3b5c", base=10, peak=34)
        yt.setStyleSheet("QPushButton { color: #ff6b84; border: 1px solid #a0243d; padding: 14px; font-size: 14px; } "
                         "QPushButton:hover { background: #2a0c14; border-color: #ff3b5c; color: #ffd6de; }")
        yt.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(YOUTUBE_URL)))
        lay.addWidget(yt)

        gh = GlowButton("⌥   GITHUB   //   github.com/YashvirGaming", color=NEON, base=10, peak=34)
        gh.setStyleSheet("QPushButton { padding: 14px; font-size: 14px; }")
        gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        lay.addWidget(gh)

        pw = QLabel("Powered by PySide6  •  edge-tts  •  FFmpeg  •  Nuitka")
        pw.setAlignment(Qt.AlignCenter)
        pw.setObjectName("muted")
        lay.addStretch(1)
        lay.addWidget(pw)

        close = GlowButton("CLOSE")
        close.clicked.connect(self.accept)
        lay.addWidget(close)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} By {AUTHOR}")
        self.resize(1320, 880)
        self.setMinimumSize(1120, 780)
        self.setAcceptDrops(True)
        self.worker = None
        self.icons = {}
        self.last_output = ""
        self.t0 = 0.0
        self.fonts = scan_fonts()
        self.title_family = next((f for f, _ in self.fonts if "bebas" in f.lower()), "Consolas")
        self.ffmpeg_path = find_tool("ffmpeg")
        self.build_ui()
        self.load_state()
        self.update_script_stats()
        self.log("system online")
        self.log(f"ffmpeg: {self.ffmpeg_path or 'NOT FOUND'}")
        self.log(f"fonts loaded: {len(self.fonts)}")

    def section(self, text):
        l = QLabel(text)
        l.setObjectName("section")
        return l

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(18, 16, 18, 14)
        main.setSpacing(12)

        main.addWidget(self.build_header())

        mid = QHBoxLayout()
        mid.setSpacing(12)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab_script(), "01 // SCRIPT")
        self.tabs.addTab(self.tab_scenes(), "02 // SCENES")
        self.tabs.addTab(self.tab_style(), "03 // CAPTIONS")
        self.tabs.addTab(self.tab_export(), "04 // EXPORT")
        mid.addWidget(self.tabs, 3)
        mid.addWidget(self.build_terminal(), 2)
        main.addLayout(mid, 1)

        main.addWidget(self.build_bottom())

    def build_header(self):
        f = QFrame()
        f.setObjectName("panel")
        lay = QHBoxLayout(f)
        lay.setContentsMargins(24, 14, 24, 14)
        box = QVBoxLayout()
        box.setSpacing(0)
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"color: {NEON}; font-family: '{self.title_family}'; font-size: 46px;")
        fx = QGraphicsDropShadowEffect(title)
        fx.setColor(QColor(NEON))
        fx.setBlurRadius(30)
        fx.setOffset(0, 0)
        title.setGraphicsEffect(fx)
        sub = QLabel(f"v{APP_VERSION}   //   By {AUTHOR}")
        sub.setObjectName("muted")
        box.addWidget(title)
        box.addWidget(sub)
        lay.addLayout(box)
        lay.addStretch(1)
        self.ff_lbl = QLabel("FFMPEG: READY" if self.ffmpeg_path else "FFMPEG: MISSING")
        self.ff_lbl.setStyleSheet(f"color: {NEON if self.ffmpeg_path else WARN}; font-weight: bold;")
        lay.addWidget(self.ff_lbl)
        lay.addSpacing(18)
        cb = GlowButton("★  CREDITS")
        cb.clicked.connect(self.show_credits)
        lay.addWidget(cb)
        return f

    def tab_script(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        lay.addWidget(self.section("NARRATION SCRIPT  (ENGLISH)"))
        self.script_edit = QPlainTextEdit()
        self.script_edit.setPlainText(DEFAULT_SCRIPT)
        lay.addWidget(self.script_edit, 1)
        self.stats_lbl = QLabel()
        lay.addWidget(self.stats_lbl)

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        self.voice_combo = QComboBox()
        self.voice_combo.setEditable(True)
        self.voice_combo.addItems(VOICES)
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(-50, 100)
        self.speed_spin.setSingleStep(5)
        self.speed_spin.setValue(10)
        self.speed_spin.setSuffix(" %")
        form.addRow("VOICE", self.voice_combo)
        form.addRow("SPEED", self.speed_spin)
        lay.addLayout(form)
        self.script_edit.textChanged.connect(self.update_script_stats)
        self.speed_spin.valueChanged.connect(self.update_script_stats)
        return page

    def tab_scenes(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(8)

        head = QHBoxLayout()
        head.addWidget(self.section("IMAGE LIBRARY  (drag & drop pictures onto the window)"))
        head.addStretch(1)
        for text, fn in (("ADD IMAGES", self.pick_images), ("REMOVE", self.remove_images),
                         ("CLEAR", self.clear_images), ("◀", lambda: self.move_image(-1)),
                         ("▶", lambda: self.move_image(1))):
            b = QPushButton(text)
            b.clicked.connect(fn)
            head.addWidget(b)
        lay.addLayout(head)

        self.img_list = QListWidget()
        self.img_list.setViewMode(QListView.IconMode)
        self.img_list.setIconSize(QSize(96, 96))
        self.img_list.setGridSize(QSize(128, 132))
        self.img_list.setResizeMode(QListView.Adjust)
        self.img_list.setMovement(QListView.Static)
        self.img_list.setWordWrap(True)
        self.img_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.img_list.setFixedHeight(190)
        lay.addWidget(self.img_list)

        row = QHBoxLayout()
        row.addWidget(self.section("SCENE MODE"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Match narration cues (recommended)", "Spread images evenly (in list order)"])
        row.addWidget(self.mode_combo, 1)
        lay.addLayout(row)

        lay.addWidget(self.section("CUES  -  the picture switches when the narration reaches the phrase"))
        self.cue_table = QTableWidget(0, 2)
        self.cue_table.setHorizontalHeaderLabels(["WHEN NARRATION SAYS...", "SHOW THIS IMAGE"])
        self.cue_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.cue_table.setColumnWidth(1, 300)
        self.cue_table.setSelectionBehavior(QTableWidget.SelectRows)
        lay.addWidget(self.cue_table, 1)

        btns = QHBoxLayout()
        for text, fn in (("ADD CUE", lambda: self.add_cue_row()), ("REMOVE CUE", self.remove_cue_row),
                         ("AUTO-FILL IMAGES", lambda: self.autofill(True))):
            b = QPushButton(text)
            b.clicked.connect(fn)
            btns.addWidget(b)
        btns.addStretch(1)
        lay.addLayout(btns)

        for ph, key in DEFAULT_CUES:
            self.add_cue_row(ph, key)
        return page

    def tab_style(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(12)

        frow = QHBoxLayout()
        self.font_combo = QComboBox()
        for fam, p in self.fonts:
            self.font_combo.addItem(fam, p)
        if not self.fonts:
            self.font_combo.addItem("Arial", "")
        fb = QPushButton("ADD FONT")
        fb.clicked.connect(self.add_font)
        frow.addWidget(self.font_combo, 1)
        frow.addWidget(fb)
        form.addRow("FONT", frow)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(40, 260)
        self.size_spin.setValue(120)
        form.addRow("FONT SIZE", self.size_spin)

        self.wpl_spin = QSpinBox()
        self.wpl_spin.setRange(1, 5)
        self.wpl_spin.setValue(2)
        form.addRow("WORDS PER LINE", self.wpl_spin)

        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(60, 1200)
        self.margin_spin.setSingleStep(20)
        self.margin_spin.setValue(560)
        form.addRow("HEIGHT FROM BOTTOM", self.margin_spin)

        self.col_text = ColorButton("#ffffff")
        self.col_hi = ColorButton("#fff200")
        self.col_outline = ColorButton("#000000")
        self.col_glow = ColorButton("#00ffff")
        form.addRow("TEXT COLOR", self.col_text)
        form.addRow("HIGHLIGHT COLOR", self.col_hi)
        form.addRow("OUTLINE COLOR", self.col_outline)

        grow = QHBoxLayout()
        self.glow_chk = QCheckBox("NEON GLOW")
        grow.addWidget(self.glow_chk)
        grow.addWidget(self.col_glow)
        grow.addStretch(1)
        form.addRow("GLOW", grow)

        self.pop_chk = QCheckBox("POP-IN ANIMATION PER LINE")
        self.pop_chk.setChecked(True)
        self.upper_chk = QCheckBox("UPPERCASE")
        self.upper_chk.setChecked(True)
        self.bold_chk = QCheckBox("BOLD")
        orow = QHBoxLayout()
        orow.addWidget(self.pop_chk)
        orow.addWidget(self.upper_chk)
        orow.addWidget(self.bold_chk)
        orow.addStretch(1)
        form.addRow("OPTIONS", orow)

        self.title_edit = QLineEdit("youtube.com/@YashvirGaming")
        self.title_edit.setPlaceholderText("Top text (leave empty for none)")
        form.addRow("TOP TEXT", self.title_edit)
        self.title_size = QSpinBox()
        self.title_size.setRange(20, 140)
        self.title_size.setValue(54)
        form.addRow("TOP TEXT SIZE", self.title_size)

        lay.addLayout(form)
        lay.addStretch(1)
        return page

    def tab_export(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(12)

        self.res_combo = QComboBox()
        self.res_combo.addItem("1080 x 1920  (Full HD)", (1080, 1920))
        self.res_combo.addItem("720 x 1280  (Faster)", (720, 1280))
        form.addRow("RESOLUTION", self.res_combo)

        self.fps_combo = QComboBox()
        for v in (24, 30, 60):
            self.fps_combo.addItem(f"{v} FPS", v)
        self.fps_combo.setCurrentIndex(1)
        form.addRow("FRAME RATE", self.fps_combo)

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Fast", ("veryfast", 23))
        self.quality_combo.addItem("Balanced", ("medium", 20))
        self.quality_combo.addItem("High quality", ("slow", 17))
        self.quality_combo.setCurrentIndex(1)
        form.addRow("QUALITY", self.quality_combo)

        self.zoom_chk = QCheckBox("SLOW ZOOM (KEN BURNS) ON IMAGES")
        self.zoom_chk.setChecked(True)
        self.blur_chk = QCheckBox("BLURRED BACKGROUND (FIT WHOLE IMAGE)")
        self.blur_chk.setChecked(True)
        form.addRow("MOTION", self.zoom_chk)
        form.addRow("FRAMING", self.blur_chk)

        mrow = QHBoxLayout()
        self.music_edit = QLineEdit()
        self.music_edit.setPlaceholderText("Optional background music (mp3 / wav)")
        mb = QPushButton("BROWSE")
        mb.clicked.connect(self.pick_music)
        mc = QPushButton("CLEAR")
        mc.clicked.connect(lambda: self.music_edit.clear())
        mrow.addWidget(self.music_edit, 1)
        mrow.addWidget(mb)
        mrow.addWidget(mc)
        form.addRow("MUSIC", mrow)

        vrow = QHBoxLayout()
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(12)
        self.music_lbl = QLabel("12%")
        self.music_lbl.setFixedWidth(46)
        self.music_slider.valueChanged.connect(lambda v: self.music_lbl.setText(f"{v}%"))
        vrow.addWidget(self.music_slider, 1)
        vrow.addWidget(self.music_lbl)
        form.addRow("MUSIC VOLUME", vrow)

        orow = QHBoxLayout()
        self.out_edit = QLineEdit(str(user_dir() / "output"))
        ob = QPushButton("BROWSE")
        ob.clicked.connect(self.pick_outdir)
        oo = QPushButton("OPEN")
        oo.clicked.connect(self.open_output_folder)
        orow.addWidget(self.out_edit, 1)
        orow.addWidget(ob)
        orow.addWidget(oo)
        form.addRow("OUTPUT FOLDER", orow)

        self.mp3_chk = QCheckBox("ALSO SAVE THE VOICEOVER AS MP3")
        form.addRow("EXTRAS", self.mp3_chk)

        lay.addLayout(form)
        lay.addStretch(1)
        return page

    def build_terminal(self):
        f = QFrame()
        f.setObjectName("panel")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.addWidget(self.section("// LIVE TERMINAL"))
        self.term = QPlainTextEdit()
        self.term.setObjectName("terminal")
        self.term.setReadOnly(True)
        lay.addWidget(self.term, 1)
        return f

    def build_bottom(self):
        f = QFrame()
        f.setObjectName("panel")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        srow = QHBoxLayout()
        self.status_lbl = QLabel("IDLE  //  READY TO CREATE")
        self.status_lbl.setStyleSheet(f"color: {NEON}; font-weight: bold;")
        self.elapsed_lbl = QLabel("00:00")
        self.elapsed_lbl.setObjectName("muted")
        srow.addWidget(self.status_lbl, 1)
        srow.addWidget(self.elapsed_lbl)
        lay.addLayout(srow)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFormat("%p%")
        lay.addWidget(self.bar)
        self.bar_anim = QPropertyAnimation(self.bar, b"value", self)
        self.bar_anim.setDuration(260)

        brow = QHBoxLayout()
        brow.setSpacing(12)
        self.btn_create = GlowButton("⚡  CREATE SHORTS", base=8, peak=36, hover=False)
        self.btn_create.setObjectName("create")
        self.btn_create.clicked.connect(self.start)
        self.btn_cancel = GlowButton("CANCEL", color=WARN)
        self.btn_cancel.setObjectName("danger")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_open = GlowButton("OPEN OUTPUT FOLDER")
        self.btn_open.clicked.connect(self.open_output_folder)
        brow.addWidget(self.btn_create, 3)
        brow.addWidget(self.btn_cancel, 1)
        brow.addWidget(self.btn_open, 1)
        lay.addLayout(brow)

        self.pulse = QPropertyAnimation(self.btn_create.fx, b"blurRadius", self)
        self.pulse.setDuration(1700)
        self.pulse.setLoopCount(-1)
        self.pulse.setKeyValueAt(0, 8)
        self.pulse.setKeyValueAt(0.5, 38)
        self.pulse.setKeyValueAt(1, 8)
        self.pulse.start()

        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.tick)

        foot = QLabel(f"{APP_NAME} v{APP_VERSION}  •  By {AUTHOR}")
        foot.setObjectName("muted")
        foot.setAlignment(Qt.AlignCenter)
        lay.addWidget(foot)
        return f

    def log(self, msg):
        stamp = datetime.now().strftime("%H:%M:%S")
        for line in str(msg).splitlines() or [""]:
            self.term.appendPlainText(f"[{stamp}] {line}")
        self.term.verticalScrollBar().setValue(self.term.verticalScrollBar().maximum())

    def tick(self):
        s = int(time.time() - self.t0)
        self.elapsed_lbl.setText(f"{s // 60:02d}:{s % 60:02d}")

    def update_script_stats(self):
        n = len(self.script_edit.toPlainText().split())
        rate = self.speed_spin.value()
        wps = 2.5 * (1 + rate / 100)
        est = n / wps if wps > 0 else 0
        color = NEON if est <= 60 else ("#ffd24d" if est <= 175 else WARN)
        self.stats_lbl.setText(f"WORDS: {n}   //   EST. LENGTH: ~{est:.0f}s")
        self.stats_lbl.setStyleSheet(f"color: {color}; font-weight: bold;")

    def thumb(self, path):
        ic = self.icons.get(path)
        if ic is None:
            pm = QPixmap(path)
            if pm.isNull():
                pm = QPixmap(64, 64)
                pm.fill(QColor("#123424"))
            ic = QIcon(pm.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.icons[path] = ic
        return ic

    def image_paths(self):
        return [self.img_list.item(i).data(Qt.UserRole) for i in range(self.img_list.count())]

    def pick_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select images", str(Path.home()),
                                                "Images (*.jpg *.jpeg *.png *.webp *.bmp)")
        self.add_images(files)

    def add_images(self, paths):
        have = set(self.image_paths())
        added = 0
        for p in paths:
            p = str(Path(p))
            if p in have or not Path(p).is_file():
                continue
            name = Path(p).name
            short = name if len(name) <= 18 else name[:15] + "..."
            it = QListWidgetItem(self.thumb(p), short)
            it.setData(Qt.UserRole, p)
            it.setToolTip(p)
            self.img_list.addItem(it)
            have.add(p)
            added += 1
        if added:
            self.refresh_combos()
            self.autofill(False)
            self.log(f"{added} image(s) added")

    def remove_images(self):
        for it in self.img_list.selectedItems():
            self.img_list.takeItem(self.img_list.row(it))
        self.refresh_combos()

    def clear_images(self):
        self.img_list.clear()
        self.refresh_combos()

    def move_image(self, delta):
        rows = sorted(self.img_list.row(i) for i in self.img_list.selectedItems())
        if len(rows) != 1:
            return
        r = rows[0]
        nr = r + delta
        if nr < 0 or nr >= self.img_list.count():
            return
        it = self.img_list.takeItem(r)
        self.img_list.insertItem(nr, it)
        self.img_list.setCurrentItem(it)

    def fill_combo(self, combo):
        for p in self.image_paths():
            combo.addItem(self.thumb(p), Path(p).name, p)

    def refresh_combos(self):
        for r in range(self.cue_table.rowCount()):
            combo = self.cue_table.cellWidget(r, 1)
            cur = combo.currentData()
            combo.clear()
            self.fill_combo(combo)
            combo.setCurrentIndex(combo.findData(cur) if cur else -1)

    def add_cue_row(self, phrase="", key="", path=""):
        r = self.cue_table.rowCount()
        self.cue_table.insertRow(r)
        it = QTableWidgetItem(phrase)
        it.setData(Qt.UserRole, key)
        self.cue_table.setItem(r, 0, it)
        combo = QComboBox()
        combo.setIconSize(QSize(34, 34))
        self.fill_combo(combo)
        self.cue_table.setCellWidget(r, 1, combo)
        self.cue_table.setRowHeight(r, 46)
        combo.setCurrentIndex(combo.findData(path) if path else -1)

    def remove_cue_row(self):
        rows = sorted({i.row() for i in self.cue_table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.cue_table.removeRow(r)

    def autofill(self, force):
        imgs = self.image_paths()
        if not imgs:
            return
        used = set()
        if not force:
            for r in range(self.cue_table.rowCount()):
                p = self.cue_table.cellWidget(r, 1).currentData()
                if p:
                    used.add(p)
        for r in range(self.cue_table.rowCount()):
            combo = self.cue_table.cellWidget(r, 1)
            if not force and combo.currentIndex() >= 0:
                continue
            key = (self.cue_table.item(r, 0).data(Qt.UserRole) or "").lower()
            pick = None
            if key:
                for p in imgs:
                    if key in Path(p).stem.lower():
                        pick = p
                        break
            if pick is None:
                for p in imgs:
                    if p not in used:
                        pick = p
                        break
            if pick is None:
                pick = imgs[r % len(imgs)]
            used.add(pick)
            combo.setCurrentIndex(combo.findData(pick))

    def cue_pairs(self):
        out = []
        for r in range(self.cue_table.rowCount()):
            ph = (self.cue_table.item(r, 0).text() if self.cue_table.item(r, 0) else "").strip()
            out.append((ph, self.cue_table.cellWidget(r, 1).currentData() or ""))
        return out

    def add_font(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select font files", str(Path.home()), "Fonts (*.ttf *.otf)")
        for f in files:
            dest_dir = user_dir() / "fonts"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / Path(f).name
            try:
                shutil.copy2(f, dest)
            except Exception:
                continue
            fam = register_font(dest)
            if fam:
                self.fonts.append((fam, str(dest)))
                self.font_combo.addItem(fam, str(dest))
                self.font_combo.setCurrentIndex(self.font_combo.count() - 1)
                self.log(f"font added: {fam}")

    def pick_music(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select music", str(Path.home()), "Audio (*.mp3 *.wav *.m4a *.ogg *.flac)")
        if f:
            self.music_edit.setText(f)

    def pick_outdir(self):
        d = QFileDialog.getExistingDirectory(self, "Select output folder", self.out_edit.text())
        if d:
            self.out_edit.setText(d)

    def open_output_folder(self):
        d = Path(self.out_edit.text())
        d.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))

    def show_credits(self):
        CreditsDialog(self, self.title_family).exec()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        paths = [u.toLocalFile() for u in e.mimeData().urls()]
        self.add_images([p for p in paths if Path(p).suffix.lower() in IMG_EXT])
        self.tabs.setCurrentIndex(1)

    def collect(self):
        if edge_tts is None:
            QMessageBox.critical(self, "Missing module", "The edge-tts module is not installed.\n\npip install edge-tts")
            return None
        if not self.ffmpeg_path:
            QMessageBox.critical(self, "FFmpeg missing", "ffmpeg.exe was not found.\nPut ffmpeg.exe inside the 'bin' folder next to the app.")
            return None
        text = self.script_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No script", "Write or paste the narration script first.")
            self.tabs.setCurrentIndex(0)
            return None
        images = self.image_paths()
        cues = self.cue_pairs()
        if not images:
            QMessageBox.warning(self, "No images", "Add at least one image in the SCENES tab.")
            self.tabs.setCurrentIndex(1)
            return None
        w, h = self.res_combo.currentData()
        preset, crf = self.quality_combo.currentData()
        fi = self.font_combo.currentIndex()
        return {
            "ffmpeg": self.ffmpeg_path,
            "text": text,
            "voice": self.voice_combo.currentText().strip() or VOICES[0],
            "rate": f"{self.speed_spin.value():+d}%",
            "w": w, "h": h, "fps": self.fps_combo.currentData(),
            "preset": preset, "crf": crf,
            "zoom": self.zoom_chk.isChecked(), "blur_fit": self.blur_chk.isChecked(),
            "even": self.mode_combo.currentIndex() == 1,
            "images": images, "cues": cues,
            "font_family": self.font_combo.currentText() or "Arial",
            "font_files": [p for _, p in self.fonts],
            "font_size": self.size_spin.value(), "bold": self.bold_chk.isChecked(),
            "uppercase": self.upper_chk.isChecked(), "wpl": self.wpl_spin.value(),
            "margin": self.margin_spin.value(),
            "col_text": self.col_text.color, "col_hi": self.col_hi.color,
            "col_outline": self.col_outline.color, "col_glow": self.col_glow.color,
            "glow": self.glow_chk.isChecked(), "pop": self.pop_chk.isChecked(),
            "title": self.title_edit.text(), "title_size": self.title_size.value(),
            "music": self.music_edit.text().strip(), "music_vol": self.music_slider.value(),
            "out_dir": self.out_edit.text().strip() or str(user_dir() / "output"),
            "save_mp3": self.mp3_chk.isChecked(),
        }

    def set_progress(self, v):
        self.bar_anim.stop()
        self.bar_anim.setStartValue(self.bar.value())
        self.bar_anim.setEndValue(int(v))
        self.bar_anim.start()

    def set_running(self, running):
        self.btn_create.setEnabled(not running)
        self.btn_cancel.setEnabled(running)
        self.tabs.setEnabled(not running)
        if running:
            self.pulse.stop()
            self.t0 = time.time()
            self.timer.start()
        else:
            self.timer.stop()
            self.pulse.start()

    def start(self):
        cfg = self.collect()
        if cfg is None:
            return
        self.save_state()
        self.bar_anim.stop()
        self.bar.setValue(0)
        self.elapsed_lbl.setText("00:00")
        self.log("=" * 40)
        self.log("job started")
        self.set_running(True)
        self.worker = Worker(cfg)
        self.worker.progress.connect(self.set_progress)
        self.worker.status.connect(self.on_status)
        self.worker.log.connect(self.log)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def cancel(self):
        if self.worker:
            self.log("cancelling...")
            self.worker.cancel()

    def on_status(self, s):
        self.status_lbl.setText(s)
        self.status_lbl.setStyleSheet(f"color: {NEON}; font-weight: bold;")
        self.log(s)

    def on_done(self, path):
        self.last_output = path
        self.set_progress(100)
        self.status_lbl.setText("COMPLETE  //  100%")
        self.log(f"saved: {path}")
        self.set_running(False)
        box = QMessageBox(self)
        box.setWindowTitle("DONE")
        box.setText(f"Your Short is ready.\n\n{path}")
        b1 = box.addButton("PLAY VIDEO", QMessageBox.ActionRole)
        b2 = box.addButton("OPEN FOLDER", QMessageBox.ActionRole)
        box.addButton("CLOSE", QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() == b1:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        elif box.clickedButton() == b2:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))

    def on_failed(self, msg):
        self.set_running(False)
        self.bar_anim.stop()
        self.bar.setValue(0)
        if msg == "CANCELLED":
            self.status_lbl.setText("CANCELLED")
            self.status_lbl.setStyleSheet(f"color: {WARN}; font-weight: bold;")
            self.log("job cancelled")
            return
        self.status_lbl.setText("FAILED")
        self.status_lbl.setStyleSheet(f"color: {WARN}; font-weight: bold;")
        self.log(f"ERROR: {msg}")
        QMessageBox.critical(self, "Error", msg[:1200])

    def state_file(self):
        return user_dir() / "settings.json"

    def save_state(self):
        try:
            d = {
                "script": self.script_edit.toPlainText(),
                "voice": self.voice_combo.currentText(),
                "speed": self.speed_spin.value(),
                "images": self.image_paths(),
                "mode": self.mode_combo.currentIndex(),
                "cues": [
                    {"phrase": (self.cue_table.item(r, 0).text() if self.cue_table.item(r, 0) else ""),
                     "key": self.cue_table.item(r, 0).data(Qt.UserRole) if self.cue_table.item(r, 0) else "",
                     "path": self.cue_table.cellWidget(r, 1).currentData() or ""}
                    for r in range(self.cue_table.rowCount())
                ],
                "font": self.font_combo.currentText(),
                "size": self.size_spin.value(), "wpl": self.wpl_spin.value(), "margin": self.margin_spin.value(),
                "col_text": self.col_text.color, "col_hi": self.col_hi.color,
                "col_outline": self.col_outline.color, "col_glow": self.col_glow.color,
                "glow": self.glow_chk.isChecked(), "pop": self.pop_chk.isChecked(),
                "upper": self.upper_chk.isChecked(), "bold": self.bold_chk.isChecked(),
                "title": self.title_edit.text(), "title_size": self.title_size.value(),
                "res": self.res_combo.currentIndex(), "fps": self.fps_combo.currentIndex(),
                "quality": self.quality_combo.currentIndex(),
                "zoom": self.zoom_chk.isChecked(), "blur": self.blur_chk.isChecked(),
                "music": self.music_edit.text(), "music_vol": self.music_slider.value(),
                "out": self.out_edit.text(), "mp3": self.mp3_chk.isChecked(),
            }
            self.state_file().write_text(json.dumps(d, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_state(self):
        f = self.state_file()
        if not f.is_file():
            return
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return
        try:
            self.script_edit.setPlainText(d.get("script", DEFAULT_SCRIPT))
            self.voice_combo.setCurrentText(d.get("voice", VOICES[0]))
            self.speed_spin.setValue(d.get("speed", 10))
            self.img_list.clear()
            for p in d.get("images", []):
                if Path(p).is_file():
                    name = Path(p).name
                    short = name if len(name) <= 18 else name[:15] + "..."
                    it = QListWidgetItem(self.thumb(p), short)
                    it.setData(Qt.UserRole, p)
                    it.setToolTip(p)
                    self.img_list.addItem(it)
            self.cue_table.setRowCount(0)
            cues = d.get("cues")
            if cues:
                for c in cues:
                    path = c.get("path", "")
                    self.add_cue_row(c.get("phrase", ""), c.get("key", ""), path if Path(path).is_file() else "")
            else:
                for ph, key in DEFAULT_CUES:
                    self.add_cue_row(ph, key)
            self.mode_combo.setCurrentIndex(d.get("mode", 0))
            i = self.font_combo.findText(d.get("font", ""))
            if i >= 0:
                self.font_combo.setCurrentIndex(i)
            self.size_spin.setValue(d.get("size", 120))
            self.wpl_spin.setValue(d.get("wpl", 2))
            self.margin_spin.setValue(d.get("margin", 560))
            self.col_text.set_color(d.get("col_text", "#ffffff"))
            self.col_hi.set_color(d.get("col_hi", "#fff200"))
            self.col_outline.set_color(d.get("col_outline", "#000000"))
            self.col_glow.set_color(d.get("col_glow", "#00ffff"))
            self.glow_chk.setChecked(d.get("glow", False))
            self.pop_chk.setChecked(d.get("pop", True))
            self.upper_chk.setChecked(d.get("upper", True))
            self.bold_chk.setChecked(d.get("bold", False))
            self.title_edit.setText(d.get("title", ""))
            self.title_size.setValue(d.get("title_size", 54))
            self.res_combo.setCurrentIndex(d.get("res", 0))
            self.fps_combo.setCurrentIndex(d.get("fps", 1))
            self.quality_combo.setCurrentIndex(d.get("quality", 1))
            self.zoom_chk.setChecked(d.get("zoom", True))
            self.blur_chk.setChecked(d.get("blur", True))
            self.music_edit.setText(d.get("music", ""))
            self.music_slider.setValue(d.get("music_vol", 12))
            self.out_edit.setText(d.get("out", str(user_dir() / "output")))
            self.mp3_chk.setChecked(d.get("mp3", False))
            self.refresh_combos()
        except Exception:
            pass

    def closeEvent(self, e):
        if self.worker is not None and self.worker.isRunning():
            r = QMessageBox.question(self, "Exit", "A job is still running. Cancel it and exit?")
            if r != QMessageBox.Yes:
                e.ignore()
                return
            self.worker.cancel()
            self.worker.wait(5000)
        self.save_state()
        e.accept()


def qt_filter(mode, ctx, msg):
    if "QFont::setPointSize" in msg:
        return
    sys.stderr.write(msg + "\n")


def main():
    if os.name == "nt":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("YashvirGaming.ShortsCreator.1.0.1")
        except Exception:
            pass
    qInstallMessageHandler(qt_filter)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    ic = res_dir() / "icon.ico"
    if ic.is_file():
        app.setWindowIcon(QIcon(str(ic)))
    app.setStyleSheet(STYLE)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()