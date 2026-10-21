# 🎬 SHORTS CREATOR APP (v1.0.1)

An automated desktop pipeline built in Python using **PySide6** to generate highly optimized, viral-style horizontal or vertical content (YouTube Shorts, Instagram Reels, TikToks) programmatically in under 60 seconds.

<img src="https://github.com/user-attachments/assets/0a80cb7b-aeb2-4c0e-8468-a772d0e96dff" width="2041" height="1389" alt="Shorts Creator App Dashboard" />

---

## ✨ Features
- **Zero-Cost Neural Text-to-Speech:** Seamless offline stream configuration leveraging `edge-tts` for dynamic narration.
- **Smart Timeline Synchronization:** Programmatic cue-matching algorithms that automatically align user script strings with corresponding graphics folders.
- **Advanced Dynamic Subtitles:** Complete support for local `.ass` style subtitles featuring custom neon glows, karaoke text markers, and pop-in animations.
- **Background Multi-Thread Performance:** Full UI isolation utilizing standalone `QThread` workers so rendering operations do not hang or freeze your window viewport.
- **FFmpeg Integration Pipeline:** Subprocess stitching mechanics built to manage video resizing, frame padding, background music levels, audio resampling, and quick h264 encoding.

---

## 📁 Repository Directory Architecture
To run the app directly via script source blocks or build standalone bundles, format your working tree matching this architecture:

```text
ShortsCreator/
├── bin/
│   └── ffmpeg.exe         <-- Drop downloaded file here
├── fonts/
│   └── BebasNeue-Regular.ttf
├── images/
│   └── [User Image Assets]
├── output/
│   └── [Rendered MP4s]
├── icon.ico
├── NuitkaBuilder.bat
├── requirements.txt
├── short_maker_CLI.py
└── short_maker_GUI.py
```

> [!IMPORTANT]  
> 📥 **[👉 Click Here to Download ffmpeg.exe](https://gyan.dev)**  
> *Extract `ffmpeg.exe` from the downloaded zip's `bin/` folder and drop it directly into the project's `bin/` directory before launching the app.*

```

---

## 🔒 Security & Verification Notice
This project is **100% open-source**. Every piece of core media parsing, sound mixing, and rendering is explicitly visible within `short_maker_GUI.py`. 

- **No Malicious Trackers / Network Requests:** The application only initiates standard network requests to secure official Microsoft endpoint CDNs via `edge-tts` to convert user text inputs into neural audio files.
- **Local Compilations Only:** Your scripts, background music, images, and logs remain completely local on your desktop storage drive at all times.

---

## 🚀 Getting Started & Installation

### 1. Clone the Space
```bash
git clone https://github.com/YashvirGaming/Faceless-Shorts-Automation-Bot.git
cd ShortsCreator
```

### 2. Install Python Libraries
Ensure you have Python 3.10+ deployed. Run the command block below to register all dependencies:
```bash
pip install -r requirements.txt
```

### 3. Setup Dependencies (FFmpeg & Typography)
To comply with host boundaries regarding repository constraints, **binaries over 100MB are not included inside the master code branches.**
1. **FFmpeg Setup:** Download the official package build of FFmpeg for Windows. Place the unpacked `ffmpeg.exe` file inside your local `bin/` subfolder.
2. **Typography Setup:** Make sure your chosen target workspace typeface file (e.g., `BebasNeue-Regular.ttf`) is stored securely inside the `fonts/` directory folder.

### 4. Boot Up the Workspace
Launch the dashboard setup directly through your console terminal terminal space:
```bash
python short_maker_GUI.py
python short_maker_CLI.py
```

---

## 🛠️ Deploying Single-Executable Applications (.EXE)
If you want to bundle this clean automation architecture into a fast executable file distribution patch that completely ignores standard command window launch hooks, leverage the pre-configured Nuitka building properties:

## 📦 Compiling to Standalone .exe (Windows)

The repository includes a custom automated batch workflow file called `NuitkaBuilder.bat` to freeze all assets, virtual environments, binaries, and icons into a single optimized standalone executable file.

### Using NuitkaBuilder.bat
Instead of running loose CLI parameters, open a standard terminal inside your workspace directory or double-click `NuitkaBuilder.bat` to run the following compiler configuration sequence:

```batch
python -m nuitka ^
 --mode=onefile ^
 --jobs=8 ^
 --enable-plugin=pyside6 ^
 --include-qt-plugins=sensible,imageformats,platforms,styles,iconengines ^
 --include-package=edge_tts ^
 --include-package=aiohttp ^
 --include-package=certifi ^
 --include-package-data=certifi ^
 --include-data-files=bin\ffmpeg.exe=bin/ffmpeg.exe ^
 --include-data-files=fonts\BebasNeue-Regular.ttf=fonts/BebasNeue-Regular.ttf ^
 --windows-console-mode=disable ^
 --company-name=YashvirGaming ^
 --product-name="Shorts Creator App" ^
 --output-filename=ShortsCreatorApp.exe ^
 --remove-output ^
 short_maker_GUI.py
```

> [!NOTE]
> * **Automatic Validation:** The batch file automatically verifies that `bin/ffmpeg.exe` and your baseline text fonts are exactly where they need to be before kicking off compilation tasks so you don't run into dead paths later!

---

## 📜 Credits & Attributions
- Designed & Developed by [YashvirGaming](https://github.com/YashvirGaming)
- Core Operations Layer Engine: PySide6, edge-tts, and FFmpeg codecs.
