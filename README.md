# PicPulse - Smart Image Analyzer & Renamer

Application desktop d'analyse d'images par IA, détection de lens flare, et renommage intelligent.

## Features

- **AI Recognition** - MobileNetV2 identifie l'objet principal de chaque image
- **Lens Flare Detection** - Détection automatique des reflets lumineux via OpenCV
- **Intelligent Renaming** - Renommage automatique : `[mot_cle]_[compteur].ext`
- **Flare Tagging** - Ajoute un préfixe `flare_` aux images concernées
- **Preview Mode** - Simule le renommage sans modifier les fichiers
- **Real-time UI** - Interface moderne avec progression en direct

## Architecture

```
PicPulse/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── core/
│   ├── __init__.py
│   ├── analyzer.py         # MobileNetV2 image recognition
│   ├── flare_detector.py   # OpenCV lens flare detection
│   ├── renamer.py          # Renaming logic + conflict management
│   └── processor.py        # Pipeline orchestrator
├── ui/
│   ├── __init__.py
│   └── app.py             # customtkinter interface
└── models/                 # Pretrained model weights cache
```

## Installation

```bash
# 1. Clone or download PicPulse
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

**Note:** PyTorch and torchvision will download MobileNetV2 weights on first run (~14MB).
OpenCV is used only for flare detection (not for AI recognition).

## How It Works

### 1. Image Recognition (MobileNetV2)
Each image is resized to 224x224 and passed through MobileNetV2 (ImageNet).
The top prediction is used as the renaming keyword.

### 2. Lens Flare Detection
OpenCV analyses each image for:
- Overexposed bright regions (value > 240)
- Connected bright spot clusters
- Purple/magenta color casts (characteristic of flares)

Images scoring above the threshold get a `flare_` prefix.

### 3. Intelligent Renaming
Format: `[keyword]_[counter].ext`
- Counters are unique per keyword (e.g., cat_001.jpg, cat_002.jpg)
- Recursive directory traversal
- Original extensions preserved
- Optional preview mode (dry run)

## Dependencies

- Python 3.8+
- PyTorch
- torchvision
- OpenCV
- Pillow
- customtkinter
- NumPy

## Usage

1. Launch the app: `python main.py`
2. Click **Browse** to select your image folder
3. Configure options (flare threshold, tagging, preview mode)
4. Click **Start Processing**
5. Watch real-time previews and logs
6. Results appear in the same folder with new names

## License

MIT
