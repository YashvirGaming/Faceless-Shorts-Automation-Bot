import asyncio
import subprocess
import sys
import shutil
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("Run: pip install edge-tts")

TITLE = "youtube.com/@YashvirGaming"
VOICE = "en-US-AndrewNeural"
RATE = "+10%"
W, H, FPS = 1080, 1920, 30

WORDS_PER_LINE = 2
FONT_FILE = ""
FONT_SIZE = 78
CAPTION_MARGIN_V = 560
GLOW = False
GLOW_COLOR = "&H00FFFF00"
POP = "{\\fscx70\\fscy70\\t(0,100,\\fscx112\\fscy112)\\t(100,180,\\fscx100\\fscy100)}"
GLOW_TAG = "{\\blur14\\alpha&H50&}"

BASE = Path(__file__).resolve().parent
IMG_DIR = BASE / "images"
OUT_DIR = BASE / "output"
TMP_DIR = OUT_DIR / "tmp"
FONTS_DIR = BASE / "fonts"

SCRIPT = (
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


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def probe_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)]
    )
    return float(out.decode().strip())


def fmt(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


async def synth(text, audio_path):
    try:
        comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    except TypeError:
        comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    words = []
    with open(audio_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "start": chunk["offset"] / 1e7,
                    "end": (chunk["offset"] + chunk["duration"]) / 1e7,
                    "text": chunk["text"],
                })
    return words


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


def detect_font():
    if not FONTS_DIR.exists():
        return "Arial"
    files = sorted(p for p in FONTS_DIR.iterdir() if p.suffix.lower() in {".ttf", ".otf"})
    if FONT_FILE:
        files = [p for p in files if p.name.lower() == FONT_FILE.lower()] or files
    if not files:
        return "Arial"
    try:
        from PIL import ImageFont
        return ImageFont.truetype(str(files[0]), 20).getname()[0]
    except Exception:
        return files[0].stem


def build_ass(words, total, path):
    font = detect_font()
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {W}\n"
        f"PlayResY: {H}\n"
        "WrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Cap,{font},{FONT_SIZE},&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,80,80,{CAPTION_MARGIN_V},1\n"
        f"Style: Glow,{font},{FONT_SIZE},{GLOW_COLOR},{GLOW_COLOR},{GLOW_COLOR},&H00000000,-1,0,0,0,100,100,0,0,1,12,0,2,80,80,{CAPTION_MARGIN_V},1\n"
        f"Style: Title,{font},54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,8,60,60,200,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    lines = [f"Dialogue: 3,{fmt(0)},{fmt(total)},Title,,0,0,0,,{TITLE}"] if TITLE else []
    groups = [words[i:i + WORDS_PER_LINE] for i in range(0, len(words), WORDS_PER_LINE)]
    for gi, group in enumerate(groups):
        start = group[0]["start"]
        last_end = group[-1]["end"]
        nxt = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else total
        end = min(nxt, last_end + 0.5)
        plain, karaoke = [], []
        for wi, w in enumerate(group):
            nstart = group[wi + 1]["start"] if wi + 1 < len(group) else end
            dur = max(1, round((nstart - w["start"]) * 100))
            clean = w["text"].replace("{", "").replace("}", "").replace("\\", "").upper()
            plain.append(clean)
            karaoke.append("{\\k" + str(dur) + "}" + clean)
        if GLOW:
            lines.append(f"Dialogue: 1,{fmt(start)},{fmt(end)},Glow,,0,0,0,,{POP}{GLOW_TAG}{' '.join(plain)}")
        lines.append(f"Dialogue: 2,{fmt(start)},{fmt(end)},Cap,,0,0,0,,{POP}{' '.join(karaoke)}")
    Path(path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def make_segments(images, total):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    for old in TMP_DIR.glob("seg*.mp4"):
        old.unlink()
    per = total / len(images)
    frames = max(1, round(per * FPS))
    segs = []
    for i, img in enumerate(images):
        z = f"1+0.15*on/{frames}" if i % 2 == 0 else f"1.15-0.15*on/{frames}"
        graph = (
            "[0:v]split[a][b];"
            "[a]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,boxblur=30:5[bg];"
            "[b]scale=1620:2880:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
            "format=yuv420p[v]"
        )
        out = TMP_DIR / f"seg{i:03d}.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(img),
             "-filter_complex", graph, "-map", "[v]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])
        segs.append(out)
    return segs


def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("ffmpeg not found. Install from https://ffmpeg.org and add it to PATH.")
    IMG_DIR.mkdir(exist_ok=True)
    FONTS_DIR.mkdir(exist_ok=True)
    images = sorted(
        p for p in IMG_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    if not images:
        sys.exit(f"Put your Diego Garcia pictures in: {IMG_DIR}")

    audio = OUT_DIR / "voice.mp3"
    words = asyncio.run(synth(SCRIPT, audio))
    audio_dur = probe_duration(audio)
    if not words:
        words = estimate_words(SCRIPT, audio_dur)
    total = audio_dur + 0.6

    (OUT_DIR / "fonts").mkdir(exist_ok=True)
    shutil.copytree(FONTS_DIR, OUT_DIR / "fonts", dirs_exist_ok=True)
    build_ass(words, total, OUT_DIR / "captions.ass")
    segs = make_segments(images, total)

    (OUT_DIR / "list.txt").write_text(
        "\n".join(f"file 'tmp/{s.name}'" for s in segs) + "\n", encoding="utf-8"
    )
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", "list.txt",
         "-i", "voice.mp3",
         "-map", "0:v", "-map", "1:a",
         "-vf", "ass=captions.ass:fontsdir=fonts",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.2f}", "short.mp4"], cwd=OUT_DIR)

    print(f"Done: {OUT_DIR / 'short.mp4'} ({total:.1f}s, {len(images)} images)")


if __name__ == "__main__":
    main()