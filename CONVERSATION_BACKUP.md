# PicPulse - Session Backup

## Date
June 30, 2026

## Overview
Built PicPulse: Smart Image Analyzer & Renamer - a desktop application for AI-powered image recognition, lens flare detection, and intelligent file renaming.

## Key Decisions
- **Platform**: Desktop app (customtkinter) rather than web app
- **AI Model**: MobileNetV2 (lightweight, 14MB) via PyTorch/torchvision
- **Flare Detection**: OpenCV with HSV analysis, connected components, purple tint detection
- **Renaming Format**: `[keyword]_[counter].ext` with optional `flare_` prefix

## Project Structure
```
PicPulse/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── analyzer.py         # MobileNetV2 recognition
│   ├── flare_detector.py   # OpenCV lens flare detection
│   ├── renamer.py          # Renaming + conflict management
│   └── processor.py        # Pipeline orchestrator
└── ui/
    ├── __init__.py
    └── app.py              # customtkinter UI
```

## Features Delivered
1. AI Recognition (MobileNetV2, ImageNet 1000 classes)
2. Lens Flare Detection (bright regions, purple tint, score-based)
3. Intelligent Renaming (keyword_counter.ext, recursive, no conflicts)
4. Modern UI (real-time preview, progress bar, log, pause/cancel)
5. Preview Mode (dry run without modifying files)

## Links
- **GitHub Repo**: https://github.com/ucfzem/PicPulse
- **Landing Page**: https://github.com/ucfzem/picpulse-landing
- **Vercel App**: https://picpulse.vercel.app (pending deployment)

## Dependencies
- PyTorch >= 2.0.0
- torchvision >= 0.15.0
- opencv-python >= 4.8.0
- Pillow >= 10.0.0
- customtkinter >= 5.2.0
- numpy >= 1.24.0
