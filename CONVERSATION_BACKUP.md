# PicPulse - Session Backup

## Date
June 30, 2026

## Overview
PicPulse: Smart Image Analyzer & Renamer - AI-powered image recognition, lens flare detection, and intelligent file renaming. Available as a desktop app (Python), Android app (Kotlin), and web landing page.

---

## Component 1: Desktop App (Python)

### Platform
Desktop app (customtkinter) using PyTorch/torchvision

### Key Decisions
- **AI Model**: MobileNetV2 (lightweight, 14MB) via PyTorch/torchvision
- **Flare Detection**: OpenCV with HSV analysis, connected components, purple tint detection
- **Renaming Format**: `[keyword]_[counter].ext` with optional `flare_` prefix

### Project Structure
```
PicPulse/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── core/
│   ├── analyzer.py         # MobileNetV2 recognition
│   ├── flare_detector.py   # OpenCV lens flare detection
│   ├── renamer.py          # Renaming + conflict management
│   └── processor.py        # Pipeline orchestrator
└── ui/
    └── app.py              # customtkinter UI
```

### Features
1. AI Recognition (MobileNetV2, ImageNet 1000 classes)
2. Lens Flare Detection (bright regions, purple tint, score-based)
3. Intelligent Renaming (keyword_counter.ext, recursive, no conflicts)
4. Modern UI (real-time preview, progress bar, log, pause/cancel)
5. Preview Mode (dry run without modifying files)

---

## Component 2: Android App (Kotlin)

### Tech Stack
- Kotlin, Jetpack Compose, Material3
- TensorFlow Lite (MobileNetV2) for on-device AI classification
- ML Kit Text Recognition for OCR
- OpenCV (QuickBird) for lens flare detection
- Storage Access Framework for folder selection

### Architecture
- MVVM with AndroidViewModel + StateFlow
- Repository pattern (ImageRepository)
- Interface-based OCR abstraction (OcrEngine, MlKitOcrEngine, NoopOcrEngine)
- Sealed class state management (ProcessingState)

### Features
1. AI Image Classification (TFLite MobileNetV2, 1001 ImageNet classes)
2. Lens Flare Detection (HSV analysis, connected components, magenta detection)
3. OCR / Text Detection (Google ML Kit)
4. Automatic Renaming (`[keyword]_[counter].ext`, optional `flare_` prefix)
5. Batch Processing (recursive folder scan via SAF)
6. AI Model Download (MobileNetV2 from Google Cloud Storage)
7. Material 3 UI with progress tracking and results summary

### Issues Fixed
1. Fixed `settings.gradle.kts` typo: `dependencyResolution` → `dependencyResolutionManagement`
2. Created `Theme.kt` with Material3 PicPulseTheme (indigo/purple color scheme)
3. Fixed `ProcessingScreen.kt`: `s.total` → `s.discovered` for Scanning state
4. Created `proguard-rules.pro` with TFLite/ML Kit keep rules
5. Created launcher icons (XML adaptive icons with vector drawables)
6. Fixed `Renamer.kt`: `private val addFlareTag` → `var` (mutable)
7. Fixed `FlareDetector.kt`: flood fill now returns pixel indices for correct meanHue calculation
8. Added Gradle wrapper (`gradlew`, `gradlew.bat`, `gradle-wrapper.jar`)
9. Added GitHub Actions CI workflow (`build-apk.yml`)

---

## Component 3: Web Landing Page

### Tech Stack
- Static HTML/CSS (single-page, inline styles)
- Minimal npm package with `serve` for local dev
- Deployed to GitHub Pages + Vercel

### Features
- Gradient logo (indigo → purple → pink)
- Feature grid (AI Recognition, Flare Detection, Smart Renaming)
- Architecture overview
- Install instructions and GitHub links
- Dark theme design

---

## Links
### Repositories
- **Main Repo (Desktop App)**: https://github.com/ucfzem/PicPulse
- **Android App**: https://github.com/ucfzem/picpulse-android
- **Landing Page**: https://github.com/ucfzem/picpulse-landing
- **Android App**: https://github.com/ucfzem/picpulse-android

### Deployed Sites
- **GitHub Pages**: https://ucfzem.github.io/PicPulse
- **Vercel**: https://picpulse-landing.vercel.app

### APK Builds
- GitHub Actions builds APK on push to `main`: https://github.com/ucfzem/picpulse-android/actions
- Download debug/release APKs from workflow artifacts

---

## Dependencies

### Desktop (Python)
- PyTorch >= 2.0.0
- torchvision >= 0.15.0
- opencv-python >= 4.8.0
- Pillow >= 10.0.0
- customtkinter >= 5.2.0
- numpy >= 1.24.0

### Android (Kotlin)
- Jetpack Compose BOM 2023.10.01, Material3
- TensorFlow Lite 2.14.0 + support 0.4.4
- OpenCV 4.9.0 (QuickBird Studios)
- ML Kit Text Recognition 16.0.0
- Coil Compose 2.5.0
- Kotlin Coroutines Android 1.7.3
